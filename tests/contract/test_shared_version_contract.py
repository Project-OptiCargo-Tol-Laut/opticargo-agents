from pathlib import Path
import sys

SHARED_SRC = Path(__file__).resolve().parents[3] / "opticargo-shared" / "src"
if SHARED_SRC.exists():
    sys.path.insert(0, str(SHARED_SRC))

from opticargo_shared import __version__ as shared_version  # noqa: E402


def test_shared_contract_version_is_pinned_to_one() -> None:
    assert shared_version == "1.0.0"
