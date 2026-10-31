
import random
from datetime import datetime, timezone

from meiwatch.equipment import EQUIPMENT, Equipment, SensorSpec


def generate_sensor_value(
    sensor: SensorSpec,
    rng: random.Random,
    anomaly_probability: float = 0.05,
) -> tuple[float, bool]:
    """
    Generate one sensor reading.

    Returns:
        A tuple containing (reading, is_abnormal).
    """

    is_abnormal = rng.random() < anomaly_probability

    if is_abnormal:
        # Generate a reading outside the normal operating range.
        span = sensor.normal_max - sensor.normal_min
        deviation = rng.uniform(0.1, 0.3) * span

        # Generate a low anomaly only when possible.
        if sensor.normal_min > 0 and rng.choice([True, False]):
            value = sensor.normal_min - deviation
        else:
            value = sensor.normal_max + deviation

    else:
        # Generate a normal reading with random fluctuations.
        value = rng.uniform(
            sensor.normal_min,
            sensor.normal_max,
        )

    return round(value, 2), is_abnormal


def generate_readings(
    equipment_list: list[Equipment] = EQUIPMENT,
    seed: int | None = None,
    anomaly_probability: float = 0.05,
) -> list[dict]:
    """
    Generate one reading for every sensor on every asset.

    A seed can be supplied to make the output reproducible.
    """

    if not 0 <= anomaly_probability <= 1:
        raise ValueError("Anomaly probability must be between 0 and 1.")

    rng = random.Random(seed)
    timestamp = datetime.now(timezone.utc)

    readings = []

    for equipment in equipment_list:
        for sensor in equipment.sensors:

            value, is_abnormal = generate_sensor_value(
                sensor,
                rng,
                anomaly_probability,
            )

            readings.append({
                "equipment_id": equipment.equipment_id,
                "sensor_name": sensor.name,
                "value": value,
                "unit": sensor.unit,
                "timestamp": timestamp,
                "is_abnormal": is_abnormal,
            })

    return readings
