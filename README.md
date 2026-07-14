# ⬡ MockForge

**Realistic mock data generator for developers and QA engineers.**  
Generate structured, relational, domain-aware fake data — preview it, download it, or seed it directly into your database.

---

## What it does

MockForge lets you generate production-quality mock data without writing a single line of code.

- **Quick Generate** — Pick a topic, format, and record count. Get data instantly.
- **By Domain** — Generate all tables for a real-world domain (e-commerce, HR, healthcare, and more) with a single click.
- **Relational Sets** — Predefined table bundles with foreign key integrity built-in. Orders always link to real customers. Appointments always link to real doctors.
- **Schema Builder** — Define your own tables and fields from scratch. Link them with foreign keys. Generate data that matches your exact schema.
- **DB Seeder** — Connect to your dev or UAT database and seed data directly. No CSV import needed.

---

## Domains

| Domain | Tables |
|---|---|
| E-commerce | customers, products, categories, orders, order_items, reviews |
| HR | departments, employees, payroll, leave_requests |
| Healthcare | doctors, patients, appointments, prescriptions |
| Education | courses, students, enrollments, grades |
| Banking | bank_customers, accounts, transactions, loans |
| Logistics | warehouses, drivers, shipments, deliveries |
| Real Estate | agents, properties, buyers, property_transactions |
| IoT | devices, sensor_readings, alerts |
| Social Media | sm_users, posts, comments, likes |
| Aviation | pilots, aircraft, flights, pilot_log_book |
| Weather | weather_stations, observations, forecasts |

---

## Output Formats

`JSON` `CSV` `TSV` `YAML` `XML` `Parquet`

Multi-table exports (domain, relational sets, schema) are packaged as a ZIP archive when using CSV, TSV, or Parquet.

---

## Database Seeding

MockForge can seed data directly into your database.

**Supported databases:** PostgreSQL · MySQL · SQLite · MSSQL

> ⚠️ Only connect dev or UAT databases. MockForge does not store, log, or persist your credentials. They are used only during the request and discarded immediately after.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.10+, FastAPI, Pydantic v2 |
| Data Generation | Faker, Pandas |
| Database Seeding | SQLAlchemy, psycopg2, PyMySQL |
| Formats | PyYAML, PyArrow (Parquet), lxml |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Runner | Uvicorn |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/MockForge.git
cd MockForge
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python run.py
```

This starts both the backend API and the frontend server.

| Service | URL |
|---|---|
| Frontend UI | http://localhost:8080 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (Redoc) | http://localhost:8000/redoc |

---

## Project Structure

```
MockForge/
├── backend/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── services/
│   │   ├── data_generator.py    # Core generation engine
│   │   ├── format_converter.py  # JSON, CSV, YAML, XML, Parquet conversion
│   │   └── db_seeder.py         # Database seeding via SQLAlchemy
│   └── utils/
│       ├── constants.py         # Domain definitions, table schemas, relational sets
│       └── validator.py         # Schema validation + content safety
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── run.py                       # One-command startup
└── requirements.txt
```

---

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/topics` | List all available topics |
| GET | `/domains` | List all domains with table info |
| GET | `/relational-sets` | List predefined relational bundles |
| GET | `/field-types` | List allowed field types for schema builder |
| GET | `/formats` | List supported output formats |

### Generate (returns data in response)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/generate` | Single topic (backward-compatible) |
| POST | `/generate/domain` | All tables for a domain |
| POST | `/generate/relational-set` | Predefined relational bundle |
| POST | `/generate/schema` | User-defined schema |

### Download (returns file)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/download` | Single topic file download |
| POST | `/download/domain` | Domain data as file/ZIP |
| POST | `/download/relational-set` | Relational set as file/ZIP |
| POST | `/download/schema` | Schema-driven data as file/ZIP |

### Database Seeding

| Method | Endpoint | Description |
|---|---|---|
| POST | `/db/test` | Test database connectivity |
| POST | `/db/seed/schema` | Seed from user-defined schema |
| POST | `/db/seed/domain` | Seed from domain |
| POST | `/db/seed/relational-set` | Seed from predefined relational set |

Full interactive docs available at `/docs` when the server is running.

---

## Content Safety

MockForge includes a validation layer that blocks explicit, harmful, or sensitive field names and table names before any data is generated. Schema-driven generation uses a strict field type whitelist — free-form text fields are not supported by design.

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

**Chirag Gupta**  
[LinkedIn](https://linkedin.com/in/chirag1706gupta) · chirag1706gupta@gmail.com · Jaipur, Rajasthan, India