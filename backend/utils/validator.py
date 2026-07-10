"""
validator.py — Schema validation + content safety layer

Responsibilities:
  1. SchemaValidator   → validates user-defined tables & relations for logical correctness
  2. ContentSafetyChecker → blocks explicit / harmful field names and schema patterns
  3. RelationValidator → validates user-defined relation graphs (no cycles, valid references)
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

from backend.models.schemas import (
    FieldTypeEnum,
    RelationDefinition,
    UserDefinedTable,
)


# ---------------------------------------------------------------------------
# Content Safety — blocked patterns
# ---------------------------------------------------------------------------

# Field names containing any of these substrings (case-insensitive) are rejected
_BLOCKED_FIELD_SUBSTRINGS: List[str] = [
    # Explicit / adult
    "porn", "nude", "naked", "nsfw", "sex", "erotic", "fetish",
    "xxx", "adult_content", "explicit",
    # Violence / hate
    "kill", "murder", "torture", "weapon", "bomb", "drug_recipe",
    "terror", "genocide",
    # Credential abuse
    "plaintext_password", "raw_password", "password_plain",
    # PII that could enable real harm
    "ssn", "social_security", "aadhar_raw", "biometric_raw",
]

# Table names containing any of these are rejected
_BLOCKED_TABLE_SUBSTRINGS: List[str] = [
    "porn", "nude", "nsfw", "xxx", "adult", "explicit",
    "terror", "weapon", "drug",
]

# Compiled for speed
_BLOCKED_FIELD_RE  = re.compile(
    "|".join(re.escape(s) for s in _BLOCKED_FIELD_SUBSTRINGS), re.IGNORECASE
)
_BLOCKED_TABLE_RE  = re.compile(
    "|".join(re.escape(s) for s in _BLOCKED_TABLE_SUBSTRINGS), re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Result dataclass (lightweight, no pydantic needed here)
# ---------------------------------------------------------------------------

class ValidationResult:
    __slots__ = ("ok", "errors", "warnings")

    def __init__(self) -> None:
        self.ok:       bool         = True
        self.errors:   List[str]    = []
        self.warnings: List[str]    = []

    def fail(self, msg: str) -> None:
        self.ok = False
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def merge(self, other: "ValidationResult") -> None:
        if not other.ok:
            self.ok = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


# ---------------------------------------------------------------------------
# 1. Content Safety Checker
# ---------------------------------------------------------------------------

class ContentSafetyChecker:
    """
    Checks table and field names against blocked-content patterns.
    Called before any generation happens.
    """

    @staticmethod
    def check_table_name(name: str) -> ValidationResult:
        result = ValidationResult()
        if _BLOCKED_TABLE_RE.search(name):
            result.fail(
                f"Table name '{name}' contains a restricted keyword. "
                "Please rename the table."
            )
        return result

    @staticmethod
    def check_field_name(field_name: str, table_name: str) -> ValidationResult:
        result = ValidationResult()
        if _BLOCKED_FIELD_RE.search(field_name):
            result.fail(
                f"Field '{field_name}' in table '{table_name}' contains a "
                "restricted keyword and cannot be used."
            )
        return result

    @classmethod
    def check_table(cls, table: UserDefinedTable) -> ValidationResult:
        result = ValidationResult()
        result.merge(cls.check_table_name(table.name))
        for field in table.fields:
            result.merge(cls.check_field_name(field.name, table.name))
        return result

    @classmethod
    def check_all_tables(cls, tables: List[UserDefinedTable]) -> ValidationResult:
        result = ValidationResult()
        for table in tables:
            result.merge(cls.check_table(table))
        return result


# ---------------------------------------------------------------------------
# 2. Schema Validator
# ---------------------------------------------------------------------------

class SchemaValidator:
    """
    Validates the logical correctness of user-defined table schemas.

    Checks:
      - Exactly one primary_key per table
      - No duplicate field names within a table
      - foreign_key fields have valid references_table / references_field
      - enum_pick fields have a non-empty choices list
      - Constraint ranges are sane (min < max)
      - Field count limits
    """

    MAX_FIELDS_PER_TABLE = 30

    @classmethod
    def validate_table(cls, table: UserDefinedTable) -> ValidationResult:
        result = ValidationResult()

        field_names: List[str] = []
        pk_count = 0

        for field in table.fields:
            # Duplicate field names
            if field.name in field_names:
                result.fail(
                    f"Table '{table.name}': duplicate field name '{field.name}'."
                )
            field_names.append(field.name)

            # Primary key count
            if field.type == FieldTypeEnum.PRIMARY_KEY:
                pk_count += 1

            # Foreign key must name a table + field
            if field.type == FieldTypeEnum.FOREIGN_KEY:
                if not field.references_table:
                    result.fail(
                        f"Table '{table.name}', field '{field.name}': "
                        "foreign_key must specify references_table."
                    )
                if not field.references_field:
                    result.fail(
                        f"Table '{table.name}', field '{field.name}': "
                        "foreign_key must specify references_field."
                    )

            # enum_pick needs choices
            if field.type == FieldTypeEnum.ENUM_PICK:
                if (
                    not field.constraints
                    or not field.constraints.choices
                    or len(field.constraints.choices) == 0
                ):
                    result.fail(
                        f"Table '{table.name}', field '{field.name}': "
                        "enum_pick type requires at least one choice in constraints.choices."
                    )

            # Constraint sanity
            if field.constraints:
                c = field.constraints
                if (
                    c.min_value is not None
                    and c.max_value is not None
                    and c.min_value >= c.max_value
                ):
                    result.fail(
                        f"Table '{table.name}', field '{field.name}': "
                        f"min_value ({c.min_value}) must be less than max_value ({c.max_value})."
                    )
                if (
                    c.min_length is not None
                    and c.max_length is not None
                    and c.min_length >= c.max_length
                ):
                    result.fail(
                        f"Table '{table.name}', field '{field.name}': "
                        f"min_length ({c.min_length}) must be less than max_length ({c.max_length})."
                    )

        # Exactly one PK
        if pk_count == 0:
            result.fail(
                f"Table '{table.name}': must have exactly one primary_key field."
            )
        elif pk_count > 1:
            result.fail(
                f"Table '{table.name}': found {pk_count} primary_key fields — only one allowed."
            )

        # Field count
        if len(table.fields) > cls.MAX_FIELDS_PER_TABLE:
            result.fail(
                f"Table '{table.name}': has {len(table.fields)} fields — "
                f"maximum allowed is {cls.MAX_FIELDS_PER_TABLE}."
            )

        return result

    @classmethod
    def validate_all_tables(cls, tables: List[UserDefinedTable]) -> ValidationResult:
        result = ValidationResult()

        # Unique table names
        names = [t.name for t in tables]
        if len(names) != len(set(names)):
            duplicates = {n for n in names if names.count(n) > 1}
            result.fail(f"Duplicate table names found: {duplicates}")

        for table in tables:
            result.merge(cls.validate_table(table))

        return result


# ---------------------------------------------------------------------------
# 3. Relation Validator
# ---------------------------------------------------------------------------

class RelationValidator:
    """
    Validates user-defined RelationDefinition objects against the provided tables.

    Checks:
      - parent_table and child_table exist in the table list
      - parent_field exists in parent_table and is a primary_key
      - child_field exists in child_table and is a foreign_key
      - No circular dependency (cycle detection via DFS)
    """

    @staticmethod
    def _get_table_map(
        tables: List[UserDefinedTable],
    ) -> Dict[str, Dict[str, FieldTypeEnum]]:
        """Returns { table_name: { field_name: field_type } }"""
        return {
            t.name: {f.name: f.type for f in t.fields}
            for t in tables
        }

    @classmethod
    def validate_relations(
        cls,
        relations: List[RelationDefinition],
        tables: List[UserDefinedTable],
    ) -> ValidationResult:
        result = ValidationResult()
        table_map = cls._get_table_map(tables)
        table_names = set(table_map.keys())

        for rel in relations:
            # Tables exist
            if rel.parent_table not in table_names:
                result.fail(
                    f"Relation references unknown parent table '{rel.parent_table}'."
                )
                continue
            if rel.child_table not in table_names:
                result.fail(
                    f"Relation references unknown child table '{rel.child_table}'."
                )
                continue

            parent_fields = table_map[rel.parent_table]
            child_fields  = table_map[rel.child_table]

            # Parent field exists and is a PK
            if rel.parent_field not in parent_fields:
                result.fail(
                    f"Relation: field '{rel.parent_field}' not found in "
                    f"parent table '{rel.parent_table}'."
                )
            elif parent_fields[rel.parent_field] != FieldTypeEnum.PRIMARY_KEY:
                result.warn(
                    f"Relation: '{rel.parent_table}.{rel.parent_field}' is not "
                    "a primary_key — referencing non-PK fields may cause data inconsistency."
                )

            # Child field exists and is a FK
            if rel.child_field not in child_fields:
                result.fail(
                    f"Relation: field '{rel.child_field}' not found in "
                    f"child table '{rel.child_table}'."
                )
            elif child_fields[rel.child_field] != FieldTypeEnum.FOREIGN_KEY:
                result.warn(
                    f"Relation: '{rel.child_table}.{rel.child_field}' is not "
                    "declared as foreign_key type — data linking may be inaccurate."
                )

        # Cycle detection
        cycle_result = cls._detect_cycles(relations, table_names)
        result.merge(cycle_result)

        return result

    @classmethod
    def _detect_cycles(
        cls,
        relations: List[RelationDefinition],
        table_names: Set[str],
    ) -> ValidationResult:
        """DFS-based cycle detection on the relation graph."""
        result = ValidationResult()

        # Build adjacency list: parent → [children]
        graph: Dict[str, List[str]] = {name: [] for name in table_names}
        for rel in relations:
            if rel.parent_table in graph:
                graph[rel.parent_table].append(rel.child_table)

        visited:    Set[str] = set()
        rec_stack:  Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbour in graph.get(node, []):
                if neighbour not in visited:
                    if dfs(neighbour):
                        return True
                elif neighbour in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for table in table_names:
            if table not in visited:
                if dfs(table):
                    result.fail(
                        "Circular dependency detected in table relations. "
                        "Please ensure relations form a directed acyclic graph (no table "
                        "can be its own ancestor)."
                    )
                    break   # One error is enough — user needs to fix the graph

        return result


# ---------------------------------------------------------------------------
# 4. Top-level validate() — single entry point called from main.py
# ---------------------------------------------------------------------------

def validate_schema_request(
    tables: List[UserDefinedTable],
    relations: Optional[List[RelationDefinition]] = None,
) -> ValidationResult:
    """
    Full validation pipeline:
      content safety → schema structure → relation graph

    Returns a ValidationResult.
    If result.ok is False, the request must be rejected before any generation.
    """
    result = ValidationResult()

    # Step 1 — content safety
    result.merge(ContentSafetyChecker.check_all_tables(tables))

    # Stop early if blocked content found — no point validating further
    if not result.ok:
        return result

    # Step 2 — schema structure
    result.merge(SchemaValidator.validate_all_tables(tables))

    # Step 3 — relation graph (only if relations provided)
    if relations:
        result.merge(RelationValidator.validate_relations(relations, tables))

    return result