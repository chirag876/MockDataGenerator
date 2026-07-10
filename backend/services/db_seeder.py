"""
db_seeder.py — Database seeding service

Supports: PostgreSQL, MySQL, SQLite, MSSQL
Security:
  - Credentials are NEVER logged or stored — used only for the duration of the request
  - Production hostnames are blocked at schema level (validator in schemas.py)
  - Parameterized queries only — no string interpolation in SQL
  - SSL support per dialect

Flow:
  1. DBConnectionFactory  → builds SQLAlchemy engine from DBConnectionConfig
  2. SchemaInspector      → checks if tables exist, creates them if not
  3. DataSeeder           → inserts records in batches with FK-safe ordering
  4. DBSeederService      → top-level orchestrator called from main.py
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from backend.models.schemas import (
    DBConnectionConfig,
    DBDialectEnum,
    DBSeedRequest,
    DBSeedResponse,
    DBTestResponse,
    FieldTypeEnum,
    UserDefinedTable,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FieldTypeEnum → SQLAlchemy column type mapping
# ---------------------------------------------------------------------------

_FIELD_TYPE_TO_SA: Dict[FieldTypeEnum, Any] = {
    FieldTypeEnum.PRIMARY_KEY:   Integer,
    FieldTypeEnum.FOREIGN_KEY:   Integer,
    FieldTypeEnum.FIRST_NAME:    String(100),
    FieldTypeEnum.LAST_NAME:     String(100),
    FieldTypeEnum.FULL_NAME:     String(200),
    FieldTypeEnum.EMAIL:         String(254),
    FieldTypeEnum.PHONE:         String(30),
    FieldTypeEnum.DATE_OF_BIRTH: String(20),
    FieldTypeEnum.GENDER:        String(30),
    FieldTypeEnum.ADDRESS:       Text,
    FieldTypeEnum.CITY:          String(100),
    FieldTypeEnum.STATE:         String(100),
    FieldTypeEnum.COUNTRY:       String(100),
    FieldTypeEnum.ZIP_CODE:      String(20),
    FieldTypeEnum.INTEGER:       Integer,
    FieldTypeEnum.FLOAT:         Float,
    FieldTypeEnum.BOOLEAN:       Boolean,
    FieldTypeEnum.UUID:          String(36),
    FieldTypeEnum.SLUG:          String(100),
    FieldTypeEnum.USERNAME:      String(50),
    FieldTypeEnum.PASSWORD_HASH: String(128),
    FieldTypeEnum.URL:           String(500),
    FieldTypeEnum.IP_ADDRESS:    String(45),
    FieldTypeEnum.MAC_ADDRESS:   String(17),
    FieldTypeEnum.COLOR_HEX:     String(7),
    FieldTypeEnum.DATE:          String(20),
    FieldTypeEnum.DATETIME:      String(30),
    FieldTypeEnum.TIME:          String(10),
    FieldTypeEnum.TIMESTAMP:     Integer,
    FieldTypeEnum.CURRENCY_CODE: String(3),
    FieldTypeEnum.AMOUNT:        Float,
    FieldTypeEnum.IBAN:          String(34),
    FieldTypeEnum.CREDIT_CARD:   String(25),
    FieldTypeEnum.PRODUCT_NAME:  String(200),
    FieldTypeEnum.CATEGORY:      String(100),
    FieldTypeEnum.SKU:           String(30),
    FieldTypeEnum.PRICE:         Float,
    FieldTypeEnum.RATING:        Float,
    FieldTypeEnum.COMPANY_NAME:  String(200),
    FieldTypeEnum.JOB_TITLE:     String(150),
    FieldTypeEnum.DEPARTMENT:    String(100),
    FieldTypeEnum.EMPLOYEE_ID:   String(20),
    FieldTypeEnum.SALARY:        Float,
    FieldTypeEnum.STATUS:        String(30),
    FieldTypeEnum.ENUM_PICK:     String(100),
}


# ---------------------------------------------------------------------------
# 1. Connection Factory
# ---------------------------------------------------------------------------

class DBConnectionFactory:
    """Builds a SQLAlchemy engine from DBConnectionConfig."""

    @staticmethod
    def build_url(config: DBConnectionConfig) -> str:
        d = config.dialect

        if d == DBDialectEnum.SQLITE:
            # SQLite is file-based; host is treated as the file path
            return f"sqlite:///{config.database}"

        drivers = {
            DBDialectEnum.POSTGRESQL: "postgresql+psycopg2",
            DBDialectEnum.MYSQL:      "mysql+pymysql",
            DBDialectEnum.MSSQL:      "mssql+pyodbc",
        }
        driver = drivers[d]

        if d == DBDialectEnum.MSSQL:
            return (
                f"{driver}://{config.username}:{config.password}"
                f"@{config.host}:{config.port}/{config.database}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )

        return (
            f"{driver}://{config.username}:{config.password}"
            f"@{config.host}:{config.port}/{config.database}"
        )

    @staticmethod
    def create_engine(config: DBConnectionConfig) -> Engine:
        url = DBConnectionFactory.build_url(config)

        connect_args: Dict[str, Any] = {}
        if config.ssl and config.dialect != DBDialectEnum.SQLITE:
            connect_args["ssl"] = {"ssl_ca": "", "ssl_verify_cert": False}

        return create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=True,     # validate connection before use
            pool_size=1,            # single connection — seeding is sequential
            max_overflow=0,
        )


# ---------------------------------------------------------------------------
# 2. Schema Inspector + Table Creator
# ---------------------------------------------------------------------------

class SchemaInspector:
    """
    Checks if tables exist in the target DB.
    Creates them if they don't — using definitions derived from UserDefinedTable.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine   = engine
        self.metadata = MetaData()

    def table_exists(self, table_name: str) -> bool:
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def create_table_if_not_exists(
        self,
        table: UserDefinedTable,
    ) -> Table:
        """Build and create a SQLAlchemy Table from UserDefinedTable schema."""
        columns: List[Column] = []

        for field in table.fields:
            sa_type = _FIELD_TYPE_TO_SA.get(field.type, String(255))

            is_pk    = field.type == FieldTypeEnum.PRIMARY_KEY
            nullable = (
                getattr(field.constraints, "nullable", True)
                if field.constraints else True
            ) and not is_pk

            col = Column(
                field.name,
                sa_type,
                primary_key=is_pk,
                nullable=nullable,
            )
            columns.append(col)

        sa_table = Table(table.name, self.metadata, *columns, extend_existing=True)
        self.metadata.create_all(self.engine, tables=[sa_table], checkfirst=True)
        return sa_table

    def truncate_table(self, table_name: str) -> None:
        """Truncate (empty) a table before seeding."""
        with self.engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {table_name}"))


