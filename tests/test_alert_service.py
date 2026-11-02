from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from meiwatch.database import Base
from meiwatch.models import (
    AlertModel,
    EquipmentModel,
    SensorDefinitionModel,
    SensorReadingModel,
)
from meiwatch.alert_service import (
    calculate_severity,
    generate_alerts,
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


def create_test_reading(session, value):
    equipment = EquipmentModel(
        equipment_id="TEST-001",
        name="Test Machine",
        category="machine",
        location="Test Area",
    )

    sensor = SensorDefinitionModel(
        sensor_name="temperature",
        unit="°C",
        normal_min=40,
        normal_max=90,
    )

    equipment.sensors.append(sensor)

    reading = SensorReadingModel(
        value=value,
        recorded_at=datetime.now(timezone.utc),
        sensor=sensor,
    )

    session.add(equipment)
    session.add(reading)
    session.flush()

    return reading


def test_calculate_severity():
    assert calculate_severity(92, 40, 90) == "low"
    assert calculate_severity(97, 40, 90) == "medium"
    assert calculate_severity(100, 40, 90) == "high"
    assert calculate_severity(110, 40, 90) == "critical"


def test_normal_reading_does_not_generate_alert(session):
    create_test_reading(session, 60)

    count = generate_alerts(session)

    assert count == 0


def test_abnormal_reading_generates_alert(session):
    create_test_reading(session, 97)

    count = generate_alerts(session)

    alerts = session.scalars(
        select(AlertModel)
    ).all()

    assert count == 1
    assert len(alerts) == 1
    assert alerts[0].severity == "medium"
    assert alerts[0].status == "open"


def test_alert_generation_does_not_create_duplicates(session):
    create_test_reading(session, 100)

    first_count = generate_alerts(session)
    second_count = generate_alerts(session)

    alerts = session.scalars(
        select(AlertModel)
    ).all()

    assert first_count == 1
    assert second_count == 0
    assert len(alerts) == 1