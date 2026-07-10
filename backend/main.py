"""
main.py — FastAPI application with all endpoints

Endpoints:
  EXISTING (backward-compatible):
    GET  /ping
    GET  /
    GET  /topics
    GET  /formats
    POST /generate
    POST /download

  NEW:
    GET  /domains                    → list all domains
    GET  /domains/{domain}/tables    → tables in a domain
    GET  /relational-sets            → list predefined relational sets

    POST /generate/schema            → schema-driven multi-table generation
    POST /generate/relational-set    → predefined relational set generation
    POST /generate/domain            → domain-based generation

    POST /download/multi             → download multi-table as ZIP / single file
    POST /download/schema            → schema-driven + download
    POST /download/relational-set    → relational set + download
    POST /download/domain            → domain + download

    POST /db/test                    → test DB connection
    POST /db/seed/schema             → seed DB from user schema
    POST /db/seed/relational-set     → seed DB from predefined relational set
    POST /db/seed/domain             → seed DB from domain
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from backend.models.schemas import (
    DataRequest,
    DataResponse,
    DBSeedRequest,
    DBSeedResponse,
    DBTestRequest,
    DBTestResponse,
    DomainInfo,
    DomainRequest,
    FieldTypeEnum,
    MultiTableResponse,
    PredefinedRelationalSet,
    RelationalSetRequest,
    SchemaGenerateRequest,
    TableData,
    TopicInfo,
    UserDefinedTable,
)
from backend.services.data_generator import DataGenerator
from backend.services.db_seeder import DBSeederService
from backend.services.format_converter import FormatConverter, MultiTableFormatConverter
from backend.utils.constants import (
    DOMAIN_REGISTRY,
    FIELD_TYPE_LABELS,
    PREDEFINED_TOPICS,
    RELATIONAL_SETS,
    SUPPORTED_FORMATS,
    TABLE_DEFINITIONS,
)
from backend.utils.validator import validate_schema_request


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title       = "Mock Data Generator API",
    description = "Generate realistic structured mock data for dev, QA, and testing.",
    version     = "2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ---------------------------------------------------------------------------
# Utility — build MultiTableResponse from tables_data dict
# ---------------------------------------------------------------------------

def _build_multi_response(
    tables_data: Dict[str, List[Dict[str, Any]]],
    format_type: str,
    label: str,
    relations: Optional[List[Dict]] = None,
) -> MultiTableResponse:
    table_results: List[TableData] = []

    for table_name, records in tables_data.items():
        content, filename, _ = FormatConverter.convert_to_format(
            data        = records,
            format_type = format_type,
            topic       = table_name,
        )
        table_results.append(TableData(
            table_name  = table_name,
            num_records = len(records),
            data        = content,
            filename    = filename,
        ))

    return MultiTableResponse(
        success   = True,
        tables    = table_results,
        relations = relations,
        format    = format_type,
    )


def _build_download_response(
    tables_data: Dict[str, List[Dict[str, Any]]],
    format_type: str,
    label: str,
) -> Response:
    """Convert multi-table data and return as downloadable Response."""
    content, filename, content_type = MultiTableFormatConverter.convert(
        tables_data = tables_data,
        format_type = format_type,
        label       = label,
    )

    # ZIP and Parquet are base64-encoded — decode before sending
    if content_type in ("application/zip", "application/octet-stream"):
        binary = base64.b64decode(content)
        return Response(
            content = binary,
            media_type = content_type,
            headers = {"Content-Disposition": f"attachment; filename={filename}"},
        )

    return Response(
        content    = content,
        media_type = content_type,
        headers    = {"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# EXISTING endpoints (backward-compatible)
# ---------------------------------------------------------------------------

@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/")
async def root():
    return {
        "message": "Mock Data Generator API v2.0 is running!",
        "docs"   : "/docs",
    }


@app.get("/topics", response_model=List[TopicInfo])
async def get_topics():
    """All available predefined topics (backward-compatible)."""
    return [
        TopicInfo(
            name        = name,
            description = info["description"],
            fields      = info["fields"],
        )
        for name, info in PREDEFINED_TOPICS.items()
    ]


@app.get("/formats")
async def get_formats():
    """All supported output formats."""
    return {"formats": SUPPORTED_FORMATS}


@app.post("/generate", response_model=DataResponse)
async def generate_data(request: DataRequest):
    """Generate mock data for a single topic (backward-compatible)."""
    try:
        generator = DataGenerator(seed=request.seed)
        data      = generator.generate_for_topic(
            topic         = request.topic,
            num_records   = request.num_records,
            custom_fields = request.custom_fields,
        )
        content, filename, content_type = FormatConverter.convert_to_format(
            data        = data,
            format_type = request.format.value,
            topic       = request.topic,
        )
        return DataResponse(
            success      = True,
            data         = content,
            filename     = filename,
            content_type = content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download")
async def download_data(request: DataRequest):
    """Generate and return single-topic data as downloadable file."""
    try:
        generator = DataGenerator(seed=request.seed)
        data      = generator.generate_for_topic(
            topic         = request.topic,
            num_records   = request.num_records,
            custom_fields = request.custom_fields,
        )
        content, filename, content_type = FormatConverter.convert_to_format(
            data        = data,
            format_type = request.format.value,
            topic       = request.topic,
        )

        if content_type == "application/octet-stream":
            return Response(
                content    = base64.b64decode(content),
                media_type = content_type,
                headers    = {"Content-Disposition": f"attachment; filename={filename}"},
            )

        return Response(
            content    = content,
            media_type = content_type,
            headers    = {"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# NEW — Discovery endpoints
# ---------------------------------------------------------------------------

@app.get("/domains", response_model=List[DomainInfo])
async def get_domains():
    """List all available domains with their tables."""
    return [
        DomainInfo(
            name        = domain,
            description = info["description"],
            tables      = info["tables"],
            relational  = bool(info["relational_sets"]),
        )
        for domain, info in DOMAIN_REGISTRY.items()
    ]


@app.get("/domains/{domain}/tables")
async def get_domain_tables(domain: str):
    """Get table definitions for a specific domain."""
    if domain not in DOMAIN_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found.")

    domain_info = DOMAIN_REGISTRY[domain]
    tables = []
    for table_name in domain_info["tables"]:
        if table_name in TABLE_DEFINITIONS:
            tdef = TABLE_DEFINITIONS[table_name]
            tables.append({
                "name"        : table_name,
                "description" : tdef["description"],
                "fields"      : [
                    {
                        "name"       : f[0],
                        "type"       : f[1],
                        "label"      : FIELD_TYPE_LABELS.get(f[1], f[1]),
                        "constraints": f[2] if len(f) > 2 else None,
                    }
                    for f in tdef["fields"]
                ],
            })

    return {
        "domain"         : domain,
        "description"    : domain_info["description"],
        "relational_sets": domain_info["relational_sets"],
        "tables"         : tables,
    }


@app.get("/relational-sets")
async def get_relational_sets():
    """List all predefined relational sets."""
    return [
        {
            "name"       : set_name,
            "description": set_info["description"],
            "tables"     : set_info["tables"],
            "relations"  : set_info["relations"],
        }
        for set_name, set_info in RELATIONAL_SETS.items()
    ]


@app.get("/field-types")
async def get_field_types():
    """List all allowed field types for schema-driven generation."""
    return [
        {"type": k, "label": v}
        for k, v in FIELD_TYPE_LABELS.items()
    ]


# ---------------------------------------------------------------------------
# NEW — Generate endpoints (return JSON response with data)
# ---------------------------------------------------------------------------

@app.post("/generate/schema", response_model=MultiTableResponse)
async def generate_from_schema(request: SchemaGenerateRequest):
    """
    Schema-driven generation.
    User supplies table definitions + optional relations.
    """
    # Validate
    validation = validate_schema_request(request.tables, request.relations)
    if not validation.ok:
        raise HTTPException(
            status_code = 422,
            detail      = {"errors": validation.errors, "warnings": validation.warnings},
        )

    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_from_schema(
            tables    = request.tables,
            relations = request.relations,
        )

        relations_echo = None
        if request.relations:
            relations_echo = [r.model_dump() for r in request.relations]

        return _build_multi_response(
            tables_data = tables_data,
            format_type = request.format.value,
            label       = "schema_export",
            relations   = relations_echo,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/relational-set", response_model=MultiTableResponse)
async def generate_relational_set(request: RelationalSetRequest):
    """Generate data from a predefined relational set (e.g. ecommerce_full)."""
    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_relational_set(
            set_name    = request.predefined_set.value,
            num_records = request.num_records,
        )

        set_info       = RELATIONAL_SETS[request.predefined_set.value]
        relations_echo = set_info.get("relations")

        return _build_multi_response(
            tables_data = tables_data,
            format_type = request.format.value,
            label       = request.predefined_set.value,
            relations   = relations_echo,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/domain", response_model=MultiTableResponse)
async def generate_domain(request: DomainRequest):
    """Generate all tables for a domain (relational or independent)."""
    if request.domain.value not in DOMAIN_REGISTRY:
        raise HTTPException(
            status_code = 404,
            detail      = f"Domain '{request.domain.value}' not found."
        )

    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_for_domain(
            domain      = request.domain.value,
            relational  = request.relational,
            num_records = request.num_records,
        )

        return _build_multi_response(
            tables_data = tables_data,
            format_type = request.format.value,
            label       = request.domain.value,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# NEW — Download endpoints (return binary / file response)
# ---------------------------------------------------------------------------

@app.post("/download/schema")
async def download_schema(request: SchemaGenerateRequest):
    """Schema-driven generation + direct file download."""
    validation = validate_schema_request(request.tables, request.relations)
    if not validation.ok:
        raise HTTPException(
            status_code = 422,
            detail      = {"errors": validation.errors, "warnings": validation.warnings},
        )

    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_from_schema(
            tables    = request.tables,
            relations = request.relations,
        )
        return _build_download_response(tables_data, request.format.value, "schema_export")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download/relational-set")
async def download_relational_set(request: RelationalSetRequest):
    """Predefined relational set generation + direct file download."""
    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_relational_set(
            set_name    = request.predefined_set.value,
            num_records = request.num_records,
        )
        return _build_download_response(
            tables_data, request.format.value, request.predefined_set.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download/domain")
async def download_domain(request: DomainRequest):
    """Domain generation + direct file download."""
    if request.domain.value not in DOMAIN_REGISTRY:
        raise HTTPException(
            status_code = 404,
            detail      = f"Domain '{request.domain.value}' not found."
        )

    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_for_domain(
            domain      = request.domain.value,
            relational  = request.relational,
            num_records = request.num_records,
        )
        return _build_download_response(tables_data, request.format.value, request.domain.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# NEW — Database seeding endpoints
# ---------------------------------------------------------------------------

@app.post("/db/test", response_model=DBTestResponse)
async def test_db_connection(request: DBTestRequest):
    """
    Test database connectivity without making any data changes.
    Use this before seeding to verify credentials and reachability.
    """
    result = DBSeederService.test_connection(request.connection)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result


@app.post("/db/seed/schema", response_model=DBSeedResponse)
async def seed_from_schema(request: DBSeedRequest):
    """
    Generate data from user-defined schema and seed directly into target DB.

    ⚠️  Only use with dev / UAT databases.
        Credentials are used only during this request and never stored.
    """
    # Validate schema first
    validation = validate_schema_request(request.tables, request.relations)
    if not validation.ok:
        raise HTTPException(
            status_code = 422,
            detail      = {"errors": validation.errors, "warnings": validation.warnings},
        )

    try:
        generator   = DataGenerator(seed=request.seed)
        tables_data = generator.generate_from_schema(
            tables    = request.tables,
            relations = request.relations,
        )
        result = DBSeederService.seed(request, tables_data)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/db/seed/relational-set", response_model=DBSeedResponse)
async def seed_relational_set(
    predefined_set : str,
    num_records    : int,
    truncate_first : bool,
    batch_size     : int,
    request        : DBTestRequest,   # only connection config needed here
):
    """
    Generate from a predefined relational set and seed into target DB.
    Pass the set name as a query param: ?predefined_set=ecommerce_full
    """
    if predefined_set not in RELATIONAL_SETS:
        raise HTTPException(
            status_code = 404,
            detail      = f"Relational set '{predefined_set}' not found."
        )

    try:
        generator   = DataGenerator()
        tables_data = generator.generate_relational_set(
            set_name    = predefined_set,
            num_records = num_records,
        )

        # Build a DBSeedRequest using the relational set's table definitions
        set_info      = RELATIONAL_SETS[predefined_set]
        table_schemas = _build_user_tables_from_definitions(set_info["tables"])

        seed_request = DBSeedRequest(
            connection     = request.connection,
            tables         = table_schemas,
            truncate_first = truncate_first,
            batch_size     = batch_size,
        )

        result = DBSeederService.seed(seed_request, tables_data)
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/db/seed/domain", response_model=DBSeedResponse)
async def seed_domain(
    domain         : str,
    num_records    : int,
    relational     : bool,
    truncate_first : bool,
    batch_size     : int,
    request        : DBTestRequest,
):
    """
    Generate domain data and seed into target DB.
    Pass domain as query param: ?domain=ecommerce
    """
    if domain not in DOMAIN_REGISTRY:
        raise HTTPException(
            status_code = 404,
            detail      = f"Domain '{domain}' not found."
        )

    try:
        generator   = DataGenerator()
        tables_data = generator.generate_for_domain(
            domain      = domain,
            relational  = relational,
            num_records = num_records,
        )

        domain_tables = DOMAIN_REGISTRY[domain]["tables"]
        table_schemas = _build_user_tables_from_definitions(domain_tables)

        seed_request = DBSeedRequest(
            connection     = request.connection,
            tables         = table_schemas,
            truncate_first = truncate_first,
            batch_size     = batch_size,
        )

        result = DBSeederService.seed(seed_request, tables_data)
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Helper — convert TABLE_DEFINITIONS entries → UserDefinedTable list
# ---------------------------------------------------------------------------

def _build_user_tables_from_definitions(table_names: List[str]) -> List[UserDefinedTable]:
    """
    Converts TABLE_DEFINITIONS entries into UserDefinedTable Pydantic models
    so DBSeederService can use them for schema creation.
    """
    from backend.models.schemas import FieldConstraints, SchemaField

    result: List[UserDefinedTable] = []

    for table_name in table_names:
        if table_name not in TABLE_DEFINITIONS:
            continue

        tdef   = TABLE_DEFINITIONS[table_name]
        fields: List[SchemaField] = []

        for field_tuple in tdef["fields"]:
            fname       = field_tuple[0]
            ftype_str   = field_tuple[1]
            fconstraints= field_tuple[2] if len(field_tuple) > 2 else None

            try:
                ftype = FieldTypeEnum(ftype_str)
            except ValueError:
                continue

            constraints_obj = None
            refs_table      = None
            refs_field      = None

            if fconstraints:
                refs_table = fconstraints.pop("references_table", None)
                refs_field = fconstraints.pop("references_field", None)
                if fconstraints:
                    constraints_obj = FieldConstraints(**fconstraints)
                # Restore for future calls
                if refs_table:
                    fconstraints["references_table"] = refs_table
                if refs_field:
                    fconstraints["references_field"] = refs_field

            fields.append(SchemaField(
                name             = fname,
                type             = ftype,
                constraints      = constraints_obj,
                references_table = refs_table,
                references_field = refs_field,
            ))

        if fields:
            result.append(UserDefinedTable(
                name        = table_name,
                fields      = fields,
                num_records = 100,
            ))

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)