import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGE_DIR = BASE_DIR / "opticargo_agents"

def test_api_routes_do_not_expose_public_internet_dependencies():
    """Memastikan layer API murni bertindak sebagai gateway internal."""
    api_dir = PACKAGE_DIR / "api"
    if not api_dir.exists():
        return
        
    for file_path in api_dir.rglob("*.py"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value.lower()
                assert "http://" not in val and "https://" not in val, \
                    f"Pelanggaran Internal Service: Hardcoded URL '{node.value}' di {file_path.name}. API harus menggunakan dependency injection."