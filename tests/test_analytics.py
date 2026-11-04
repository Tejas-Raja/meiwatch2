from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from meiwatch.database import Base
from meiwatch.models import (
    EquipmentModel,
    SensorDefinitionModel,
    SensorReadingModel,
    AlertModel,
)
from meiwatch.analytics import (
    get_equipment_summary,
    get_sensor_statistics,
    get_alert_summary,
    get_equipment_health_summary,
)


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def populate_test_data(session):
    # Equipment 1: Machine
    machine = EquipmentModel(
        equipment_id="CNC-TEST",
        name="Test CNC Machine",
        category="machine",
        location="Test Hall A",
    )

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

    machine.sensors.extend([temperature, vibration])

    # Equipment 2: Transformer
    transformer = EquipmentModel(
        equipment_id="TRF-TEST",
        name="Test Transformer",
        category="transformer",
        location="Test Electrical Room",
    )

    oil_temperature = SensorDefinitionModel(
        sensor_name="oil_temperature",
        unit="°C",
        normal_min=30,
        normal_max=75,
    )

    transformer.sensors.append(oil_temperature)

    # Equipment 3: Switchgear with no readings
    switchgear = EquipmentModel(
        equipment_id="SWG-TEST",
        name="Test Switchgear",
        category="switchgear",
        location="Test Electrical Room",
    )

    current = SensorDefinitionModel(
        sensor_name="current",
        unit="A",
        normal_min=50,
        normal_max=400,
    )

    switchgear.sensors.append(current)

    session.add_all([machine, transformer, switchgear])
    session.flush()

    # Insert sensor readings.
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

    session.add_all(readings)
    session.flush()

    # Add alerts for the two abnormal readings.
    session.add_all([
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
    ])

    session.commit()


def test_equipment_summary(session):
    populate_test_data(session)

    result = get_equipment_summary(session)

    counts = {
        row["category"]: row["equipment_count"]
        for row in result
    }

    assert counts == {
        "machine": 1,
        "switchgear": 1,
        "transformer": 1,
    }


def test_sensor_statistics(session):
    populate_test_data(session)

    result = get_sensor_statistics(session)

    temperature = next(
        row for row in result
        if row["equipment_id"] == "CNC-TEST"
        and row["sensor_name"] == "temperature"
    )

    assert temperature["reading_count"] == 2
    assert temperature["average_value"] == 75.0
    assert temperature["minimum_value"] == 50
    assert temperature["maximum_value"] == 100


def test_alert_summary(session):
    populate_test_data(session)

    result = get_alert_summary(session)

    summary = {
        (row["severity"], row["status"]): row["alert_count"]
        for row in result
    }

    assert summary == {
        ("high", "open"): 1,
        ("medium", "resolved"): 1,
    }


def test_equipment_health_summary(session):
    populate_test_data(session)

    result = get_equipment_health_summary(session)

    health = {
        row["equipment_id"]: row
        for row in result
    }

    assert health["CNC-TEST"]["total_readings"] == 3
    assert health["CNC-TEST"]["abnormal_readings"] == 1
    assert health["CNC-TEST"]["open_alerts"] == 1
    assert health["CNC-TEST"]["monitoring_status"] == "attention"

    assert health["TRF-TEST"]["abnormal_readings"] == 1
    assert health["TRF-TEST"]["open_alerts"] == 0

    # Verify equipment without readings is still included.
    assert health["SWG-TEST"]["total_readings"] == 0
    assert health["SWG-TEST"]["monitoring_status"] == "normal"