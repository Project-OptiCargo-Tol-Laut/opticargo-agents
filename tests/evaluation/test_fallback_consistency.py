"""Evaluasi: pastikan MLModelsClient ASLI selalu menandai fallback_used=True
dan menyertakan warning yang jelas setiap kali ML service tidak tersedia --
bukan mengecek string pesan yang ditulis manual di dalam test."""

from opticargo_agents.clients import MLModelsClient
from opticargo_agents.config import load_settings

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0


class _FailingTransport:
    def post_json(self, url, payload, headers, timeout):
        raise ConnectionRefusedError("ml-models tidak bisa dihubungi")


class _WorkingTransport:
    def post_json(self, url, payload, headers, timeout):
        return {"score": 0.7, "hard_constraint_valid": True, "fallback_used": False}


DATASET = [
    {"name": "url_tidak_dikonfigurasi", "settings_env": {}, "transport": None, "expect_fallback": True},
    {
        "name": "service_gagal_dihubungi",
        "settings_env": {"ML_MODELS_INTERNAL_URL": "http://ml-models"},
        "transport": _FailingTransport(),
        "expect_fallback": True,
    },
    {
        "name": "service_jalan_normal",
        "settings_env": {"ML_MODELS_INTERNAL_URL": "http://ml-models"},
        "transport": _WorkingTransport(),
        "expect_fallback": False,
    },
]


def test_fallback_consistency() -> None:
    failures = []
    successes = 0

    for case in DATASET:
        settings = load_settings(case["settings_env"])
        client = MLModelsClient(settings, transport=case["transport"])
        result = client.score_cargo_match({"voyage": {}, "candidate": {}})

        if result.fallback_used != case["expect_fallback"]:
            failures.append({"case": case["name"], "fallback_used": result.fallback_used})
        elif result.fallback_used and not result.warnings:
            failures.append({"case": case["name"], "reason": "fallback tanpa warning"})
        else:
            successes += 1

    accuracy = successes / len(DATASET)

    assert accuracy >= THRESHOLD, (
        f"Fallback consistency {accuracy*100:.1f}% di bawah ambang {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )