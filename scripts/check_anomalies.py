from meiwatch.anomaly_detector import detect_anomalies
from meiwatch.database import SessionLocal


def main():
    with SessionLocal() as session:
        anomalies = detect_anomalies(session)

    print(f"Anomalies detected: {len(anomalies)}")

    for anomaly in anomalies:
        print(
            f"{anomaly['sensor_name']} | "
            f"Reading: {anomaly['value']} {anomaly['unit']} | "
            f"Normal range: "
            f"{anomaly['normal_min']} - {anomaly['normal_max']} | "
            f"Reading ID: {anomaly['reading_id']}"
        )


if __name__ == "__main__":
    main()