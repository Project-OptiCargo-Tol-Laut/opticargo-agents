from __future__ import annotations

import compileall
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    return 0 if compileall.compile_dir(root / "src", quiet=1) else 1


if __name__ == "__main__":
    raise SystemExit(main())
