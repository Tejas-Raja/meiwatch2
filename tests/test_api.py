from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from meiwatch.database import Base, get_db
from meiwatch.main import app
from meiwatch.models import (
    EquipmentModel,
    SensorDefinitionModel,
    SensorReadingModel,
    AlertModel,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_data(db_session):
    # Create equipment.
    machine = EquipmentModel(
        equipment_id="CNC-TEST",
        name="Test CNC Machine",
        category="machine",
        location="Test Hall",
    )

    transformer = EquipmentModel(
        equipment_id="TRF-TEST",
        name="Test Transformer",
        category="transformer",
        location="Electrical Room",
    )

    switchgear = EquipmentModel(
        equipment_id="SWG-TEST",
        name="Test Switchgear",
        category="switchgear",
        location="Electrical Room",
    )

    # Create sensor definitions.
    temperature = SensorDefinitionModel(
        sensor_name="temperature",
        unit="°C",
        normal_min=40,
        normal_max=90,
    )

    vibration = SensorDefinitionModel(
        sensor_name="vibration",
        unit="mm/s",
        normal_min=0.5,
        normal_max=4.0,
    )

    oil_temperature = SensorDefinitionModel(
        sensor_name="oil_temperature",
        unit="°C",
        normal_min=30,
        normal_max=75,
    )

    current = SensorDefinitionModel(
        sensor_name="current",
        unit="A",
        normal_min=50,
        normal_max=400,
    )

    machine.sensors.extend([temperature, vibration])
    transformer.sensors.append(oil_temperature)
    switchgear.sensors.append(current)

    db_session.add_all([machine, transformer, switchgear])
    db_session.flush()

    # Create readings.
    readings = [
        SensorReadingModel(
            sensor=temperature,
            value=50,
            recorded_at=datetime.now(timezone.utc),
        ),
        SensorReadingModel(
            sensor=temperature,
            value=100,
            recorded_at=datetime.now(timezone.utc),
        ),
        SensorReadingModel(
            sensor=vibration,
            value=2,
            recorded_at=datetime.now(timezone.utc),
        ),
        SensorReadingModel(
            sensor=oil_temperature,
            value=80,
            recorded_at=datetime.now(timezone.utc),
        ),
    ]

    db_session.add_all(readings)
    db_session.flush()

    # Create alerts.
    alerts = [
        AlertModel(
            reading=readings[1],
            severity="high",
            message="Temperature exceeded normal range",
            status="open",
            created_at=datetime.now(timezone.utc),
        ),
        AlertModel(
            reading=readings[3],
            severity="medium",
            message="Oil temperature exceeded normal range",
            status="resolved",
            created_at=datetime.now(timezone.utc),
        ),
    ]

    db_session.add_all(alerts)
    db_session.commit()

    return {
        "equipment_id": machine.equipment_id,
        "reading_id": readings[0].id,
        "alert_id": alerts[0].id,
    }


# -------------------------
# Equipment API tests
# -------------------------

def test_list_equipment(client, sample_data):
    response = client.get("/equipment/")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_equipment(client, sample_data):
    response = client.get("/equipment/CNC-TEST")

    assert response.status_code == 200
    assert response.json()["equipment_id"] == "CNC-TEST"


def test_get_unknown_equipment(client):
    response = client.get("/equipment/UNKNOWN")

    assert response.status_code == 404


# -------------------------
# Readings API tests
# -------------------------

def test_list_readings(client, sample_data):
    response = client.get("/readings")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_readings_pagination(client, sample_data):
    response = client.get("/readings?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_equipment_readings(client, sample_data):
    response = client.get(
        "/readings?equipment_id=CNC-TEST"
    )

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_get_reading(client, sample_data):
    reading_id = sample_data["reading_id"]

    response = client.get(f"/readings/{reading_id}")

    assert response.status_code == 200
    assert response.json()["value"] == 50


# -------------------------
# Alerts API tests
# -------------------------

def test_list_alerts(client, sample_data):
    response = client.get("/alerts/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_alerts(client, sample_data):
    response = client.get("/alerts/?severity=high")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_alert_status(client, sample_data):
    alert_id = sample_data["alert_id"]

    response = client.patch(
        f"/alerts/{alert_id}",
        json={"status": "acknowledged"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_invalid_alert_status(client, sample_data):
    alert_id = sample_data["alert_id"]

    response = client.patch(
        f"/alerts/{alert_id}",
        json={"status": "closed"},
    )

    assert response.status_code == 422


# -------------------------
# Analytics API tests
# -------------------------

def test_equipment_analytics(client, sample_data):
    response = client.get("/analytics/equipment")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_sensor_analytics(client, sample_data):
    response = client.get("/analytics/sensors")

    assert response.status_code == 200

    temperature = next(
        row for row in response.json()
        if row["equipment_id"] == "CNC-TEST"
        and row["sensor_name"] == "temperature"
    )

    assert temperature["reading_count"] == 2
    assert temperature["average_value"] == 75.0


def test_alert_analytics(client, sample_data):
    response = client.get("/analytics/alerts")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_equipment_health_analytics(client, sample_data):
    response = client.get("/analytics/health")

    assert response.status_code == 200

    health = {
        row["equipment_id"]: row
        for row in response.json()
    }

    assert health["CNC-TEST"]["abnormal_readings"] == 1
    assert health["CNC-TEST"]["open_alerts"] == 1

    assert health["SWG-TEST"]["total_readings"] == 0
    assert health["SWG-TEST"]["monitoring_status"] == "normal"