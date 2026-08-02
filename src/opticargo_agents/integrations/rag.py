from __future__ import annotations

import time
from typing import Any, Callable

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.contracts import RetrievalRequest, RetrievalResult, payload_to_dict
from opticargo_agents.errors import (
    DependencyContractError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)

RetrieveFunc = Callable[..., Any]


class RagAdapter:
    def __init__(self, settings: Settings | None = None, retrieve_func: RetrieveFunc | None = None) -> None:
        self.settings = settings or get_settings()
        self._retrieve_func = retrieve_func

    def health(self) -> dict[str, str]:
        if self._retrieve_func is not None:
            return {"name": "rag", "status": "ready", "detail": "injected"}
        try:
            self._load_retrieve_func()
        except Exception as exc:  # pragma: no cover - exercised through adapter result tests
            return {"name": "rag", "status": "degraded", "detail": exc.__class__.__name__}
        return {"name": "rag", "status": "ready", "detail": "package_available"}

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        query = request.query.strip()
        if not query:
            return RetrievalResult(
                query=request.query,
                abstained=True,
                abstention_reason="Query is empty.",
                warnings=["RAG retrieval skipped because query is empty."],
            )

        top_k = max(1, min(request.top_k or self.settings.rag_top_k, self.settings.max_top_n))
        started = time.perf_counter()
        try:
            result = self._load_retrieve_func()(
                query,
                graph_context=request.graph_context,
                top_k=top_k,
                min_score=request.min_score,
            )
        except TimeoutError as exc:
            return self._abstain(query, DependencyTimeoutError(str(exc), dependency="rag"))
        except ImportError as exc:
            return self._abstain(query, DependencyUnavailableError(str(exc), dependency="rag"))
        except Exception as exc:
            return self._abstain(query, DependencyUnavailableError(str(exc), dependency="rag"))

        elapsed = time.perf_counter() - started
        if elapsed > self.settings.request_timeout_seconds:
            return self._abstain(
                query,
                DependencyTimeoutError("RAG retrieval exceeded timeout budget.", dependency="rag"),
            )
        return self._normalize_result(query, result)

    def _load_retrieve_func(self) -> RetrieveFunc:
        if self._retrieve_func is not None:
            return self._retrieve_func
        from opticargo_rag_pipeline.retrieval.service import retrieve

        return retrieve

    def _normalize_result(self, query: str, result: Any) -> RetrievalResult:
        data = payload_to_dict(result)
        try:
            confidence = data.get("confidence")
            return RetrievalResult(
                query=str(data.get("query") or query),
                chunks=[payload_to_dict(item) for item in data.get("chunks", [])],
                citations=[payload_to_dict(item) for item in data.get("citations", [])],
                confidence=float(confidence) if confidence is not None else None,
                abstained=bool(data.get("abstained", False)),
                abstention_reason=data.get("abstention_reason"),
                warnings=list(data.get("warnings", [])),
                raw=data,
            )
        except (TypeError, ValueError) as exc:
            return self._abstain(
                query,
                DependencyContractError(f"Invalid RAG result: {exc}", dependency="rag"),
            )

    def _abstain(self, query: str, error: DependencyUnavailableError | DependencyTimeoutError | DependencyContractError) -> RetrievalResult:
        return RetrievalResult(
            query=query,
            abstained=True,
            abstention_reason="RAG evidence is unavailable.",
            warnings=[str(error)],
            error=error.envelope(),
        )


__all__ = ["RagAdapter"]
