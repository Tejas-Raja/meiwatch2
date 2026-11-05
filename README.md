# MeiWatch2.0 — Factory Operations Monitoring System

A Python-based factory operations monitoring system that simulates industrial equipment sensor readings, stores them in PostgreSQL, detects abnormal readings, generates alerts, and exposes monitoring data through a REST API.

The project demonstrates backend development, database design, SQL analytics, automated testing, and containerized deployment.

## Features

- **Sensor simulation:** Generates synthetic readings for machines, transformers, and switchgear.
- **Data validation:** Uses pandas to validate incoming readings and reject malformed or duplicate records.
- **Database management:** Stores equipment, sensor definitions, readings, and alerts in PostgreSQL using SQLAlchemy.
- **Database migrations:** Uses Alembic to manage schema changes.
- **Anomaly detection:** Identifies readings outside configured normal operating ranges.
- **Alert management:** Generates alerts with severity levels and supports status updates.
- **SQL analytics:** Provides equipment summaries, sensor statistics, alert summaries, and equipment health information.
- **REST API:** Exposes monitoring functionality through FastAPI.
- **Containerization:** Uses Docker Compose to run the API and PostgreSQL database.
- **Automated testing:** Uses pytest for unit and API integration tests.

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
| Testing | pytest, HTTPX |
| Containerization | Docker, Docker Compose |
| Version control | Git |

## Architecture

```text
                  Sensor Generator
                        |
                        v
                 Data Validation
                     (pandas)
                        |
                        v
                  PostgreSQL
                        |
             +----------+----------+
             |          |          |
             v          v          v
       Anomaly       SQL        Equipment
       Detection   Analytics     Data
             |
             v
        Alert Service
             |
             v
          FastAPI
             |
             v
       REST API Clients
```

## Project Structure

```text
meiwatch2/
├── migrations/             # Alembic migration files
├── scripts/                # Data ingestion and utility scripts
├── src/
│   └── meiwatch/
│       ├── routers/        # FastAPI route modules
│       ├── equipment.py    # Equipment and sensor definitions
│       ├── sensor_generator.py
│       ├── data_processor.py
│       ├── database.py
│       ├── models.py
│       ├── seed.py
│       ├── repository.py
│       ├── anomaly_detector.py
│       ├── alert_service.py
│       ├── analytics.py
│       ├── schemas.py
│       └── main.py
├── tests/                  # Automated tests
├── Dockerfile
├── compose.yaml
├── alembic.ini
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone <repository-url>
cd meiwatch2
```

### 2. Configure environment variables

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the PostgreSQL credentials.

Do not commit your `.env` file to version control.

### 3. Start the application

```bash
docker compose up --build -d
```

Docker Compose starts the PostgreSQL database and FastAPI application.

On application startup:

1. Alembic applies pending database migrations.
2. The seed script inserts the initial equipment and sensor definitions.
3. Uvicorn starts the FastAPI application.

### 4. Verify the deployment

Check container status:

```bash
docker compose ps
```

Check application logs:

```bash
docker compose logs app
```

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

The anomaly detector compares stored readings against these ranges. Abnormal readings can generate alerts with one of four severity levels:

- Low
- Medium
- High
- Critical

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
- REST API endpoints and error handling

## Useful Docker Commands

```bash
# Start services
docker compose up -d

# Rebuild and start services
docker compose up --build -d

# View logs
docker compose logs -f

# View application logs
docker compose logs -f app

# Open a PostgreSQL shell
docker compose exec db psql -U meiwatch -d meiwatch_db

# Stop services without deleting database data
docker compose down
```

## Limitations

- Sensor readings are synthetically generated.
- Equipment operating ranges and alert thresholds are illustrative.
- The project does not implement authentication or role-based access control.
- The equipment health classification is a simplified monitoring indicator, not a complete industrial condition assessment.
- The API is intended as a demonstration project rather than a production industrial monitoring platform.

## Future Improvements

- Interactive monitoring dashboard using Streamlit.
- Configurable sensor generation and ingestion intervals.
- Real-time sensor ingestion.
- Historical trend visualization.
- Alert acknowledgement and resolution history.
- Authentication and authorization.
- Improved equipment health scoring.