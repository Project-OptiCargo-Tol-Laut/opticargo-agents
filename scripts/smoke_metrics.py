from opticargo_agents.metrics import METRICS, record_node


def main() -> int:
    record_node("smoke", "completed")
    print(METRICS.snapshot())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
