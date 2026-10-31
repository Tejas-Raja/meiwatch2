
from meiwatch.sensor_generator import generate_readings
from meiwatch.data_processor import process_readings


def main():

    # Generate normal and abnormal sensor readings.
    raw_readings = generate_readings(
        seed=42,
        anomaly_probability=0.2,
    )

    # Introduce an invalid numeric value.
    invalid_value = raw_readings[0].copy()
    invalid_value["value"] = "not_a_number"

    # Introduce an incorrect sensor unit.
    invalid_unit = raw_readings[1].copy()
    invalid_unit["unit"] = "kg"

    # Introduce a duplicate reading.
    duplicate = raw_readings[2].copy()

    # Add the bad records.
    raw_readings.extend([
        invalid_value,
        invalid_unit,
        duplicate,
    ])

    # Process the readings.
    valid_df, rejected_df = process_readings(raw_readings)

    print("\n--- Processing Summary ---")
    print(f"Raw readings: {len(raw_readings)}")
    print(f"Valid readings: {len(valid_df)}")
    print(f"Rejected readings: {len(rejected_df)}")

    print("\n--- Valid Readings ---")
    print(valid_df.head())

    print("\n--- Rejected Readings ---")
    if not rejected_df.empty:
        print(
            rejected_df[
                ["equipment_id", "sensor_name", "rejection_reason"]
            ]
        )


if __name__ == "__main__":
    main()
