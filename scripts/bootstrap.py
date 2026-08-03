from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    print(f"Agents repository ready at {root}")
    print("Install with: python -m pip install -e .")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
