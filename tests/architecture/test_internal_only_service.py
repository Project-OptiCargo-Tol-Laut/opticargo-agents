import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
API_FILE = BASE_DIR / "src" / "opticargo_agents" / "api.py"


def test_api_routes_do_not_expose_public_internet_dependencies():
    """Memastikan layer API murni bertindak sebagai gateway internal."""
    assert API_FILE.exists(), f"api.py tidak ditemukan di {API_FILE}"

    with open(API_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        tree = ast.parse(content, filename=str(API_FILE))

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.lower()
            assert "http://" not in val and "https://" not in val, \
                f"Pelanggaran Internal Service: Hardcoded URL '{node.value}' di {API_FILE.name}. " \
                f"API harus menggunakan dependency injection."