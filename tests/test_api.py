from insureiq.api import health, metrics, models


def test_health_and_metrics_are_read_only() -> None:
    assert health() == {"status": "ok"}
    assert metrics()["status"] == "demo"
    assert "models" in models()
