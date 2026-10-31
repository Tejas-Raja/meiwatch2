
from meiwatch.equipment import EQUIPMENT
from meiwatch.sensor_generator import generate_readings


def test_generator_produces_25_readings():
    readings = generate_readings(seed=42)

    assert len(readings) == 25


def test_generator_produces_correct_reading_structure():
    readings = generate_readings(seed=42)

    required_keys = {
        "equipment_id",
        "sensor_name",
        "value",
        "unit",
        "timestamp",
        "is_abnormal",
    }

    for reading in readings:
        assert required_keys.issubset(reading.keys())


def test_generator_is_reproducible():
    readings_1 = generate_readings(seed=42)
    readings_2 = generate_readings(seed=42)

    for first, second in zip(readings_1, readings_2):
        assert first["value"] == second["value"]
        assert first["is_abnormal"] == second["is_abnormal"]


def test_zero_anomaly_probability():
    readings = generate_readings(
        seed=42,
        anomaly_probability=0,
    )

    assert all(
        not reading["is_abnormal"]
        for reading in readings
    )


def test_full_anomaly_probability():
    readings = generate_readings(
        seed=42,
        anomaly_probability=1,
    )

    assert all(
        reading["is_abnormal"]
        for reading in readings
    )

    sensor_lookup = {
        (equipment.equipment_id, sensor.name): sensor
        for equipment in EQUIPMENT
        for sensor in equipment.sensors
    }

    for reading in readings:
        sensor = sensor_lookup[
            (reading["equipment_id"], reading["sensor_name"])
        ]

        assert (
            reading["value"] < sensor.normal_min
            or reading["value"] > sensor.normal_max
        )


def test_invalid_anomaly_probability():
    import pytest

    with pytest.raises(ValueError):
        generate_readings(anomaly_probability=1.5)
