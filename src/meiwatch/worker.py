import logging
import os
import signal
import threading

from meiwatch.ingestion import run_ingestion_cycle


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    interval = float(
        os.getenv("INGESTION_INTERVAL_SECONDS", "10")
    )

    anomaly_probability = float(
        os.getenv("ANOMALY_PROBABILITY", "0.05")
    )

    if interval <= 0:
        raise ValueError("INGESTION_INTERVAL_SECONDS must be positive")

    if not 0 <= anomaly_probability <= 1:
        raise ValueError("ANOMALY_PROBABILITY must be between 0 and 1")

    stop_event = threading.Event()

    def request_shutdown(signum, frame):
        logger.info("Shutdown signal received")
        stop_event.set()

    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)

    logger.info("Sensor ingestion worker starting")
    logger.info("Ingestion interval: %s seconds", interval)
    logger.info("Anomaly probability: %s", anomaly_probability)

    while not stop_event.is_set():
        try:
            run_ingestion_cycle(anomaly_probability)
        except Exception:
            logger.exception("Ingestion cycle failed")

        stop_event.wait(interval)

    logger.info("Sensor ingestion worker stopped")


if __name__ == "__main__":
    main()