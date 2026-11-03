from meiwatch.analytics import get_sensor_statistics
from meiwatch.database import SessionLocal


def main():
    with SessionLocal() as session:
        statistics = get_sensor_statistics(session)

    print("=== Sensor Statistics ===\n")

    for row in statistics:
        print(
            f"{row['equipment_id']} | "
            f"{row['sensor_name']} | "
            f"Count: {row['reading_count']} | "
            f"Avg: {row['average_value']} {row['unit']} | "
            f"Min: {row['minimum_value']} | "
            f"Max: {row['maximum_value']}"
        )


if __name__ == "__main__":
    main()