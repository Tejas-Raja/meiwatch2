
import math

import pandas as pd

from meiwatch.equipment import EQUIPMENT


REQUIRED_COLUMNS = [
    "equipment_id",
    "sensor_name",
    "value",
    "unit",
    "timestamp",
]


def process_readings(
    raw_readings: list[dict],
) -> tuple[pd.DataFrame, pd.DataFrame]:

    # Convert raw dictionaries into a DataFrame.
    df = pd.DataFrame(raw_readings)

    # Handle an empty input.
    if df.empty:
        return df, pd.DataFrame()

    # Check that all required columns exist.
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Build a lookup of valid equipment and sensors.
    sensor_lookup = {
        (equipment.equipment_id, sensor.name): sensor
        for equipment in EQUIPMENT
        for sensor in equipment.sensors
    }

    # Convert values to numeric.
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    # Convert timestamps to UTC.
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True,
    )

    # Remove the generator's anomaly flag.
    # Anomaly detection belongs to a separate component.
    df = df.drop(columns=["is_abnormal"], errors="ignore")

    valid_indices = []
    rejected_records = []

    seen_readings = set()

    for index, row in df.iterrows():

        reasons = []

        equipment_id = row["equipment_id"]
        sensor_name = row["sensor_name"]
        value = row["value"]
        unit = row["unit"]
        timestamp = row["timestamp"]

        # Check for missing values.
        if pd.isna(equipment_id) or not str(equipment_id).strip():
            reasons.append("Missing equipment ID")

        if pd.isna(sensor_name) or not str(sensor_name).strip():
            reasons.append("Missing sensor name")

        if pd.isna(unit) or not str(unit).strip():
            reasons.append("Missing unit")

        if pd.isna(value):
            reasons.append("Invalid or missing numeric value")
        elif not math.isfinite(value):
            reasons.append("Non-finite numeric value")

        if pd.isna(timestamp):
            reasons.append("Invalid or missing timestamp")

        # Validate equipment and sensor combination.
        sensor = None

        if not pd.isna(equipment_id) and not pd.isna(sensor_name):
            sensor = sensor_lookup.get(
                (equipment_id, sensor_name)
            )

            if sensor is None:
                reasons.append("Unknown equipment or sensor")

        # Validate measurement unit.
        if sensor is not None and not pd.isna(unit):
            if unit != sensor.unit:
                reasons.append("Incorrect sensor unit")

        # Check duplicate readings.
        if not reasons:
            reading_key = (
                equipment_id,
                sensor_name,
                timestamp,
            )

            if reading_key in seen_readings:
                reasons.append("Duplicate reading")
            else:
                seen_readings.add(reading_key)

        # Separate valid and rejected records.
        if reasons:
            record = row.to_dict()
            record["rejection_reason"] = "; ".join(reasons)
            rejected_records.append(record)
        else:
            valid_indices.append(index)

    valid_df = df.loc[valid_indices].reset_index(drop=True)

    rejected_df = pd.DataFrame(rejected_records)

    return valid_df, rejected_df
