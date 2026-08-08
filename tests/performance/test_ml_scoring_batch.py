import time

from opticargo_agents.clients.ml_models import MLModelsClient
from opticargo_agents.config import load_settings
from tests.performance._support import successful_ml_response


class _FakeTransport:
    def post_json(self, url, payload, headers, timeout):
        return successful_ml_response()


ML_BATCH_P95_THRESHOLD_MS = 100


def test_ml_scoring_batch() -> None:
    """Ukur latensi MLModelsClient.score_cargo_match asli untuk 1 batch kandidat,
    dengan transport palsu (bukan HTTP asli) -- yang diukur overhead client kita
    sendiri (bangun payload, validasi, parsing respons), bukan jaringan."""
    client = MLModelsClient(load_settings({"ML_MODELS_INTERNAL_URL": "http://ml-models"}), transport=_FakeTransport())
    payload = {
        "trace_id": "batch-test",
        "voyage": {
            "voyage_id": "voyage-1",
            "route_id": "route-1",
            "route_distance_km": 120.0,
            "remaining_weight_ton": 80.0,
            "remaining_volume_m3": 160.0,
            "operating_cost_per_km_idr": 5000.0,
        },
        "candidate": {
            "cargo_listing_id": "listing-1",
            "supplier_id": "supplier-1",
            "cargo_weight_ton": 25.0,
            "cargo_volume_m3": 40.0,
            "asking_price_per_ton_idr": 100000.0,
            "market_rate_per_ton_idr": 120000.0,
            "origin_distance_km": 5.0,
            "destination_distance_km": 5.0,
            "schedule_gap_hours": 2.0,
            "supplier_rating": 4.5,
            "supplier_success_rate": 0.9,
            "supplier_cancellation_rate": 0.05,
            "commodity_compatibility": True,
            "certification_match": True,
            "temperature_match": True,
            "weather_risk": 0.1,
            "port_congestion": 0.1,
            "historical_acceptance_rate": 0.8,
        },
    }

    for _ in range(3):
        client.score_cargo_match(payload)

    batch_size = 20
    start = time.perf_counter()
    for _ in range(batch_size):
        result = client.score_cargo_match(payload)
    total_ms = (time.perf_counter() - start) * 1000

    assert result.available is True
    avg_per_call = total_ms / batch_size

    assert avg_per_call <= ML_BATCH_P95_THRESHOLD_MS, (
        f"Rata-rata latensi score_cargo_match {avg_per_call:.2f}ms melebihi ambang {ML_BATCH_P95_THRESHOLD_MS}ms"
    )