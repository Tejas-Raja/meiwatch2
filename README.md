# MeiWatch2.0 — Factory Operations Monitoring System

A Python-based factory operations monitoring system that simulates industrial equipment sensor readings, validates and stores them in PostgreSQL, detects abnormal readings, generates alerts, and exposes monitoring data through a REST API.

The project demonstrates backend development, database design, SQL analytics, automated testing, background processing, and containerized deployment.

## Features

- **Sensor simulation:** Generates synthetic readings for machines, transformers, and switchgear.
- **Automated ingestion:** Runs a background worker that periodically generates, validates, and stores sensor readings.
- **Data validation:** Uses pandas to validate incoming readings and reject malformed or duplicate records.
- **Database management:** Stores equipment, sensor definitions, readings, and alerts in PostgreSQL using SQLAlchemy.
- **Database migrations:** Uses Alembic to manage schema changes.
- **Anomaly detection:** Identifies readings outside configured normal operating ranges.
- **Automated alerts:** Generates alerts for abnormal readings with severity levels and prevents duplicate alerts.
- **Alert management:** Supports alert status updates through the REST API.
- **SQL analytics:** Provides equipment summaries, sensor statistics, alert summaries, and equipment health information.
- **REST API:** Exposes monitoring functionality through FastAPI.
- **Containerization:** Uses Docker Compose to run the API, PostgreSQL database, and ingestion worker as separate services.
- **Automated testing:** Uses pytest for unit, service, and API integration tests.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| API | FastAPI |
| Data processing | pandas |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic |
| Background processing | Python threading and signal handling |
| Testing | pytest, HTTPX |
| Containerization | Docker, Docker Compose |
| Version control | Git |

## Architecture

```text
                 Docker Compose
                       |
          +------------+------------+
          |            |            |
          v            v            v
       FastAPI     PostgreSQL    Ingestion
       Service      Database      Worker
          |            ^            |
          |            |            v
          |            |      Sensor Generator
          |            |            |
          |            |            v
          |            |      Data Validation
          |            |         (pandas)
          |            |            |
          |            +------------+
          |                 |
          |                 v
          |           Alert Service
          |                 |
          +-----------------+
                    |
                    v
              REST API Clients

       PostgreSQL also stores equipment,
       sensor definitions, readings and alerts.
```

The ingestion worker operates independently of the FastAPI application. It periodically generates sensor readings, validates them, inserts valid records into PostgreSQL, and generates alerts for abnormal readings.

The FastAPI application provides access to the stored monitoring data through REST endpoints.

## Project Structure

```text
meiwatch2/
├── migrations/                  # Alembic migration files
├── scripts/                     # Data ingestion and utility scripts
│   ├── ingest_readings.py
│   └── generate_alerts.py
├── src/
│   └── meiwatch/
│       ├── routers/             # FastAPI route modules
│       ├── equipment.py         # Equipment and sensor definitions
│       ├── sensor_generator.py  # Synthetic sensor data generation
│       ├── data_processor.py    # Reading validation
│       ├── ingestion.py         # Single ingestion cycle
│       ├── worker.py            # Continuous ingestion worker
│       ├── database.py          # Database configuration
│       ├── models.py            # SQLAlchemy models
│       ├── seed.py               # Initial equipment and sensor data
│       ├── repository.py        # Database operations
│       ├── anomaly_detector.py  # Anomaly detection
│       ├── alert_service.py     # Alert generation
│       ├── analytics.py         # SQL analytics
│       ├── schemas.py           # Pydantic schemas
│       └── main.py              # FastAPI application
├── tests/                       # Automated tests
├── Dockerfile
├── compose.yaml
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Tejas-Raja/meiwatch2
cd meiwatch2
```

### 2. Configure environment variables

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the PostgreSQL credentials and ingestion settings.

Example configuration:

