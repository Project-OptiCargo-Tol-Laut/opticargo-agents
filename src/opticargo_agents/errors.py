from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ErrorEnvelope:
    code: str
    message: str
    dependency: str | None = None
    retryable: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class AgentsError(Exception):
    code = "agents_error"
    retryable = False

    def __init__(self, message: str, *, dependency: str | None = None) -> None:
        super().__init__(message)
        self.dependency = dependency

    def envelope(self) -> ErrorEnvelope:
        return ErrorEnvelope(
            code=self.code,
            message=str(self),
            dependency=self.dependency,
            retryable=self.retryable,
        )


class DependencyUnavailableError(AgentsError):
    code = "dependency_unavailable"
    retryable = True


class DependencyTimeoutError(AgentsError):
    code = "dependency_timeout"
    retryable = True


class DependencyContractError(AgentsError):
    code = "dependency_contract_error"
    retryable = False


class InvalidRequestError(AgentsError):
    code = "invalid_request"
    retryable = False