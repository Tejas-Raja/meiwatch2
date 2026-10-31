
import pytest

from meiwatch.sensor_generator import generate_readings
from meiwatch.data_processor import process_readings


def test_valid_readings_are_accepted():
    readings = generate_readings(
        seed=42,
        anomaly_probability=0.2,
    )

    valid_df, rejected_df = process_readings(readings)

    assert len(valid_df) == 25
    assert rejected_df.empty


def test_invalid_numeric_value_is_rejected():
    readings = generate_readings(seed=42)

    readings[0]["value"] = "invalid"

    valid_df, rejected_df = process_readings(readings)

    assert len(valid_df) == 24
    assert len(rejected_df) == 1
    assert "Invalid or missing numeric value" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_incorrect_unit_is_rejected():
    readings = generate_readings(seed=42)

    readings[0]["unit"] = "kg"

    valid_df, rejected_df = process_readings(readings)

    assert len(valid_df) == 24
    assert len(rejected_df) == 1
    assert "Incorrect sensor unit" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_duplicate_reading_is_rejected():
    readings = generate_readings(seed=42)

    readings.append(readings[0].copy())

    valid_df, rejected_df = process_readings(readings)

    assert len(valid_df) == 25
    assert len(rejected_df) == 1
    assert "Duplicate reading" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_abnormal_readings_are_preserved():
    readings = generate_readings(
        seed=42,
        anomaly_probability=1,
    )

    valid_df, rejected_df = process_readings(readings)

    assert len(valid_df) == 25
    assert rejected_df.empty

    assert "is_abnormal" not in valid_df.columns


def test_missing_required_column_raises_error():
    readings = generate_readings(seed=42)

    for reading in readings:
      del reading["unit"]

    with pytest.raises(ValueError):
        process_readings(readings)


def test_empty_input():
    valid_df, rejected_df = process_readings([])

    assert valid_df.empty
    assert rejected_df.empty
