
from meiwatch.sensor_generator import generate_readings


def main():
    readings = generate_readings(
        seed=42,
        anomaly_probability=1,
      )

    print(f"Total readings generated: {len(readings)}")

    abnormal_count = sum(
        reading["is_abnormal"]
        for reading in readings
    )

    print(f"Abnormal readings: {abnormal_count}")
    print("-" * 75)

    for reading in readings:
        status = "ABNORMAL" if reading["is_abnormal"] else "NORMAL"

        print(
            f"{reading['equipment_id']:<10} "
            f"{reading['sensor_name']:<22} "
            f"{reading['value']:>8} "
            f"{reading['unit']:<8} "
            f"{status}"
        )


if __name__ == "__main__":
    main()
