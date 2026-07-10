"""
schemas.py — Pydantic models for Mock Data Generator API

Covers:
  1. Basic / existing generation
  2. Schema-driven generation (user-defined fields with type whitelist)
  3. Relational data generation (predefined sets + user-defined relations)
  4. Database seeding
  5. Domain-specific generation
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FormatEnum(str, Enum):
    JSON    = "JSON"
    CSV     = "CSV"
    TSV     = "TSV"
    YAML    = "YAML"
    XML     = "XML"
    PARQUET = "Parquet"


class FieldTypeEnum(str, Enum):
    """
    Whitelist of allowed field types for schema-driven generation.
    Explicit / free-text content types are intentionally excluded.
    """
    # Identity / personal (safe subset)
    FIRST_NAME      = "first_name"
    LAST_NAME       = "last_name"
    FULL_NAME       = "full_name"
    EMAIL           = "email"
    PHONE           = "phone"
    DATE_OF_BIRTH   = "date_of_birth"
    GENDER          = "gender"
    ADDRESS         = "address"
    CITY            = "city"
    STATE           = "state"
    COUNTRY         = "country"
    ZIP_CODE        = "zip_code"

    # Numbers
    INTEGER         = "integer"
    FLOAT           = "float"
    BOOLEAN         = "boolean"

    # Text (bounded / structured — NOT free-form prose)
    UUID            = "uuid"
    SLUG            = "slug"
    USERNAME        = "username"
    PASSWORD_HASH   = "password_hash"   # bcrypt-style hash, never plaintext
    URL             = "url"
    IP_ADDRESS      = "ip_address"
    MAC_ADDRESS     = "mac_address"
    COLOR_HEX       = "color_hex"

    # Temporal
    DATE            = "date"
    DATETIME        = "datetime"
    TIME            = "time"
    TIMESTAMP       = "timestamp"

    # Finance
    CURRENCY_CODE   = "currency_code"
    AMOUNT          = "amount"
    IBAN            = "iban"
    CREDIT_CARD     = "credit_card"     # masked: **** **** **** 1234

    # Commerce
    PRODUCT_NAME    = "product_name"
    CATEGORY        = "category"
    SKU             = "sku"
    PRICE           = "price"
    RATING          = "rating"

    # Company / HR
    COMPANY_NAME    = "company_name"
    JOB_TITLE       = "job_title"
    DEPARTMENT      = "department"
    EMPLOYEE_ID     = "employee_id"
    SALARY          = "salary"

    # System / Dev
    STATUS          = "status"          # random from: active/inactive/pending/suspended
    ENUM_PICK       = "enum_pick"       # pick from user-supplied choices list
    FOREIGN_KEY     = "foreign_key"     # references another table's PK
    PRIMARY_KEY     = "primary_key"     # auto-incremented or UUID PK


class RelationTypeEnum(str, Enum):
    """How the foreign key relationship is expressed."""
    ONE_TO_MANY  = "one_to_many"   # one parent → many children
    MANY_TO_ONE  = "many_to_one"   # alias, same wiring
    ONE_TO_ONE   = "one_to_one"    # strict 1:1


class DBDialectEnum(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL      = "mysql"
    SQLITE     = "sqlite"
    MSSQL      = "mssql"


class DomainEnum(str, Enum):
    """
    High-level domains.  Each domain maps to a group of related tables
    defined in constants.py  (replaces the old flat PREDEFINED_TOPICS dict).
    """
    ECOMMERCE    = "ecommerce"
    HEALTHCARE   = "healthcare"
    EDUCATION    = "education"
    BANKING      = "banking"
    LOGISTICS    = "logistics"
    HR           = "hr"
    REAL_ESTATE  = "real_estate"
    IOT          = "iot"
    SOCIAL_MEDIA = "social_media"
    AVIATION     = "aviation"
    WEATHER      = "weather"
    CUSTOM       = "custom"          # user-defined schema path


# ---------------------------------------------------------------------------
# Schema-driven field definition
# ---------------------------------------------------------------------------

class FieldConstraints(BaseModel):
    """Optional constraints per field — only relevant ones are used per type."""
    min_value:   Optional[float]       = None   # for integer / float / amount
    max_value:   Optional[float]       = None
    min_length:  Optional[int]         = None   # for slug / username
    max_length:  Optional[int]         = None
    decimal_places: Optional[int]      = Field(default=2, ge=0, le=6)
    choices:     Optional[List[str]]   = None   # required when type = enum_pick
    nullable:    bool                  = False  # whether field can be None (~10% of the time)
    unique:      bool                  = False  # best-effort uniqueness (no DB constraint)


class SchemaField(BaseModel):
    """One column / field in a user-defined schema."""
    name:        str           = Field(..., min_length=1, max_length=64,
                                       pattern=r"^[a-zA-Z_][a-zA-Z0-9_ ]*$")
    type:        FieldTypeEnum
    constraints: Optional[FieldConstraints] = None

    # Only used when type == FOREIGN_KEY
    references_table: Optional[str] = None   # table name in the same request
    references_field: Optional[str] = None   # field name in that table (usually PK)

    @model_validator(mode="after")
    def validate_foreign_key(self) -> SchemaField:
        if self.type == FieldTypeEnum.FOREIGN_KEY:
            if not self.references_table or not self.references_field:
                raise ValueError(
                    "references_table and references_field are required for foreign_key type"
                )
        if self.type == FieldTypeEnum.ENUM_PICK:
            if not self.constraints or not self.constraints.choices:
                raise ValueError(
                    "constraints.choices list is required for enum_pick type"
                )
        return self


class UserDefinedTable(BaseModel):
    """A single table definition supplied by the user."""
    name:        str                = Field(..., min_length=1, max_length=64,
                                            pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    fields:      List[SchemaField]  = Field(..., min_length=1, max_length=30)
    num_records: int                = Field(default=100, ge=1, le=1000)

    @field_validator("fields")
    @classmethod
    def must_have_primary_key(cls, fields: List[SchemaField]) -> List[SchemaField]:
        pk_fields = [f for f in fields if f.type == FieldTypeEnum.PRIMARY_KEY]
        if len(pk_fields) == 0:
            raise ValueError("Each table must have exactly one primary_key field")
        if len(pk_fields) > 1:
            raise ValueError("Each table must have exactly one primary_key field")
        return fields


# ---------------------------------------------------------------------------
# Relational generation
# ---------------------------------------------------------------------------

class RelationDefinition(BaseModel):
    """
    Describes a foreign-key relationship between two user-defined tables.
    Used when the user wants to wire tables manually instead of picking
    a predefined relational set.
    """
    parent_table:  str
    parent_field:  str              # usually the PK
    child_table:   str
    child_field:   str              # the FK column in child
    relation_type: RelationTypeEnum = RelationTypeEnum.ONE_TO_MANY


class PredefinedRelationalSet(str, Enum):
    """
    Ready-made relational bundles.  Expanding these is just a constants.py change.
    """
    ECOMMERCE_FULL   = "ecommerce_full"    # customers → orders → order_items → products
    HR_FULL          = "hr_full"           # departments → employees → payroll
    HEALTHCARE_FULL  = "healthcare_full"   # doctors → patients → appointments → prescriptions
    EDUCATION_FULL   = "education_full"    # courses → students → enrollments → grades
    BANKING_FULL     = "banking_full"      # accounts → transactions → loans


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

# --- 1. Basic (existing, backward-compatible) ---

class DataRequest(BaseModel):
    """Original single-topic request — kept for backward compatibility."""
    topic:         str
    format:        FormatEnum
    num_records:   int               = Field(default=100, le=1000, ge=1)
    custom_fields: Optional[List[str]] = None
    seed:          Optional[int]     = None


# --- 2. Schema-driven request ---

class SchemaGenerateRequest(BaseModel):
    """
    User supplies one or more table schemas.
    Relations can be declared inline (via SchemaField.type = foreign_key)
    or explicitly via the relations list.
    """
    tables:    List[UserDefinedTable]       = Field(..., min_length=1, max_length=10)
    relations: Optional[List[RelationDefinition]] = None
    format:    FormatEnum                   = FormatEnum.JSON
    seed:      Optional[int]               = None

    @field_validator("tables")
    @classmethod
    def unique_table_names(cls, tables: List[UserDefinedTable]) -> List[UserDefinedTable]:
        names = [t.name for t in tables]
        if len(names) != len(set(names)):
            raise ValueError("All table names must be unique within one request")
        return tables


# --- 3. Predefined relational set request ---

class RelationalSetRequest(BaseModel):
    predefined_set: PredefinedRelationalSet
    format:         FormatEnum  = FormatEnum.JSON
    num_records:    int         = Field(default=100, ge=1, le=1000)
    seed:           Optional[int] = None


# --- 4. Domain-specific request ---

class DomainRequest(BaseModel):
    """
    Pick a domain (ecommerce, hr, etc.) and get all its tables generated,
    either as individual tables or as a relational bundle.
    """
    domain:      DomainEnum
    relational:  bool          = True    # False → each table independent
    format:      FormatEnum    = FormatEnum.JSON
    num_records: int           = Field(default=100, ge=1, le=1000)
    seed:        Optional[int] = None


# --- 5. Database seeding request ---

class DBConnectionConfig(BaseModel):
    """
    Connection details for target database.
    IMPORTANT: We never persist these — used only for the duration of the request.
    """
    dialect:   DBDialectEnum
    host:      str  = Field(..., min_length=1)
    port:      int  = Field(..., ge=1, le=65535)
    database:  str  = Field(..., min_length=1)
    username:  str  = Field(..., min_length=1)
    password:  str  = Field(..., min_length=1)
    ssl:       bool = False

    # Safety guard — reject obvious production hostnames
    @field_validator("host")
    @classmethod
    def no_prod_hosts(cls, host: str) -> str:
        blocked_keywords = ["prod", "production", "live", "prd"]
        lower = host.lower()
        for kw in blocked_keywords:
            if kw in lower:
                raise ValueError(
                    f"Host '{host}' looks like a production server. "
                    "Please only seed dev / UAT environments."
                )
        return host


class DBSeedRequest(BaseModel):
    """Seed a database with generated data."""
    connection:     DBConnectionConfig
    tables:         List[UserDefinedTable]        = Field(..., min_length=1, max_length=10)
    relations:      Optional[List[RelationDefinition]] = None
    truncate_first: bool  = False   # truncate table before inserting
    batch_size:     int   = Field(default=500, ge=100, le=1000)
    seed:           Optional[int] = None


# --- 6. Connection test request (no data generated) ---

class DBTestRequest(BaseModel):
    connection: DBConnectionConfig


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class TableData(BaseModel):
    """Generated data for one table."""
    table_name:   str
    num_records:  int
    data:         Optional[str]  = None   # serialized content (format-dependent)
    filename:     Optional[str]  = None


class DataResponse(BaseModel):
    """Generic single-table response (backward-compatible)."""
    success:      bool
    data:         Optional[str]  = None
    filename:     Optional[str]  = None
    error:        Optional[str]  = None
    content_type: str            = "application/json"


class MultiTableResponse(BaseModel):
    """Response carrying multiple tables (relational / domain / schema-driven)."""
    success:      bool
    tables:       List[TableData]         = []
    relations:    Optional[List[Dict[str, Any]]] = None   # echo back relation graph
    error:        Optional[str]          = None
    format:       str                    = "JSON"


class DBSeedResponse(BaseModel):
    success:          bool
    tables_seeded:    List[str]  = []
    rows_inserted:    Dict[str, int] = {}
    error:            Optional[str]  = None
    warning:          Optional[str]  = None


class DBTestResponse(BaseModel):
    success:  bool
    message:  str
    dialect:  Optional[str] = None


class TopicInfo(BaseModel):
    """Used by /topics endpoint — backward-compatible."""
    name:        str
    description: str
    fields:      List[str]


class DomainInfo(BaseModel):
    """Used by /domains endpoint."""
    name:        str
    description: str
    tables:      List[str]
    relational:  bool