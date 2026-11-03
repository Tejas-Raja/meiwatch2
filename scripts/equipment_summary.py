from meiwatch.analytics import get_equipment_summary
from meiwatch.database import SessionLocal


def main():
    with SessionLocal() as session:
        summary = get_equipment_summary(session)

    print("=== Equipment Summary ===")

    total = 0

    for row in summary:
        count = row["equipment_count"]
        total += count

        print(f"{row['category']}: {count}")

    print(f"\nTotal equipment: {total}")


if __name__ == "__main__":
    main()