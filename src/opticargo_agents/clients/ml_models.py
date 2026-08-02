from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.contracts import MLScoreResult, payload_to_dict
from opticargo_agents.errors import (
    DependencyContractError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


class JsonTransport(Protocol):
    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
        timeout: float,
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class UrllibJsonTransport:
    def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
        timeout: float,
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(url, data=body, headers=headers, method="POST")
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - URL comes from internal config.
            return json.loads(response.read().decode("utf-8"))


class MLModelsClient:
    def __init__(self, settings: Settings | None = None, transport: JsonTransport | None = None) -> None:
        self.settings = settings or get_settings()
        self.transport = transport or UrllibJsonTransport()

    def health(self) -> dict[str, str]:
        if not self.settings.ml_models_internal_url:
            return {"name": "ml_models", "status": "degraded", "detail": "url_not_configured"}
        return {"name": "ml_models", "status": "unknown", "detail": "http_health_not_called"}

    def score_cargo_match(
        self,
        payload: dict[str, Any],
        *,
        correlation_id: str | None = None,
    ) -> MLScoreResult:
        if not self.settings.ml_models_internal_url:
            error = DependencyUnavailableError("ML Models URL is not configured.", dependency="ml_models")
            return self._fallback(error)

        url = self.settings.ml_models_internal_url.rstrip("/") + "/v1/score/cargo-match"
        headers = {
            "Content-Type": "application/json",
            self.settings.correlation_header: correlation_id or "",
        }
        if self.settings.internal_service_token:
            headers["X-Internal-Service-Token"] = self.settings.internal_service_token

        last_error: Exception | None = None
        attempts = max(1, self.settings.ml_model_max_retries + 1)
        for _ in range(attempts):
            started = time.perf_counter()
            try:
                response = self.transport.post_json(
                    url,
                    payload,
                    headers,
                    self.settings.ml_model_request_timeout_seconds,
                )
                if time.perf_counter() - started > self.settings.ml_model_request_timeout_seconds:
                    raise TimeoutError("ML Models request exceeded timeout budget.")
                return self._normalize_score(response)
            except TimeoutError as exc:
                last_error = DependencyTimeoutError(str(exc), dependency="ml_models")
            except (HTTPError, URLError, OSError) as exc:
                last_error = DependencyUnavailableError(str(exc), dependency="ml_models")
            except (TypeError, ValueError) as exc:
                last_error = DependencyContractError(str(exc), dependency="ml_models")
                break

        if hasattr(last_error, "envelope"):
            return self._fallback(last_error)  # type: ignore[arg-type]
        return self._fallback(DependencyUnavailableError("ML Models request failed.", dependency="ml_models"))

    def _normalize_score(self, response: Any) -> MLScoreResult:
        data = payload_to_dict(response)
        score = data.get("score")
        if score is None:
            raise ValueError("ML score response is missing score.")
        return MLScoreResult(
            score=float(score),
            model_mode=data.get("model_mode"),
            model_version=data.get("model_version"),
            fallback_used=bool(data.get("fallback_used", False)),
            hard_constraint_valid=data.get("hard_constraint_valid"),
            feature_explanations=[payload_to_dict(item) for item in data.get("feature_explanations", [])],
            warnings=list(data.get("warnings", [])),
            raw=data,
        )

    def _fallback(
        self,
        error: DependencyUnavailableError | DependencyTimeoutError | DependencyContractError,
    ) -> MLScoreResult:
        return MLScoreResult(
            fallback_used=True,
            warnings=[str(error)],
            error=error.envelope(),
        )


__all__ = ["JsonTransport", "MLModelsClient", "UrllibJsonTransport"]
