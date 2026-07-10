"""
data_generator.py — Core data generation engine

Handles:
  1. FieldGenerator          → generates a single value for any FieldTypeEnum
  2. RelationalDataGenerator → generates multiple linked tables respecting FK constraints
  3. DataGenerator           → top-level class (backward-compatible + new modes)
"""

from __future__ import annotations

import hashlib
import random
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from faker import Faker

from backend.models.schemas import (
    FieldTypeEnum,
    RelationDefinition,
    UserDefinedTable,
)
from backend.utils.constants import (
    DOMAIN_REGISTRY,
    RELATIONAL_SETS,
    TABLE_DEFINITIONS,
)


# ---------------------------------------------------------------------------
# 1. FieldGenerator — one value per FieldTypeEnum
# ---------------------------------------------------------------------------

class FieldGenerator:
    """
    Stateless (except for faker/random seed) value generator.
    Maps every FieldTypeEnum to a realistic fake value.
    Constraints (min, max, choices, etc.) are applied when provided.
    """

    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def generate(
        self,
        field_type: FieldTypeEnum,
        constraints: Optional[Any] = None,    # FieldConstraints | dict | None
        pk_index: Optional[int] = None,       # used for primary_key auto-increment
        fk_pool: Optional[List[Any]] = None,  # pool of parent PKs for foreign_key
    ) -> Any:
        """Generate a single value for the given field type."""

        c = constraints  # shorthand

        # Helper to get constraint attr (works for both Pydantic model and dict)
        def cget(attr: str, default=None):
            if c is None:
                return default
            if isinstance(c, dict):
                return c.get(attr, default)
            return getattr(c, attr, default)

        nullable = cget("nullable", False)
        if nullable and random.random() < 0.08:   # ~8% chance of None
            return None

        # ── Primary / Foreign Keys ────────────────────────────────────────
        if field_type == FieldTypeEnum.PRIMARY_KEY:
            if pk_index is not None:
                return pk_index + 1
            return str(uuid.uuid4())

        if field_type == FieldTypeEnum.FOREIGN_KEY:
            if fk_pool:
                return random.choice(fk_pool)
            return random.randint(1, 100)   # fallback if pool not provided

        # ── Personal ─────────────────────────────────────────────────────
        if field_type == FieldTypeEnum.FIRST_NAME:
            return self.fake.first_name()

        if field_type == FieldTypeEnum.LAST_NAME:
            return self.fake.last_name()

        if field_type == FieldTypeEnum.FULL_NAME:
            return self.fake.name()

        if field_type == FieldTypeEnum.EMAIL:
            return self.fake.email()

        if field_type == FieldTypeEnum.PHONE:
            return self.fake.phone_number()

        if field_type == FieldTypeEnum.DATE_OF_BIRTH:
            min_age = int(cget("min_value", 18))
            max_age = int(cget("max_value", 70))
            return self.fake.date_of_birth(
                minimum_age=min_age, maximum_age=max_age
            ).isoformat()

        if field_type == FieldTypeEnum.GENDER:
            return random.choice(["Male", "Female", "Non-binary", "Prefer not to say"])

        if field_type == FieldTypeEnum.ADDRESS:
            return self.fake.address().replace("\n", ", ")

        if field_type == FieldTypeEnum.CITY:
            return self.fake.city()

        if field_type == FieldTypeEnum.STATE:
            return self.fake.state()

        if field_type == FieldTypeEnum.COUNTRY:
            return self.fake.country()

        if field_type == FieldTypeEnum.ZIP_CODE:
            return self.fake.postcode()

        # ── Numbers ───────────────────────────────────────────────────────
        if field_type == FieldTypeEnum.INTEGER:
            lo = int(cget("min_value", 0))
            hi = int(cget("max_value", 10000))
            return random.randint(lo, hi)

        if field_type == FieldTypeEnum.FLOAT:
            lo  = float(cget("min_value", 0.0))
            hi  = float(cget("max_value", 1000.0))
            dec = int(cget("decimal_places", 2))
            return round(random.uniform(lo, hi), dec)

        if field_type == FieldTypeEnum.BOOLEAN:
            return random.choice([True, False])

        # ── Text / Identifiers ────────────────────────────────────────────
        if field_type == FieldTypeEnum.UUID:
            return str(uuid.uuid4())

        if field_type == FieldTypeEnum.SLUG:
            words = self.fake.words(nb=2)
            return "-".join(w.lower() for w in words)

        if field_type == FieldTypeEnum.USERNAME:
            min_l = int(cget("min_length", 5))
            max_l = int(cget("max_length", 15))
            return self.fake.user_name()[:max_l].ljust(min_l, "x")

        if field_type == FieldTypeEnum.PASSWORD_HASH:
            raw = self.fake.password(length=16)
            return "$2b$12$" + hashlib.sha256(raw.encode()).hexdigest()[:53]

        if field_type == FieldTypeEnum.URL:
            return self.fake.url()

        if field_type == FieldTypeEnum.IP_ADDRESS:
            return self.fake.ipv4()

        if field_type == FieldTypeEnum.MAC_ADDRESS:
            return self.fake.mac_address()

        if field_type == FieldTypeEnum.COLOR_HEX:
            return self.fake.color()

        # ── Temporal ─────────────────────────────────────────────────────
        if field_type == FieldTypeEnum.DATE:
            return self.fake.date_between(start_date="-5y", end_date="today").isoformat()

        if field_type == FieldTypeEnum.DATETIME:
            return self.fake.date_time_between(
                start_date="-5y", end_date="now"
            ).strftime("%Y-%m-%d %H:%M:%S")

        if field_type == FieldTypeEnum.TIME:
            return self.fake.time()

        if field_type == FieldTypeEnum.TIMESTAMP:
            dt = self.fake.date_time_between(start_date="-2y", end_date="now")
            return int(dt.timestamp())

        # ── Finance ───────────────────────────────────────────────────────
        if field_type == FieldTypeEnum.CURRENCY_CODE:
            return random.choice(["USD", "EUR", "GBP", "INR", "JPY", "AED", "SGD", "CAD", "AUD"])

        if field_type == FieldTypeEnum.AMOUNT:
            lo  = float(cget("min_value", 1.0))
            hi  = float(cget("max_value", 100000.0))
            dec = int(cget("decimal_places", 2))
            return round(random.uniform(lo, hi), dec)

        if field_type == FieldTypeEnum.IBAN:
            country = random.choice(["DE", "GB", "FR", "IN", "AE"])
            digits  = "".join([str(random.randint(0, 9)) for _ in range(18)])
            return f"{country}{digits}"

        if field_type == FieldTypeEnum.CREDIT_CARD:
            # Always masked — never expose full card numbers
            last4 = random.randint(1000, 9999)
            return f"**** **** **** {last4}"

        # ── Commerce ──────────────────────────────────────────────────────
        if field_type == FieldTypeEnum.PRODUCT_NAME:
            adjectives = ["Pro", "Ultra", "Smart", "Classic", "Premium", "Lite", "Max", "Elite"]
            nouns = ["Device", "Kit", "Pack", "System", "Tool", "Module", "Unit", "Set"]
            brand = self.fake.company().split()[0]
            return f"{brand} {random.choice(adjectives)} {random.choice(nouns)}"

        if field_type == FieldTypeEnum.CATEGORY:
            categories = [
                "Electronics", "Clothing", "Books", "Home & Living", "Sports",
                "Beauty", "Automotive", "Toys", "Grocery", "Furniture",
                "Health", "Office", "Garden", "Baby", "Tools",
            ]
            return random.choice(categories)

        if field_type == FieldTypeEnum.SKU:
            prefix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
            suffix = str(random.randint(10000, 99999))
            return f"{prefix}-{suffix}"

        if field_type == FieldTypeEnum.PRICE:
            lo  = float(cget("min_value", 1.0))
            hi  = float(cget("max_value", 9999.0))
            dec = int(cget("decimal_places", 2))
            return round(random.uniform(lo, hi), dec)

        if field_type == FieldTypeEnum.RATING:
            return round(random.uniform(1.0, 5.0), 1)

        # ── Company / HR ──────────────────────────────────────────────────
        if field_type == FieldTypeEnum.COMPANY_NAME:
            return self.fake.company()

        if field_type == FieldTypeEnum.JOB_TITLE:
            return self.fake.job()

        if field_type == FieldTypeEnum.DEPARTMENT:
            departments = [
                "Engineering", "Product", "Design", "Marketing", "Sales",
                "Finance", "HR", "Legal", "Operations", "Customer Success",
                "Data Science", "DevOps", "QA", "Research", "Administration",
            ]
            return random.choice(departments)

        if field_type == FieldTypeEnum.EMPLOYEE_ID:
            prefix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
            return f"{prefix}{random.randint(10000, 99999)}"

        if field_type == FieldTypeEnum.SALARY:
            lo = float(cget("min_value", 20000.0))
            hi = float(cget("max_value", 500000.0))
            return round(random.uniform(lo, hi), 2)

        # ── System ────────────────────────────────────────────────────────
        if field_type == FieldTypeEnum.STATUS:
            return random.choice(["active", "inactive", "pending", "suspended"])

        if field_type == FieldTypeEnum.ENUM_PICK:
            choices = cget("choices", ["option_a", "option_b", "option_c"])
            return random.choice(choices)

        # Fallback
        return self.fake.word()


