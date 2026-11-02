from meiwatch.alert_service import generate_alerts
from meiwatch.database import SessionLocal


def main():
    with SessionLocal() as session:
        count = generate_alerts(session)

    print(f"New alerts generated: {count}")


if __name__ == "__main__":
    main()