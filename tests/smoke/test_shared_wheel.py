import os
import subprocess
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@pytest.mark.skipif(not os.getenv("TEST_WHEEL_BUILD"), reason="Set TEST_WHEEL_BUILD=1 untuk menjalankan kompilasi wheel")
def test_shared_package_can_build_wheel():
    """Memastikan root package dapat di-build menjadi .whl."""
    try:
        import build
    except ImportError:
        pytest.skip("Package 'build' tidak terinstal")

    result = subprocess.run(
        ["python", "-m", "build", "--wheel", "--outdir", str(BASE_DIR / "dist")],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Gagal build wheel: {result.stderr}"