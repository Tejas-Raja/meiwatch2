from meiwatch.analytics import get_alert_summary
from meiwatch.database import SessionLocal


def main():
    with SessionLocal() as session:
        summary = get_alert_summary(session)

    print("=== Alert Summary ===\n")

    total = 0

    for row in summary:
        count = row["alert_count"]
        total += count

        print(
            f"Severity: {row['severity']} | "
            f"Status: {row['status']} | "
            f"Count: {count}"
        )

    print(f"\nTotal alerts: {total}")


if __name__ == "__main__":
    main()