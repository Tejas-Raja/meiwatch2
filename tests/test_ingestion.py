import logging

import pandas as pd

from meiwatch import ingestion


def test_run_ingestion_cycle_returns_summary(monkeypatch):
    raw_readings = [
        {"equipment_id": "CNC-001"},
        {"equipment_id": "PUMP-001"},
        {"equipment_id": "TRF-001"},
    ]

    valid_df = pd.DataFrame([
        {
            "equipment_id": "CNC-001",
            "sensor_name": "temperature",
            "value": 50.0,
            "unit": "°C",
            "timestamp": pd.Timestamp("2026-11-06", tz="UTC"),
        },
        {
            "equipment_id": "PUMP-001",
            "sensor_name": "temperature",
            "value": 45.0,
            "unit": "°C",
            "timestamp": pd.Timestamp("2026-11-06", tz="UTC"),
        },
    ])

    rejected_df = pd.DataFrame(
        columns=["equipment_id", "sensor_name", "rejection_reason"]
    )

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    # Mock sensor generation.
    def fake_generate_readings(seed, anomaly_probability):
        assert seed is None
        assert anomaly_probability == 0.10
        return raw_readings

    # Mock database insertion.
    def fake_insert_readings(session, readings):
        assert len(readings) == 2
        return 2

    monkeypatch.setattr(
        ingestion,
        "generate_readings",
        fake_generate_readings,
    )

    monkeypatch.setattr(
        ingestion,
        "process_readings",
        lambda readings: (valid_df, rejected_df),
    )

    monkeypatch.setattr(
        ingestion,
        "SessionLocal",
        lambda: FakeSession(),
    )

    monkeypatch.setattr(
        ingestion,
        "insert_readings",
        fake_insert_readings,
    )

    monkeypatch.setattr(
        ingestion,
        "generate_alerts",
        lambda session: 1,
    )

    result = ingestion.run_ingestion_cycle(
        anomaly_probability=0.10
    )

    assert result == {
        "generated": 3,
        "valid": 2,
        "rejected": 0,
        "inserted": 2,
        "alerts": 1,
    }


def test_run_ingestion_cycle_logs_rejected_readings(
    monkeypatch,
    caplog,
):
    raw_readings = [{"equipment_id": "CNC-001"}]

    valid_df = pd.DataFrame(columns=[
        "equipment_id",
        "sensor_name",
        "value",
        "unit",
        "timestamp",
    ])

    rejected_df = pd.DataFrame([
        {
            "equipment_id": "CNC-001",
            "sensor_name": "temperature",
            "rejection_reason": "invalid value",
        }
    ])

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        ingestion,
        "generate_readings",
        lambda **kwargs: raw_readings,
    )

    monkeypatch.setattr(
        ingestion,
        "process_readings",
        lambda readings: (valid_df, rejected_df),
    )

    monkeypatch.setattr(
        ingestion,
        "SessionLocal",
        lambda: FakeSession(),
    )

    monkeypatch.setattr(
        ingestion,
        "insert_readings",
        lambda session, readings: 0,
    )

    monkeypatch.setattr(
        ingestion,
        "generate_alerts",
        lambda session: 0,
    )

    with caplog.at_level(logging.WARNING):
        result = ingestion.run_ingestion_cycle()

    assert result["generated"] == 1
    assert result["valid"] == 0
    assert result["rejected"] == 1
    assert "Rejected readings" in caplog.text
    assert "invalid value" in caplog.text