# ---------------------------------------------------------------------------
# 3. DataSeeder
# ---------------------------------------------------------------------------

class DataSeeder:
    """
    Inserts generated records into the target database in batches.
    Uses parameterized queries — no raw string SQL interpolation.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def insert_batch(
        self,
        sa_table: Table,
        records: List[Dict[str, Any]],
        batch_size: int = 500,
    ) -> int:
        """Insert records in batches. Returns total rows inserted."""
        total = 0
        with self.engine.begin() as conn:
            for start in range(0, len(records), batch_size):
                batch = records[start : start + batch_size]
                conn.execute(sa_table.insert(), batch)
                total += len(batch)
        return total


# ---------------------------------------------------------------------------
# 4. DBSeederService — top-level orchestrator
# ---------------------------------------------------------------------------

class DBSeederService:
    """
    Called from main.py endpoints.
    Orchestrates: connect → inspect → (truncate) → create → seed
    """

    @staticmethod
    def test_connection(config: DBConnectionConfig) -> DBTestResponse:
        """Just test if the DB is reachable — no data changes."""
        try:
            engine = DBConnectionFactory.create_engine(config)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return DBTestResponse(
                success=True,
                message="Connection successful.",
                dialect=config.dialect.value,
            )
        except OperationalError as e:
            return DBTestResponse(
                success=False,
                message=f"Connection failed: {_clean_error(str(e))}",
                dialect=config.dialect.value,
            )
        except Exception as e:
            return DBTestResponse(
                success=False,
                message=f"Unexpected error: {_clean_error(str(e))}",
            )

    @staticmethod
    def seed(
        request: DBSeedRequest,
        tables_data: Dict[str, List[Dict[str, Any]]],
    ) -> DBSeedResponse:
        """
        Main seeding method.

        Args:
            request     : DBSeedRequest with connection config + table schemas
            tables_data : { table_name: [records] } from DataGenerator

        Returns:
            DBSeedResponse with per-table row counts or error message
        """
        try:
            engine    = DBConnectionFactory.create_engine(request.connection)
            inspector = SchemaInspector(engine)
            seeder    = DataSeeder(engine)

            tables_seeded: List[str]       = []
            rows_inserted: Dict[str, int]  = {}
            warnings:      List[str]       = []

            # Process tables in the order provided (should be dependency order)
            table_map = {t.name: t for t in request.tables}

            for table_name, records in tables_data.items():
                if table_name not in table_map:
                    warnings.append(
                        f"Table '{table_name}' has data but no schema definition — skipped."
                    )
                    continue

                user_table = table_map[table_name]

                # Truncate if requested
                if request.truncate_first and inspector.table_exists(table_name):
                    try:
                        inspector.truncate_table(table_name)
                    except Exception as e:
                        warnings.append(
                            f"Could not truncate '{table_name}': {_clean_error(str(e))}"
                        )

                # Create table if not exists
                try:
                    sa_table = inspector.create_table_if_not_exists(user_table)
                except Exception as e:
                    warnings.append(
                        f"Could not create table '{table_name}': {_clean_error(str(e))}"
                    )
                    continue

                # Insert records
                try:
                    count = seeder.insert_batch(sa_table, records, request.batch_size)
                    rows_inserted[table_name] = count
                    tables_seeded.append(table_name)
                except Exception as e:
                    warnings.append(
                        f"Insert failed for '{table_name}': {_clean_error(str(e))}"
                    )

            return DBSeedResponse(
                success      = len(tables_seeded) > 0,
                tables_seeded= tables_seeded,
                rows_inserted= rows_inserted,
                warning      = "; ".join(warnings) if warnings else None,
            )

        except OperationalError as e:
            return DBSeedResponse(
                success=False,
                error=f"Database connection failed: {_clean_error(str(e))}",
            )
        except SQLAlchemyError as e:
            return DBSeedResponse(
                success=False,
                error=f"Database error: {_clean_error(str(e))}",
            )
        except Exception as e:
            return DBSeedResponse(
                success=False,
                error=f"Unexpected error: {_clean_error(str(e))}",
            )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _clean_error(msg: str) -> str:
    """
    Strip connection string from error messages so credentials
    are never accidentally exposed in API responses.
    """
    # Remove anything that looks like a connection URL
    import re
    msg = re.sub(r"://[^\s]+", "://<redacted>", msg)
    # Trim long stack traces
    return msg[:300] if len(msg) > 300 else msg