# ---------------------------------------------------------------------------
# 2. RelationalDataGenerator
#    Generates multiple tables where FK columns reference actual PK values
#    from already-generated parent tables.
# ---------------------------------------------------------------------------

class RelationalDataGenerator:
    """
    Generates a set of tables in dependency order, ensuring FK integrity.

    How it works:
      1. Build a dependency graph from relations list.
      2. Topological sort → generation order (parents before children).
      3. Generate parent tables first, collect their PK values.
      4. When generating child tables, sample from parent PK pool for FK fields.
    """

    def __init__(self, fake: Faker) -> None:
        self.fake      = fake
        self.field_gen = FieldGenerator(fake)

    # ── Public entry points ───────────────────────────────────────────────

    def generate_from_tables(
        self,
        tables: List[UserDefinedTable],
        relations: Optional[List[RelationDefinition]] = None,
        num_records: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Schema-driven generation from UserDefinedTable objects.
        Returns { table_name: [records] }.
        """
        # Build FK map: (child_table, child_field) → [parent PKs]
        fk_map: Dict[Tuple[str, str], List[Any]] = {}

        # Determine generation order
        order = self._topological_order(
            [t.name for t in tables],
            relations or [],
        )
        table_by_name = {t.name: t for t in tables}

        result: Dict[str, List[Dict[str, Any]]] = {}

        for table_name in order:
            table = table_by_name[table_name]
            n     = table.num_records
            rows  = self._generate_table_rows(table, n, fk_map)
            result[table_name] = rows

            # Register PK values so child tables can reference them
            pk_field = next(
                (f for f in table.fields if f.type == FieldTypeEnum.PRIMARY_KEY), None
            )
            if pk_field:
                pk_values = [row[pk_field.name] for row in rows]
                # Register for all FK fields in other tables that point here
                if relations:
                    for rel in relations:
                        if rel.parent_table == table_name:
                            fk_map[(rel.child_table, rel.child_field)] = pk_values
                # Also register from inline FK declarations in child tables
                for other_table in tables:
                    for field in other_table.fields:
                        if (
                            field.type == FieldTypeEnum.FOREIGN_KEY
                            and field.references_table == table_name
                        ):
                            fk_map[(other_table.name, field.name)] = pk_values

        return result

    def generate_from_predefined(
        self,
        set_name: str,
        num_records: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate data from a RELATIONAL_SETS entry (e.g. 'ecommerce_full').
        Returns { table_name: [records] }.
        """
        rel_set  = RELATIONAL_SETS[set_name]
        tables   = rel_set["tables"]
        relations = rel_set["relations"]

        fk_map: Dict[Tuple[str, str], List[Any]] = {}
        result:  Dict[str, List[Dict[str, Any]]] = {}

        for table_name in tables:   # already in dependency order in constants.py
            table_def = TABLE_DEFINITIONS[table_name]
            rows      = self._generate_from_definition(
                table_name, table_def, num_records, fk_map
            )
            result[table_name] = rows

            # Extract and register PKs
            pk_field_name = next(
                (f[0] for f in table_def["fields"] if f[1] == "primary_key"), None
            )
            if pk_field_name:
                pk_values = [row[pk_field_name] for row in rows]
                for rel in relations:
                    if rel["parent"] == table_name:
                        fk_map[(rel["child"], rel["child_field"])] = pk_values

        return result

    def generate_domain(
        self,
        domain: str,
        relational: bool = True,
        num_records: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate all tables for a domain.
        If relational=True, uses the domain's relational set.
        If relational=False, generates each table independently.
        """
        domain_info = DOMAIN_REGISTRY[domain]

        if relational and domain_info["relational_sets"]:
            set_name = domain_info["relational_sets"][0]
            return self.generate_from_predefined(set_name, num_records)

        # Independent mode — each table standalone
        result: Dict[str, List[Dict[str, Any]]] = {}
        for table_name in domain_info["tables"]:
            if table_name in TABLE_DEFINITIONS:
                table_def = TABLE_DEFINITIONS[table_name]
                rows = self._generate_from_definition(
                    table_name, table_def, num_records, fk_map={}
                )
                result[table_name] = rows
        return result

    # ── Internal helpers ──────────────────────────────────────────────────

    def _generate_table_rows(
        self,
        table: UserDefinedTable,
        num_records: int,
        fk_map: Dict[Tuple[str, str], List[Any]],
    ) -> List[Dict[str, Any]]:
        """Generate rows for a UserDefinedTable object."""
        unique_trackers: Dict[str, Set[Any]] = {}
        rows: List[Dict[str, Any]] = []

        for i in range(num_records):
            row: Dict[str, Any] = {}
            for field in table.fields:
                fk_pool = fk_map.get((table.name, field.name))
                value   = self.field_gen.generate(
                    field_type  = field.type,
                    constraints = field.constraints,
                    pk_index    = i if field.type == FieldTypeEnum.PRIMARY_KEY else None,
                    fk_pool     = fk_pool,
                )

                # Uniqueness enforcement (best-effort, max 10 retries)
                if field.constraints and getattr(field.constraints, "unique", False):
                    unique_trackers.setdefault(field.name, set())
                    attempts = 0
                    while value in unique_trackers[field.name] and attempts < 10:
                        value = self.field_gen.generate(
                            field_type  = field.type,
                            constraints = field.constraints,
                            pk_index    = None,
                            fk_pool     = fk_pool,
                        )
                        attempts += 1
                    unique_trackers[field.name].add(value)

                row[field.name] = value
            rows.append(row)

        return rows

    def _generate_from_definition(
        self,
        table_name: str,
        table_def: Dict[str, Any],
        num_records: int,
        fk_map: Dict[Tuple[str, str], List[Any]],
    ) -> List[Dict[str, Any]]:
        """Generate rows from a TABLE_DEFINITIONS entry (tuple-based field list)."""
        unique_trackers: Dict[str, Set[Any]] = {}
        rows: List[Dict[str, Any]] = []

        for i in range(num_records):
            row: Dict[str, Any] = {}
            for field_tuple in table_def["fields"]:
                field_name  = field_tuple[0]
                field_type  = FieldTypeEnum(field_tuple[1])
                constraints = field_tuple[2] if len(field_tuple) > 2 else None

                # Resolve FK pool
                fk_pool = None
                if field_type == FieldTypeEnum.FOREIGN_KEY and constraints:
                    ref_table = constraints.get("references_table")
                    ref_field = constraints.get("references_field")
                    if ref_table and ref_field:
                        fk_pool = fk_map.get((table_name, field_name))

                value = self.field_gen.generate(
                    field_type  = field_type,
                    constraints = constraints,
                    pk_index    = i if field_type == FieldTypeEnum.PRIMARY_KEY else None,
                    fk_pool     = fk_pool,
                )

                # Uniqueness enforcement
                if constraints and constraints.get("unique"):
                    unique_trackers.setdefault(field_name, set())
                    attempts = 0
                    while value in unique_trackers[field_name] and attempts < 10:
                        value = self.field_gen.generate(
                            field_type  = field_type,
                            constraints = constraints,
                            fk_pool     = fk_pool,
                        )
                        attempts += 1
                    unique_trackers[field_name].add(value)

                row[field_name] = value
            rows.append(row)

        return rows

    @staticmethod
    def _topological_order(
        table_names: List[str],
        relations: List[RelationDefinition],
    ) -> List[str]:
        """
        Kahn's algorithm — returns tables in dependency order.
        Tables with no parents come first.
        """
        from collections import defaultdict, deque

        in_degree: Dict[str, int]        = {n: 0 for n in table_names}
        adj:       Dict[str, List[str]]  = defaultdict(list)

        for rel in relations:
            if rel.parent_table in in_degree and rel.child_table in in_degree:
                adj[rel.parent_table].append(rel.child_table)
                in_degree[rel.child_table] += 1

        queue  = deque([n for n in table_names if in_degree[n] == 0])
        order: List[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbour in adj[node]:
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)

        # If cycle exists, fallback to original order (validator should have caught this)
        if len(order) != len(table_names):
            return table_names

        return order


# ---------------------------------------------------------------------------
# 3. DataGenerator — top-level class (backward-compatible)
# ---------------------------------------------------------------------------

class DataGenerator:
    """
    Primary entry point.  All generation modes go through here.

    Backward-compatible: generate_for_topic() still works exactly as before,
    now backed by TABLE_DEFINITIONS instead of hardcoded methods.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self.fake = Faker(["en_US"])
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        self.field_gen    = FieldGenerator(self.fake)
        self.relational   = RelationalDataGenerator(self.fake)

    # ── Mode 1: Backward-compatible single topic ──────────────────────────

    def generate_for_topic(
        self,
        topic: str,
        num_records: int,
        custom_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Drop-in replacement for the old generate_for_topic().
        Looks up the table in TABLE_DEFINITIONS; falls back to generic
        custom generation if not found.
        """
        if topic in TABLE_DEFINITIONS:
            return self.relational._generate_from_definition(
                table_name  = topic,
                table_def   = TABLE_DEFINITIONS[topic],
                num_records = num_records,
                fk_map      = {},   # standalone — no FK linking
            )

        # Custom / unknown topic — generic field-name heuristic generation
        return self._generate_custom(num_records, custom_fields or [])

    # ── Mode 2: Schema-driven (user-defined tables) ───────────────────────

    def generate_from_schema(
        self,
        tables: List[UserDefinedTable],
        relations: Optional[List[RelationDefinition]] = None,
        num_records: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate data from user-supplied schema."""
        return self.relational.generate_from_tables(tables, relations, num_records)

    # ── Mode 3: Predefined relational set ────────────────────────────────

    def generate_relational_set(
        self,
        set_name: str,
        num_records: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate a predefined relational bundle (e.g. ecommerce_full)."""
        return self.relational.generate_from_predefined(set_name, num_records)

    # ── Mode 4: Domain ────────────────────────────────────────────────────

    def generate_for_domain(
        self,
        domain: str,
        relational: bool = True,
        num_records: int = 100,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all tables for a domain."""
        return self.relational.generate_domain(domain, relational, num_records)

    # ── Fallback: generic custom field generation ─────────────────────────

    def _generate_custom(
        self,
        num_records: int,
        custom_fields: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Heuristic generation based on field name keywords.
        Used when topic is not in TABLE_DEFINITIONS (backward compat).
        """
        _EMAIL_DOMAINS = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
            "icloud.com", "protonmail.com", "zoho.com",
        ]

        rows: List[Dict[str, Any]] = []
        for i in range(num_records):
            record: Dict[str, Any] = {"id": i + 1}
            last_name = ""
            for field in custom_fields:
                fl = field.lower()
                if "name" in fl:
                    val     = self.fake.name()
                    last_name = val
                elif "email" in fl:
                    safe = last_name.lower().replace(" ", ".").replace("'", "")
                    val  = f"{safe or self.fake.user_name()}@{random.choice(_EMAIL_DOMAINS)}"
                elif "phone" in fl:
                    val = self.fake.phone_number()
                elif "address" in fl:
                    val = self.fake.address().replace("\n", ", ")
                elif "date" in fl or "dob" in fl:
                    val = self.fake.date().isoformat()
                elif "price" in fl or "amount" in fl or "salary" in fl:
                    val = round(random.uniform(100, 100000), 2)
                elif "age" in fl:
                    val = random.randint(18, 70)
                elif "status" in fl:
                    val = random.choice(["active", "inactive", "pending", "completed"])
                elif "category" in fl:
                    val = self.fake.word().capitalize()
                elif "id" in fl:
                    val = i + 1
                elif "url" in fl or "link" in fl:
                    val = self.fake.url()
                elif "city" in fl:
                    val = self.fake.city()
                elif "country" in fl:
                    val = self.fake.country()
                elif "company" in fl or "employer" in fl:
                    val = self.fake.company()
                elif "job" in fl or "title" in fl or "role" in fl:
                    val = self.fake.job()
                else:
                    val = self.fake.word()
                record[field] = val
            rows.append(record)

        return rows