```env
POSTGRES_DB=meiwatch_db
POSTGRES_USER=meiwatch
POSTGRES_PASSWORD=change_this_local_password

DATABASE_URL=postgresql+psycopg://meiwatch:change_this_local_password@localhost:5432/meiwatch_db

INGESTION_INTERVAL_SECONDS=10
ANOMALY_PROBABILITY=0.05
```

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_DB` | PostgreSQL database name | `meiwatch_db` |
| `POSTGRES_USER` | PostgreSQL username | `meiwatch` |
| `POSTGRES_PASSWORD` | PostgreSQL password | User-configured |
| `DATABASE_URL` | Database connection URL | User-configured |
| `INGESTION_INTERVAL_SECONDS` | Time between ingestion cycles | `10` |
| `ANOMALY_PROBABILITY` | Probability of generating an abnormal sensor reading | `0.05` |

The ingestion worker reads its configuration from environment variables.

For example, setting `INGESTION_INTERVAL_SECONDS=5` runs an ingestion cycle every five seconds.

Increasing `ANOMALY_PROBABILITY` generates abnormal readings more frequently, which is useful for testing alert generation.

Do not commit your `.env` file to version control.

### 3. Start the application

```bash
docker compose up --build -d
```

Docker Compose starts three services:

1. **PostgreSQL:** Stores equipment, sensor definitions, readings, and alerts.
2. **FastAPI:** Provides the REST API and applies database migrations during startup.
3. **Ingestion Worker:** Periodically generates and processes sensor readings.

On application startup:

1. PostgreSQL becomes healthy.
2. Alembic applies pending database migrations.
3. The seed script inserts the initial equipment and sensor definitions.
4. Uvicorn starts the FastAPI application.
5. The ingestion worker starts generating sensor readings.

The worker waits for the API service to become healthy before starting, ensuring that database initialization has completed.

### 4. Verify the deployment

Check container status:

```bash
docker compose ps
```

All three services should be running.

Check application logs:

```bash
docker compose logs -f app
```

Check ingestion worker logs:

```bash
docker compose logs -f worker
```

The worker logs include ingestion summaries containing:

- Generated readings
- Valid readings
- Rejected readings
- Inserted readings
- Generated alerts

The application should be available at:

- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

To stop the containers:

```bash
docker compose down
```

PostgreSQL data is stored in a persistent Docker volume and is retained when containers are stopped or recreated.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Application and database health |
| GET | `/equipment/` | List all equipment |
| GET | `/equipment/{equipment_id}` | Retrieve equipment details |
| GET | `/readings` | List sensor readings |
| GET | `/readings/{reading_id}` | Retrieve a specific reading |
| GET | `/equipment/{equipment_id}/readings` | Retrieve readings for equipment |
| GET | `/alerts/` | List alerts |
| GET | `/alerts/{alert_id}` | Retrieve a specific alert |
| PATCH | `/alerts/{alert_id}` | Update alert status |
| GET | `/analytics/equipment` | Equipment summary |
| GET | `/analytics/sensors` | Sensor statistics |
| GET | `/analytics/alerts` | Alert summary |
| GET | `/analytics/health` | Equipment health summary |

The readings endpoint supports pagination and equipment filtering. The alerts endpoint supports status and severity filtering.

Interactive API documentation is available through Swagger UI at `/docs`.

## Sensor Data and Alerts

The system simulates readings for seven equipment assets across three categories:

- Machines
- Transformers
- Switchgear

Each asset has multiple sensor definitions with configured normal operating ranges.

The ingestion pipeline processes sensor data through the following stages:

1. Generate synthetic sensor readings.
2. Validate readings using pandas.
3. Reject malformed, invalid, or duplicate records.
4. Insert valid readings into PostgreSQL.
5. Identify abnormal readings.
6. Generate alerts for readings outside their normal operating ranges.

Alerts are assigned one of four severity levels:

- Low
- Medium
- High
- Critical

The alert service avoids generating duplicate alerts for readings that already have an associated alert.

These thresholds and operating ranges are synthetic demonstration values. They are not manufacturer specifications or industrial safety standards.

## Running Tests

The project uses pytest for automated testing.

With the development dependencies installed, run:

```bash
python -m pytest -v
```

The test suite covers:

- Equipment definitions
- Sensor generation
- Data validation
- Alert generation and severity calculation
- SQL analytics
- Ingestion service orchestration
- Ingestion error handling and logging
- Worker recovery and shutdown behavior
- REST API endpoints and error handling

## Useful Docker Commands

```bash
# Start services
docker compose up -d

# Rebuild and start services
docker compose up --build -d

# View all service logs
docker compose logs -f

# View application logs
docker compose logs -f app

# View ingestion worker logs
docker compose logs -f worker

# Check container status
docker compose ps

# Open a PostgreSQL shell
docker compose exec db psql -U meiwatch -d meiwatch_db

# Count stored sensor readings
docker compose exec db psql -U meiwatch -d meiwatch_db -c "SELECT COUNT(*) FROM sensor_readings;"

# Stop services without deleting database data
docker compose down
```

## Limitations

- Sensor readings are synthetically generated.
- Equipment operating ranges and alert thresholds are illustrative.
- The project does not implement authentication or role-based access control.
- The equipment health classification is a simplified monitoring indicator, not a complete industrial condition assessment.
- The ingestion worker currently uses periodic polling rather than a message broker or streaming platform.
- The API is intended as a demonstration project rather than a production industrial monitoring platform.

## Future Improvements

- Interactive monitoring dashboard using Streamlit.
- Real industrial sensor integration.
- Historical trend visualization.
- Alert acknowledgement and resolution history.
- Authentication and authorization.
- Improved equipment health scoring.
- Database retention policies and performance optimization.
- Message broker integration for scalable sensor ingestion.