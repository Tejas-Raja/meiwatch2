from sqlalchemy import select
from sqlalchemy.orm import Session

from meiwatch.models import (
    SensorDefinitionModel,
    SensorReadingModel,
)


def detect_anomalies(session: Session) -> list[dict]:
    """Find readings outside their configured operating ranges."""

    result = session.execute(
        select(
            SensorReadingModel,
            SensorDefinitionModel,
        ).join(
            SensorDefinitionModel,
            SensorReadingModel.sensor_id == SensorDefinitionModel.id,
        )
    )

    anomalies = []

    for reading, sensor in result:

        if (
            reading.value < sensor.normal_min
            or reading.value > sensor.normal_max
        ):
            anomalies.append({
                "reading_id": reading.id,
                "sensor_name": sensor.sensor_name,
                "value": reading.value,
                "unit": sensor.unit,
                "normal_min": sensor.normal_min,
                "normal_max": sensor.normal_max,
                "recorded_at": reading.recorded_at,
            })

    return anomalies