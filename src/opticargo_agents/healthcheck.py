from __future__ import annotations

from opticargo_agents.health import readiness_report


def main() -> int:
    report = readiness_report()
    return 0 if report.status == "ready" else 1


__all__ = ["main"]
