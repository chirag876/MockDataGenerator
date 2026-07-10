"""
constants.py — All static configuration for Mock Data Generator

Structure:
  1. SUPPORTED_FORMATS
  2. DOMAIN_REGISTRY       → domain → { description, tables, relational_sets }
  3. PREDEFINED_TOPICS     → backward-compatible flat dict (auto-built from DOMAIN_REGISTRY)
  4. RELATIONAL_SETS       → predefined relational bundles with full table + field definitions
  5. FIELD_TYPE_LABELS     → human-readable labels for FieldTypeEnum (used in frontend)
  6. DB_DEFAULT_PORTS      → default ports per dialect
"""

# ---------------------------------------------------------------------------
# 1. Supported formats
# ---------------------------------------------------------------------------

SUPPORTED_FORMATS = ["JSON", "CSV", "TSV", "YAML", "XML", "Parquet"]


# ---------------------------------------------------------------------------
# 2. Domain Registry
#    Each domain has:
#      - description      : shown in /domains endpoint
#      - tables           : list of table names belonging to this domain
#      - relational_sets  : which RELATIONAL_SETS keys apply to this domain
#      - independent_ok   : whether tables make sense standalone (always True)
# ---------------------------------------------------------------------------

DOMAIN_REGISTRY = {
    "ecommerce": {
        "description": "E-commerce domain — customers, products, orders, reviews",
        "tables": ["customers", "products", "categories", "orders", "order_items", "reviews"],
        "relational_sets": ["ecommerce_full"],
        "independent_ok": True,
    },
    "hr": {
        "description": "Human Resources — departments, employees, payroll, leave",
        "tables": ["departments", "employees", "payroll", "leave_requests"],
        "relational_sets": ["hr_full"],
        "independent_ok": True,
    },
    "healthcare": {
        "description": "Healthcare — doctors, patients, appointments, prescriptions",
        "tables": ["doctors", "patients", "appointments", "prescriptions"],
        "relational_sets": ["healthcare_full"],
        "independent_ok": True,
    },
    "education": {
        "description": "Education — courses, students, enrollments, grades",
        "tables": ["courses", "students", "enrollments", "grades"],
        "relational_sets": ["education_full"],
        "independent_ok": True,
    },
    "banking": {
        "description": "Banking — accounts, customers, transactions, loans",
        "tables": ["bank_customers", "accounts", "transactions", "loans"],
        "relational_sets": ["banking_full"],
        "independent_ok": True,
    },
    "logistics": {
        "description": "Logistics — warehouses, shipments, drivers, deliveries",
        "tables": ["warehouses", "drivers", "shipments", "deliveries"],
        "relational_sets": ["logistics_full"],
        "independent_ok": True,
    },
    "real_estate": {
        "description": "Real Estate — agents, properties, buyers, transactions",
        "tables": ["agents", "properties", "buyers", "property_transactions"],
        "relational_sets": ["real_estate_full"],
        "independent_ok": True,
    },
    "iot": {
        "description": "IoT — devices, sensor readings, alerts",
        "tables": ["devices", "sensor_readings", "alerts"],
        "relational_sets": ["iot_full"],
        "independent_ok": True,
    },
    "social_media": {
        "description": "Social Media — users, posts, comments, likes",
        "tables": ["sm_users", "posts", "comments", "likes"],
        "relational_sets": ["social_media_full"],
        "independent_ok": True,
    },
    "aviation": {
        "description": "Aviation — pilots, aircraft, flights, pilot log book",
        "tables": ["pilots", "aircraft", "flights", "pilot_log_book"],
        "relational_sets": ["aviation_full"],
        "independent_ok": True,
    },
    "weather": {
        "description": "Weather — stations, observations, forecasts",
        "tables": ["weather_stations", "observations", "forecasts"],
        "relational_sets": ["weather_full"],
        "independent_ok": True,
    },
}


# ---------------------------------------------------------------------------
# 3. Table Definitions
#    Each table has:
#      - description  : short label
#      - fields       : ordered list of (field_name, field_type, constraints_dict_or_None)
#
#    field_type values must match FieldTypeEnum in schemas.py
# ---------------------------------------------------------------------------

