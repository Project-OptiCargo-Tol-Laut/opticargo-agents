import json


def main() -> int:
    print(json.dumps({"event": "completed", "data": {"ok": True}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
