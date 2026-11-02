from sqlalchemy import select
from sqlalchemy.orm import Session

from meiwatch.models import (
    EquipmentModel,
    SensorDefinitionModel,
    SensorReadingModel,
)


def insert_readings(
    session: Session,
    readings: list[dict],
) -> int:
    """Insert validated sensor readings into PostgreSQL."""

    if not readings:
        return 0

    # Fetch all sensor definitions in one query.
    result = session.execute(
        select(
            EquipmentModel.equipment_id,
            SensorDefinitionModel,
        ).join(EquipmentModel.sensors)
    )

    sensor_lookup = {
        (equipment_id, sensor.sensor_name): sensor
        for equipment_id, sensor in result
    }

    db_readings = []

    for reading in readings:
        key = (
            reading["equipment_id"],
            reading["sensor_name"],
        )

        sensor = sensor_lookup.get(key)

        if sensor is None:
            raise ValueError(f"Unknown sensor: {key}")

        db_readings.append(
            SensorReadingModel(
                sensor_id=sensor.id,
                value=float(reading["value"]),
                recorded_at=reading["timestamp"],
            )
        )

    session.add_all(db_readings)
    session.commit()

    return len(db_readings)