TABLE_DEFINITIONS = {

    # ── ECOMMERCE ────────────────────────────────────────────────────────────

    "customers": {
        "description": "Customer profiles",
        "fields": [
            ("customer_id",  "primary_key",  None),
            ("first_name",   "first_name",   None),
            ("last_name",    "last_name",    None),
            ("email",        "email",        {"unique": True}),
            ("phone",        "phone",        None),
            ("address",      "address",      None),
            ("city",         "city",         None),
            ("country",      "country",      None),
            ("created_at",   "datetime",     None),
        ],
    },
    "products": {
        "description": "Product catalog",
        "fields": [
            ("product_id",   "primary_key",  None),
            ("product_name", "product_name", None),
            ("category",     "category",     None),
            ("price",        "price",        {"min_value": 1, "max_value": 9999}),
            ("sku",          "sku",          {"unique": True}),
            ("stock",        "integer",      {"min_value": 0, "max_value": 5000}),
            ("rating",       "rating",       None),
        ],
    },
    "categories": {
        "description": "Product categories",
        "fields": [
            ("category_id",  "primary_key",  None),
            ("name",         "category",     None),
            ("slug",         "slug",         None),
        ],
    },
    "orders": {
        "description": "Customer orders",
        "fields": [
            ("order_id",     "primary_key",  None),
            ("customer_id",  "foreign_key",  {"references_table": "customers", "references_field": "customer_id"}),
            ("order_date",   "datetime",     None),
            ("status",       "enum_pick",    {"choices": ["pending", "confirmed", "shipped", "delivered", "cancelled"]}),
            ("total_amount", "amount",       {"min_value": 10, "max_value": 50000}),
        ],
    },
    "order_items": {
        "description": "Line items within each order",
        "fields": [
            ("item_id",      "primary_key",  None),
            ("order_id",     "foreign_key",  {"references_table": "orders",   "references_field": "order_id"}),
            ("product_id",   "foreign_key",  {"references_table": "products", "references_field": "product_id"}),
            ("quantity",     "integer",      {"min_value": 1, "max_value": 20}),
            ("unit_price",   "price",        {"min_value": 1, "max_value": 9999}),
        ],
    },
    "reviews": {
        "description": "Product reviews by customers",
        "fields": [
            ("review_id",    "primary_key",  None),
            ("product_id",   "foreign_key",  {"references_table": "products",  "references_field": "product_id"}),
            ("customer_id",  "foreign_key",  {"references_table": "customers", "references_field": "customer_id"}),
            ("rating",       "rating",       None),
            ("created_at",   "datetime",     None),
        ],
    },

    # ── HR ───────────────────────────────────────────────────────────────────

    "departments": {
        "description": "Company departments",
        "fields": [
            ("department_id",   "primary_key",  None),
            ("department_name", "department",   None),
            ("location",        "city",         None),
        ],
    },
    "employees": {
        "description": "Employee records",
        "fields": [
            ("employee_id",   "primary_key",  None),
            ("first_name",    "first_name",   None),
            ("last_name",     "last_name",    None),
            ("email",         "email",        {"unique": True}),
            ("department_id", "foreign_key",  {"references_table": "departments", "references_field": "department_id"}),
            ("job_title",     "job_title",    None),
            ("salary",        "salary",       None),
            ("hire_date",     "date",         None),
        ],
    },
    "payroll": {
        "description": "Monthly payroll records",
        "fields": [
            ("payroll_id",    "primary_key",  None),
            ("employee_id",   "foreign_key",  {"references_table": "employees", "references_field": "employee_id"}),
            ("pay_period",    "date",         None),
            ("gross_salary",  "salary",       None),
            ("tax_deducted",  "amount",       {"min_value": 0, "max_value": 50000}),
            ("net_salary",    "salary",       None),
        ],
    },
    "leave_requests": {
        "description": "Employee leave requests",
        "fields": [
            ("leave_id",      "primary_key",  None),
            ("employee_id",   "foreign_key",  {"references_table": "employees", "references_field": "employee_id"}),
            ("leave_type",    "enum_pick",    {"choices": ["casual", "sick", "earned", "maternity", "paternity"]}),
            ("start_date",    "date",         None),
            ("end_date",      "date",         None),
            ("status",        "enum_pick",    {"choices": ["pending", "approved", "rejected"]}),
        ],
    },

    # ── HEALTHCARE ───────────────────────────────────────────────────────────

    "doctors": {
        "description": "Doctor profiles",
        "fields": [
            ("doctor_id",    "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("speciality",   "enum_pick",    {"choices": ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General Medicine", "Dermatology", "Oncology"]}),
            ("email",        "email",        None),
            ("phone",        "phone",        None),
        ],
    },
    "patients": {
        "description": "Patient records",
        "fields": [
            ("patient_id",   "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("date_of_birth","date_of_birth",None),
            ("gender",       "gender",       None),
            ("phone",        "phone",        None),
            ("address",      "address",      None),
            ("blood_group",  "enum_pick",    {"choices": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]}),
        ],
    },
    "appointments": {
        "description": "Doctor-patient appointments",
        "fields": [
            ("appointment_id","primary_key", None),
            ("patient_id",   "foreign_key",  {"references_table": "patients", "references_field": "patient_id"}),
            ("doctor_id",    "foreign_key",  {"references_table": "doctors",  "references_field": "doctor_id"}),
            ("appointment_dt","datetime",    None),
            ("status",       "enum_pick",    {"choices": ["scheduled", "completed", "cancelled", "no_show"]}),
        ],
    },
    "prescriptions": {
        "description": "Prescriptions issued after appointments",
        "fields": [
            ("prescription_id","primary_key",None),
            ("appointment_id","foreign_key",  {"references_table": "appointments", "references_field": "appointment_id"}),
            ("medication",   "product_name", None),
            ("dosage",       "enum_pick",    {"choices": ["5mg", "10mg", "20mg", "50mg", "100mg", "250mg", "500mg"]}),
            ("duration_days","integer",      {"min_value": 1, "max_value": 90}),
        ],
    },

    # ── EDUCATION ────────────────────────────────────────────────────────────

    "courses": {
        "description": "Course catalog",
        "fields": [
            ("course_id",    "primary_key",  None),
            ("course_name",  "product_name", None),
            ("department",   "department",   None),
            ("credits",      "integer",      {"min_value": 1, "max_value": 6}),
            ("semester",     "enum_pick",    {"choices": ["Spring", "Summer", "Fall", "Winter"]}),
        ],
    },
    "students": {
        "description": "Student profiles",
        "fields": [
            ("student_id",   "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("email",        "email",        {"unique": True}),
            ("date_of_birth","date_of_birth",None),
            ("enrollment_year","integer",    {"min_value": 2015, "max_value": 2025}),
        ],
    },
    "enrollments": {
        "description": "Student course enrollments",
        "fields": [
            ("enrollment_id","primary_key",  None),
            ("student_id",   "foreign_key",  {"references_table": "students", "references_field": "student_id"}),
            ("course_id",    "foreign_key",  {"references_table": "courses",  "references_field": "course_id"}),
            ("enrolled_on",  "date",         None),
            ("status",       "enum_pick",    {"choices": ["active", "dropped", "completed"]}),
        ],
    },
    "grades": {
        "description": "Grades per enrollment",
        "fields": [
            ("grade_id",     "primary_key",  None),
            ("enrollment_id","foreign_key",  {"references_table": "enrollments", "references_field": "enrollment_id"}),
            ("grade",        "enum_pick",    {"choices": ["A", "A-", "B+", "B", "B-", "C+", "C", "D", "F"]}),
            ("gpa_points",   "float",        {"min_value": 0.0, "max_value": 4.0}),
            ("graded_on",    "date",         None),
        ],
    },

    # ── BANKING ──────────────────────────────────────────────────────────────

    "bank_customers": {
        "description": "Bank customer profiles",
        "fields": [
            ("customer_id",  "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("email",        "email",        {"unique": True}),
            ("phone",        "phone",        None),
            ("address",      "address",      None),
            ("kyc_status",   "enum_pick",    {"choices": ["pending", "verified", "rejected"]}),
        ],
    },
    "accounts": {
        "description": "Bank accounts",
        "fields": [
            ("account_id",   "primary_key",  None),
            ("customer_id",  "foreign_key",  {"references_table": "bank_customers", "references_field": "customer_id"}),
            ("account_type", "enum_pick",    {"choices": ["savings", "current", "salary", "fixed_deposit"]}),
            ("balance",      "amount",       {"min_value": 0, "max_value": 10000000}),
            ("iban",         "iban",         None),
            ("opened_on",    "date",         None),
            ("status",       "enum_pick",    {"choices": ["active", "dormant", "closed"]}),
        ],
    },
    "transactions": {
        "description": "Account transactions",
        "fields": [
            ("transaction_id","primary_key", None),
            ("account_id",   "foreign_key",  {"references_table": "accounts", "references_field": "account_id"}),
            ("type",         "enum_pick",    {"choices": ["credit", "debit", "transfer", "withdrawal", "deposit"]}),
            ("amount",       "amount",       {"min_value": 1, "max_value": 500000}),
            ("timestamp",    "timestamp",    None),
            ("description",  "slug",         None),
        ],
    },
    "loans": {
        "description": "Loan records",
        "fields": [
            ("loan_id",      "primary_key",  None),
            ("customer_id",  "foreign_key",  {"references_table": "bank_customers", "references_field": "customer_id"}),
            ("loan_type",    "enum_pick",    {"choices": ["home", "personal", "auto", "education", "business"]}),
            ("principal",    "amount",       {"min_value": 10000, "max_value": 10000000}),
            ("interest_rate","float",        {"min_value": 5.0, "max_value": 24.0, "decimal_places": 2}),
            ("tenure_months","integer",      {"min_value": 6, "max_value": 360}),
            ("status",       "enum_pick",    {"choices": ["active", "closed", "defaulted", "pending_approval"]}),
        ],
    },

    # ── LOGISTICS ────────────────────────────────────────────────────────────

    "warehouses": {
        "description": "Warehouse locations",
        "fields": [
            ("warehouse_id", "primary_key",  None),
            ("name",         "company_name", None),
            ("city",         "city",         None),
            ("country",      "country",      None),
            ("capacity",     "integer",      {"min_value": 100, "max_value": 100000}),
        ],
    },
    "drivers": {
        "description": "Delivery drivers",
        "fields": [
            ("driver_id",    "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("phone",        "phone",        None),
            ("license_no",   "employee_id",  None),
            ("status",       "enum_pick",    {"choices": ["available", "on_trip", "off_duty"]}),
        ],
    },
    "shipments": {
        "description": "Shipment records",
        "fields": [
            ("shipment_id",  "primary_key",  None),
            ("warehouse_id", "foreign_key",  {"references_table": "warehouses", "references_field": "warehouse_id"}),
            ("driver_id",    "foreign_key",  {"references_table": "drivers",    "references_field": "driver_id"}),
            ("origin",       "city",         None),
            ("destination",  "city",         None),
            ("weight_kg",    "float",        {"min_value": 0.1, "max_value": 5000}),
            ("status",       "enum_pick",    {"choices": ["pending", "in_transit", "delivered", "returned", "lost"]}),
            ("shipped_on",   "datetime",     None),
        ],
    },
    "deliveries": {
        "description": "Delivery events per shipment",
        "fields": [
            ("delivery_id",  "primary_key",  None),
            ("shipment_id",  "foreign_key",  {"references_table": "shipments", "references_field": "shipment_id"}),
            ("attempted_on", "datetime",     None),
            ("outcome",      "enum_pick",    {"choices": ["delivered", "failed", "rescheduled"]}),
            ("signature",    "full_name",    None),
        ],
    },

    # ── REAL ESTATE ──────────────────────────────────────────────────────────

    "agents": {
        "description": "Real estate agents",
        "fields": [
            ("agent_id",     "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("email",        "email",        None),
            ("phone",        "phone",        None),
            ("agency",       "company_name", None),
        ],
    },
    "properties": {
        "description": "Property listings",
        "fields": [
            ("property_id",  "primary_key",  None),
            ("agent_id",     "foreign_key",  {"references_table": "agents", "references_field": "agent_id"}),
            ("address",      "address",      None),
            ("city",         "city",         None),
            ("price",        "amount",       {"min_value": 500000, "max_value": 100000000}),
            ("bedrooms",     "integer",      {"min_value": 1, "max_value": 10}),
            ("bathrooms",    "integer",      {"min_value": 1, "max_value": 6}),
            ("area_sqft",    "float",        {"min_value": 300, "max_value": 10000}),
            ("type",         "enum_pick",    {"choices": ["apartment", "villa", "plot", "commercial", "studio"]}),
            ("status",       "enum_pick",    {"choices": ["available", "sold", "rented", "under_negotiation"]}),
        ],
    },
    "buyers": {
        "description": "Prospective buyers",
        "fields": [
            ("buyer_id",     "primary_key",  None),
            ("full_name",    "full_name",    None),
            ("email",        "email",        None),
            ("phone",        "phone",        None),
            ("budget",       "amount",       {"min_value": 500000, "max_value": 100000000}),
        ],
    },
    "property_transactions": {
        "description": "Property sale / rental transactions",
        "fields": [
            ("txn_id",       "primary_key",  None),
            ("property_id",  "foreign_key",  {"references_table": "properties", "references_field": "property_id"}),
            ("buyer_id",     "foreign_key",  {"references_table": "buyers",     "references_field": "buyer_id"}),
            ("agent_id",     "foreign_key",  {"references_table": "agents",     "references_field": "agent_id"}),
            ("txn_type",     "enum_pick",    {"choices": ["sale", "rental"]}),
            ("amount",       "amount",       {"min_value": 500000, "max_value": 100000000}),
            ("txn_date",     "date",         None),
        ],
    },

    # ── IOT ──────────────────────────────────────────────────────────────────

    "devices": {
        "description": "IoT device registry",
        "fields": [
            ("device_id",    "primary_key",  None),
            ("device_name",  "slug",         None),
            ("type",         "enum_pick",    {"choices": ["temperature_sensor", "humidity_sensor", "pressure_sensor", "motion_detector", "smart_meter"]}),
            ("location",     "city",         None),
            ("ip_address",   "ip_address",   None),
            ("mac_address",  "mac_address",  None),
            ("status",       "enum_pick",    {"choices": ["active", "inactive", "maintenance"]}),
        ],
    },
    "sensor_readings": {
        "description": "Time-series sensor readings",
        "fields": [
            ("reading_id",   "primary_key",  None),
            ("device_id",    "foreign_key",  {"references_table": "devices", "references_field": "device_id"}),
            ("timestamp",    "timestamp",    None),
            ("temperature",  "float",        {"min_value": -30.0, "max_value": 80.0, "decimal_places": 2}),
            ("humidity",     "float",        {"min_value": 0.0,   "max_value": 100.0}),
            ("pressure",     "float",        {"min_value": 900.0, "max_value": 1100.0}),
        ],
    },
    "alerts": {
        "description": "Device alerts and anomalies",
        "fields": [
            ("alert_id",     "primary_key",  None),
            ("device_id",    "foreign_key",  {"references_table": "devices", "references_field": "device_id"}),
            ("alert_type",   "enum_pick",    {"choices": ["threshold_breach", "device_offline", "battery_low", "anomaly_detected"]}),
            ("severity",     "enum_pick",    {"choices": ["low", "medium", "high", "critical"]}),
            ("triggered_at", "timestamp",    None),
            ("resolved",     "boolean",      None),
        ],
    },

    # ── SOCIAL MEDIA ─────────────────────────────────────────────────────────

    "sm_users": {
        "description": "Social media user profiles",
        "fields": [
            ("user_id",      "primary_key",  None),
            ("username",     "username",     {"unique": True}),
            ("email",        "email",        {"unique": True}),
            ("full_name",    "full_name",    None),
            ("joined_on",    "date",         None),
            ("followers",    "integer",      {"min_value": 0, "max_value": 1000000}),
            ("following",    "integer",      {"min_value": 0, "max_value": 5000}),
            ("verified",     "boolean",      None),
        ],
    },
    "posts": {
        "description": "User posts",
        "fields": [
            ("post_id",      "primary_key",  None),
            ("user_id",      "foreign_key",  {"references_table": "sm_users", "references_field": "user_id"}),
            ("platform",     "enum_pick",    {"choices": ["twitter", "instagram", "facebook", "linkedin", "threads"]}),
            ("likes",        "integer",      {"min_value": 0, "max_value": 500000}),
            ("shares",       "integer",      {"min_value": 0, "max_value": 100000}),
            ("posted_at",    "timestamp",    None),
        ],
    },
    "comments": {
        "description": "Comments on posts",
        "fields": [
            ("comment_id",   "primary_key",  None),
            ("post_id",      "foreign_key",  {"references_table": "posts",    "references_field": "post_id"}),
            ("user_id",      "foreign_key",  {"references_table": "sm_users", "references_field": "user_id"}),
            ("likes",        "integer",      {"min_value": 0, "max_value": 10000}),
            ("commented_at", "timestamp",    None),
        ],
    },
    "likes": {
        "description": "Post likes",
        "fields": [
            ("like_id",      "primary_key",  None),
            ("post_id",      "foreign_key",  {"references_table": "posts",    "references_field": "post_id"}),
            ("user_id",      "foreign_key",  {"references_table": "sm_users", "references_field": "user_id"}),
            ("liked_at",     "timestamp",    None),
        ],
    },

    # ── AVIATION ─────────────────────────────────────────────────────────────

    "pilots": {
        "description": "Pilot profiles",
        "fields": [
            ("pilot_id",         "primary_key",  None),
            ("full_name",        "full_name",    None),
            ("license_number",   "employee_id",  {"unique": True}),
            ("email",            "email",        None),
            ("phone",            "phone",        None),
            ("total_flight_hrs", "float",        {"min_value": 200, "max_value": 30000}),
        ],
    },
    "aircraft": {
        "description": "Aircraft registry",
        "fields": [
            ("aircraft_id",  "primary_key",  None),
            ("tail_number",  "sku",          {"unique": True}),
            ("type",         "enum_pick",    {"choices": ["Boeing 737", "Airbus A320", "ATR 72", "Cessna 172", "Boeing 777", "Airbus A380"]}),
            ("capacity",     "integer",      {"min_value": 4, "max_value": 600}),
            ("status",       "enum_pick",    {"choices": ["active", "maintenance", "retired"]}),
        ],
    },
    "flights": {
        "description": "Flight records",
        "fields": [
            ("flight_id",        "primary_key",  None),
            ("pilot_id",         "foreign_key",  {"references_table": "pilots",   "references_field": "pilot_id"}),
            ("aircraft_id",      "foreign_key",  {"references_table": "aircraft", "references_field": "aircraft_id"}),
            ("flight_number",    "sku",          None),
            ("departure_airport","enum_pick",    {"choices": ["DEL", "BOM", "BLR", "HYD", "MAA", "CCU", "JFK", "LHR", "DXB", "SIN"]}),
            ("arrival_airport",  "enum_pick",    {"choices": ["DEL", "BOM", "BLR", "HYD", "MAA", "CCU", "JFK", "LHR", "DXB", "SIN"]}),
            ("departure_dt",     "datetime",     None),
            ("arrival_dt",       "datetime",     None),
            ("passenger_count",  "integer",      {"min_value": 1, "max_value": 600}),
            ("status",           "enum_pick",    {"choices": ["scheduled", "departed", "arrived", "cancelled", "diverted"]}),
        ],
    },
    "pilot_log_book": {
        "description": "Pilot flight log entries",
        "fields": [
            ("log_id",           "primary_key",  None),
            ("pilot_id",         "foreign_key",  {"references_table": "pilots",  "references_field": "pilot_id"}),
            ("flight_id",        "foreign_key",  {"references_table": "flights", "references_field": "flight_id"}),
            ("role",             "enum_pick",    {"choices": ["Captain", "First Officer", "Second Officer"]}),
            ("flight_time_hrs",  "float",        {"min_value": 0.5, "max_value": 18.0}),
            ("night_flight",     "boolean",      None),
            ("weather_conditions","enum_pick",   {"choices": ["Clear", "Partly Cloudy", "Overcast", "Rain", "Thunderstorm", "Fog", "Snow"]}),
            ("fuel_consumed_kg", "float",        {"min_value": 100, "max_value": 80000}),
            ("remarks",          "enum_pick",    {"choices": ["Normal", "Turbulence encountered", "Diverted", "Medical emergency", "Bird strike", "Delay"]}),
        ],
    },

    # ── WEATHER ──────────────────────────────────────────────────────────────

    "weather_stations": {
        "description": "Weather monitoring stations",
        "fields": [
            ("station_id",   "primary_key",  None),
            ("station_name", "slug",         None),
            ("city",         "city",         None),
            ("country",      "country",      None),
            ("latitude",     "float",        {"min_value": -90.0,  "max_value": 90.0,  "decimal_places": 4}),
            ("longitude",    "float",        {"min_value": -180.0, "max_value": 180.0, "decimal_places": 4}),
        ],
    },
    "observations": {
        "description": "Weather observations from stations",
        "fields": [
            ("observation_id",   "primary_key",  None),
            ("station_id",       "foreign_key",  {"references_table": "weather_stations", "references_field": "station_id"}),
            ("observed_at",      "timestamp",    None),
            ("temperature_c",    "float",        {"min_value": -50.0, "max_value": 60.0}),
            ("humidity_percent", "float",        {"min_value": 0.0,   "max_value": 100.0}),
            ("pressure_mb",      "float",        {"min_value": 900.0, "max_value": 1100.0}),
            ("wind_speed_kmh",   "float",        {"min_value": 0.0,   "max_value": 300.0}),
            ("wind_direction",   "enum_pick",    {"choices": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]}),
            ("precipitation_mm", "float",        {"min_value": 0.0,   "max_value": 500.0}),
            ("condition",        "enum_pick",    {"choices": ["Clear", "Cloudy", "Rain", "Snow", "Thunderstorm", "Fog", "Hail"]}),
        ],
    },
    "forecasts": {
        "description": "Weather forecasts per station",
        "fields": [
            ("forecast_id",      "primary_key",  None),
            ("station_id",       "foreign_key",  {"references_table": "weather_stations", "references_field": "station_id"}),
            ("forecast_date",    "date",         None),
            ("min_temp_c",       "float",        {"min_value": -50.0, "max_value": 60.0}),
            ("max_temp_c",       "float",        {"min_value": -50.0, "max_value": 60.0}),
            ("condition",        "enum_pick",    {"choices": ["Clear", "Cloudy", "Rain", "Snow", "Thunderstorm", "Fog"]}),
            ("confidence_pct",   "float",        {"min_value": 50.0,  "max_value": 99.0}),
        ],
    },
}


# ---------------------------------------------------------------------------
# 4. Predefined Relational Sets
#    Defines the order of table generation + explicit FK wiring.
#    "tables" order matters — parent tables must come before child tables.
# ---------------------------------------------------------------------------

RELATIONAL_SETS = {
    "ecommerce_full": {
        "description": "Full e-commerce schema: customers → products → orders → order_items → reviews",
        "tables": ["customers", "products", "categories", "orders", "order_items", "reviews"],
        "relations": [
            {"parent": "customers", "parent_field": "customer_id",
             "child": "orders",      "child_field": "customer_id"},
            {"parent": "products",  "parent_field": "product_id",
             "child": "order_items","child_field": "product_id"},
            {"parent": "orders",    "parent_field": "order_id",
             "child": "order_items","child_field": "order_id"},
            {"parent": "products",  "parent_field": "product_id",
             "child": "reviews",    "child_field": "product_id"},
            {"parent": "customers", "parent_field": "customer_id",
             "child": "reviews",    "child_field": "customer_id"},
        ],
    },
    "hr_full": {
        "description": "HR schema: departments → employees → payroll / leave_requests",
        "tables": ["departments", "employees", "payroll", "leave_requests"],
        "relations": [
            {"parent": "departments","parent_field": "department_id",
             "child": "employees",   "child_field": "department_id"},
            {"parent": "employees",  "parent_field": "employee_id",
             "child": "payroll",     "child_field": "employee_id"},
            {"parent": "employees",  "parent_field": "employee_id",
             "child": "leave_requests","child_field": "employee_id"},
        ],
    },
    "healthcare_full": {
        "description": "Healthcare schema: doctors + patients → appointments → prescriptions",
        "tables": ["doctors", "patients", "appointments", "prescriptions"],
        "relations": [
            {"parent": "patients",      "parent_field": "patient_id",
             "child": "appointments",   "child_field": "patient_id"},
            {"parent": "doctors",       "parent_field": "doctor_id",
             "child": "appointments",   "child_field": "doctor_id"},
            {"parent": "appointments",  "parent_field": "appointment_id",
             "child": "prescriptions",  "child_field": "appointment_id"},
        ],
    },
    "education_full": {
        "description": "Education schema: courses + students → enrollments → grades",
        "tables": ["courses", "students", "enrollments", "grades"],
        "relations": [
            {"parent": "students",    "parent_field": "student_id",
             "child": "enrollments",  "child_field": "student_id"},
            {"parent": "courses",     "parent_field": "course_id",
             "child": "enrollments",  "child_field": "course_id"},
            {"parent": "enrollments", "parent_field": "enrollment_id",
             "child": "grades",       "child_field": "enrollment_id"},
        ],
    },
    "banking_full": {
        "description": "Banking schema: bank_customers → accounts → transactions / loans",
        "tables": ["bank_customers", "accounts", "transactions", "loans"],
        "relations": [
            {"parent": "bank_customers","parent_field": "customer_id",
             "child": "accounts",       "child_field": "customer_id"},
            {"parent": "accounts",      "parent_field": "account_id",
             "child": "transactions",   "child_field": "account_id"},
            {"parent": "bank_customers","parent_field": "customer_id",
             "child": "loans",          "child_field": "customer_id"},
        ],
    },
    "logistics_full": {
        "description": "Logistics schema: warehouses + drivers → shipments → deliveries",
        "tables": ["warehouses", "drivers", "shipments", "deliveries"],
        "relations": [
            {"parent": "warehouses", "parent_field": "warehouse_id",
             "child": "shipments",   "child_field": "warehouse_id"},
            {"parent": "drivers",    "parent_field": "driver_id",
             "child": "shipments",   "child_field": "driver_id"},
            {"parent": "shipments",  "parent_field": "shipment_id",
             "child": "deliveries",  "child_field": "shipment_id"},
        ],
    },
    "real_estate_full": {
        "description": "Real estate schema: agents → properties + buyers → property_transactions",
        "tables": ["agents", "properties", "buyers", "property_transactions"],
        "relations": [
            {"parent": "agents",      "parent_field": "agent_id",
             "child": "properties",   "child_field": "agent_id"},
            {"parent": "properties",  "parent_field": "property_id",
             "child": "property_transactions","child_field": "property_id"},
            {"parent": "buyers",      "parent_field": "buyer_id",
             "child": "property_transactions","child_field": "buyer_id"},
            {"parent": "agents",      "parent_field": "agent_id",
             "child": "property_transactions","child_field": "agent_id"},
        ],
    },
    "iot_full": {
        "description": "IoT schema: devices → sensor_readings + alerts",
        "tables": ["devices", "sensor_readings", "alerts"],
        "relations": [
            {"parent": "devices",         "parent_field": "device_id",
             "child": "sensor_readings",  "child_field": "device_id"},
            {"parent": "devices",         "parent_field": "device_id",
             "child": "alerts",           "child_field": "device_id"},
        ],
    },
    "social_media_full": {
        "description": "Social media schema: sm_users → posts → comments + likes",
        "tables": ["sm_users", "posts", "comments", "likes"],
        "relations": [
            {"parent": "sm_users", "parent_field": "user_id",
             "child": "posts",     "child_field": "user_id"},
            {"parent": "posts",    "parent_field": "post_id",
             "child": "comments",  "child_field": "post_id"},
            {"parent": "sm_users", "parent_field": "user_id",
             "child": "comments",  "child_field": "user_id"},
            {"parent": "posts",    "parent_field": "post_id",
             "child": "likes",     "child_field": "post_id"},
            {"parent": "sm_users", "parent_field": "user_id",
             "child": "likes",     "child_field": "user_id"},
        ],
    },
    "aviation_full": {
        "description": "Aviation schema: pilots + aircraft → flights → pilot_log_book",
        "tables": ["pilots", "aircraft", "flights", "pilot_log_book"],
        "relations": [
            {"parent": "pilots",   "parent_field": "pilot_id",
             "child": "flights",   "child_field": "pilot_id"},
            {"parent": "aircraft", "parent_field": "aircraft_id",
             "child": "flights",   "child_field": "aircraft_id"},
            {"parent": "pilots",   "parent_field": "pilot_id",
             "child": "pilot_log_book","child_field": "pilot_id"},
            {"parent": "flights",  "parent_field": "flight_id",
             "child": "pilot_log_book","child_field": "flight_id"},
        ],
    },
    "weather_full": {
        "description": "Weather schema: weather_stations → observations + forecasts",
        "tables": ["weather_stations", "observations", "forecasts"],
        "relations": [
            {"parent": "weather_stations","parent_field": "station_id",
             "child": "observations",     "child_field": "station_id"},
            {"parent": "weather_stations","parent_field": "station_id",
             "child": "forecasts",        "child_field": "station_id"},
        ],
    },
}


# ---------------------------------------------------------------------------
# 5. Backward-compatible PREDEFINED_TOPICS
#    Auto-built so old /topics endpoint still works without changes.
# ---------------------------------------------------------------------------

PREDEFINED_TOPICS = {
    table_name: {
        "description": table_def["description"],
        "fields": [f[0] for f in table_def["fields"]],
    }
    for table_name, table_def in TABLE_DEFINITIONS.items()
}


# ---------------------------------------------------------------------------
# 6. DB default ports
# ---------------------------------------------------------------------------

DB_DEFAULT_PORTS = {
    "postgresql": 5432,
    "mysql":      3306,
    "sqlite":     None,   # file-based
    "mssql":      1433,
}


# ---------------------------------------------------------------------------
# 7. Field type → human readable label (for frontend dropdowns)
# ---------------------------------------------------------------------------

FIELD_TYPE_LABELS = {
    "primary_key":   "Primary Key (auto)",
    "foreign_key":   "Foreign Key",
    "first_name":    "First Name",
    "last_name":     "Last Name",
    "full_name":     "Full Name",
    "email":         "Email Address",
    "phone":         "Phone Number",
    "date_of_birth": "Date of Birth",
    "gender":        "Gender",
    "address":       "Street Address",
    "city":          "City",
    "state":         "State / Province",
    "country":       "Country",
    "zip_code":      "ZIP / Postal Code",
    "integer":       "Integer",
    "float":         "Decimal Number",
    "boolean":       "Boolean (true/false)",
    "uuid":          "UUID",
    "slug":          "Slug / Code",
    "username":      "Username",
    "password_hash": "Password Hash (bcrypt)",
    "url":           "URL",
    "ip_address":    "IP Address",
    "mac_address":   "MAC Address",
    "color_hex":     "Color (Hex)",
    "date":          "Date",
    "datetime":      "Date & Time",
    "time":          "Time",
    "timestamp":     "Timestamp (Unix)",
    "currency_code": "Currency Code",
    "amount":        "Monetary Amount",
    "iban":          "IBAN",
    "credit_card":   "Credit Card (masked)",
    "product_name":  "Product Name",
    "category":      "Category",
    "sku":           "SKU / Code",
    "price":         "Price",
    "rating":        "Rating (1–5)",
    "company_name":  "Company Name",
    "job_title":     "Job Title",
    "department":    "Department",
    "employee_id":   "Employee ID",
    "salary":        "Salary",
    "status":        "Status (random)",
    "enum_pick":     "Pick from List",
}