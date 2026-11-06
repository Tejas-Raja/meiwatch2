import signal

from meiwatch import worker


class FakeEvent:
    def __init__(self):
        self.stopped = False
        self.wait_count = 0

    def is_set(self):
        return self.stopped

    def set(self):
        self.stopped = True

    def wait(self, interval):
        self.wait_count += 1

        if self.wait_count >= 2:
            self.stopped = True

        return self.stopped


def configure_environment(monkeypatch):
    monkeypatch.setattr(
        worker.os,
        "getenv",
        lambda key, default=None: {
            "INGESTION_INTERVAL_SECONDS": "1",
            "ANOMALY_PROBABILITY": "0.05",
        }.get(key, default),
    )


def test_worker_continues_after_ingestion_failure(monkeypatch):
    calls = 0

    def fake_ingestion(anomaly_probability):
        nonlocal calls
        calls += 1

        if calls == 1:
            raise RuntimeError("Database temporarily unavailable")

    monkeypatch.setattr(
        worker,
        "run_ingestion_cycle",
        fake_ingestion,
    )

    monkeypatch.setattr(
        worker.threading,
        "Event",
        FakeEvent,
    )

    configure_environment(monkeypatch)

    worker.main()

    assert calls == 2


def test_worker_stops_on_shutdown_signal(monkeypatch):
    calls = 0

    def fake_ingestion(anomaly_probability):
        nonlocal calls
        calls += 1

    monkeypatch.setattr(
        worker,
        "run_ingestion_cycle",
        fake_ingestion,
    )

    monkeypatch.setattr(
        worker.threading,
        "Event",
        FakeEvent,
    )

    configure_environment(monkeypatch)

    def fake_signal(sig, handler):
        if sig == signal.SIGINT:
            handler(sig, None)

    monkeypatch.setattr(
        worker.signal,
        "signal",
        fake_signal,
    )

    worker.main()

    assert calls == 0