from meiwatch.analytics import get_equipment_health_summary
from meiwatch.database import SessionLocal


def main():
    with SessionLocal() as session:
        summary = get_equipment_health_summary(session)

    print("=== Equipment Health Summary ===\n")

    for row in summary:
        print(
            f"{row['equipment_id']} | "
            f"{row['category']} | "
            f"Readings: {row['total_readings']} | "
            f"Abnormal: {row['abnormal_readings']} | "
            f"Open alerts: {row['open_alerts']} | "
            f"Status: {row['monitoring_status']}"
        )


if __name__ == "__main__":
    main()