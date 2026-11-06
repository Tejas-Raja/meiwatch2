from datetime import datetime, timezone

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from meiwatch.models import (
    AlertModel,
    SensorDefinitionModel,
    SensorReadingModel,
)


def calculate_severity(
    value: float,
    normal_min: float,
    normal_max: float,
) -> str:
    """Classify an anomaly based on its deviation from the normal range."""

    span = normal_max - normal_min

    if value < normal_min:
        deviation = normal_min - value
    else:
        deviation = value - normal_max

    deviation_ratio = deviation / span

    if deviation_ratio <= 0.05:
        return "low"
    elif deviation_ratio <= 0.15:
        return "medium"
    elif deviation_ratio <= 0.30:
        return "high"
    else:
        return "critical"


def generate_alerts(session: Session) -> int:
    """Create alerts for anomalous readings that have no existing alert."""

    result = session.execute(
        select(
            SensorReadingModel,
            SensorDefinitionModel,
        )
        .join(
            SensorDefinitionModel,
            SensorReadingModel.sensor_id == SensorDefinitionModel.id,
        )
        .outerjoin(
            AlertModel,
            AlertModel.reading_id == SensorReadingModel.id,
        )
        .where(AlertModel.id.is_(None),
            or_(
                SensorReadingModel.value < SensorDefinitionModel.normal_min,
                SensorReadingModel.value > SensorDefinitionModel.normal_max,
            ),
        )
    )

    new_alerts = []

    for reading, sensor in result:

        # Check whether the reading is outside its normal range.
        if (
            sensor.normal_min
            <= reading.value
            <= sensor.normal_max
        ):
            continue

        severity = calculate_severity(
            reading.value,
            sensor.normal_min,
            sensor.normal_max,
        )

        message = (
            f"{sensor.sensor_name} reading of "
            f"{reading.value} {sensor.unit} is outside "
            f"the normal range "
            f"({sensor.normal_min}-{sensor.normal_max} {sensor.unit})."
        )

        new_alerts.append(
            AlertModel(
                reading_id=reading.id,
                severity=severity,
                message=message,
                status="open",
                created_at=datetime.now(timezone.utc),
            )
        )

    session.add_all(new_alerts)
    session.commit()

    return len(new_alerts)