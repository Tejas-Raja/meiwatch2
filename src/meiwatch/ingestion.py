
import logging
from meiwatch.database import SessionLocal
from meiwatch.data_processor import process_readings
from meiwatch.repository import insert_readings
from meiwatch.sensor_generator import generate_readings
from meiwatch.alert_service import generate_alerts


logger = logging.getLogger(__name__)


def run_ingestion_cycle(
    anomaly_probability: float = 0.05,
) -> dict:
    """
    Execute one complete sensor ingestion cycle.

    Generates readings, validates them, stores valid records,
    and generates alerts for abnormal readings.
    """

    # 1. Generate synthetic sensor readings.
    raw_readings = generate_readings(
        seed=None,
        anomaly_probability=anomaly_probability,
    )

    # 2. Validate and process readings.
    valid_df, rejected_df = process_readings(raw_readings)

    readings = valid_df.to_dict(orient="records")

    # 3. Insert readings and generate alerts.
    with SessionLocal() as session:
        inserted_count = insert_readings(session, readings)
        generated_alerts = generate_alerts(session)

    # 4. Build ingestion summary.
    summary = {
        "generated": len(raw_readings),
        "valid": len(valid_df),
        "rejected": len(rejected_df),
        "inserted": inserted_count,
        "alerts": generated_alerts,
    }

    logger.info(
        "Ingestion completed: %s",
        summary,
    )

    if not rejected_df.empty:
        logger.warning(
            "Rejected readings:\n%s",
            rejected_df[
                ["equipment_id", "sensor_name", "rejection_reason"]
            ].to_string(index=False),
        )

    return summary
