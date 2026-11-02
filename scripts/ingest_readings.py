from meiwatch.database import SessionLocal
from meiwatch.data_processor import process_readings
from meiwatch.repository import insert_readings
from meiwatch.sensor_generator import generate_readings


def main():
    # 1. Generate synthetic sensor readings.
    raw_readings = generate_readings(
        seed=42,
        anomaly_probability=0.10,
    )

    # 2. Validate and process the readings.
    valid_df, rejected_df = process_readings(raw_readings)

    print("=== Ingestion Summary ===")
    print(f"Generated readings: {len(raw_readings)}")
    print(f"Valid readings: {len(valid_df)}")
    print(f"Rejected readings: {len(rejected_df)}")

    # 3. Insert valid readings into PostgreSQL.
    readings = valid_df.to_dict(orient="records")

    with SessionLocal() as session:
        inserted_count = insert_readings(session, readings)

    print(f"Inserted into PostgreSQL: {inserted_count}")

    # 4. Display rejected records, if any.
    if not rejected_df.empty:
        print("\n=== Rejected Readings ===")
        print(
            rejected_df[
                ["equipment_id", "sensor_name", "rejection_reason"]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()