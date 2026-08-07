import ast
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
NODES_DIR = BASE_DIR / "src" / "opticargo_agents" / "nodes"


def get_module_imports(file_path: Path) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def test_workflow_nodes_do_not_import_each_other():
    """Node (agen) harus independen dan dikoordinasikan oleh graph/orchestrator."""
    assert NODES_DIR.exists(), f"Direktori nodes tidak ditemukan di {NODES_DIR}"

    node_files = list(NODES_DIR.rglob("*.py"))
    assert node_files, "Tidak ada file node yang ditemukan untuk diperiksa"

    for file_path in node_files:
        current_module = file_path.stem
        if current_module == "__init__":
            continue
        imports = get_module_imports(file_path)
        for imp in imports:
            if imp.startswith("opticargo_agents.nodes."):
                imported_module = imp.split(".")[-1]
                if imported_module != current_module and imported_module not in {"common", "__init__"}:
                    pytest.fail(
                        f"Coupling Bocor: Node '{current_module}' mengimpor saudaranya "
                        f"'{imported_module}' secara langsung."
                    )