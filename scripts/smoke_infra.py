from opticargo_agents.health import readiness_report


def main() -> int:
    report = readiness_report()
    print(report.to_dict())
    return 0 if report.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
