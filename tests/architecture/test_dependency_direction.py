import ast
from pathlib import Path

# Root project diasumsikan berada 3 tingkat di atas file ini
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGE_NAME = "opticargo_agents"
PACKAGE_DIR = BASE_DIR / PACKAGE_NAME

def get_imports(file_path: Path) -> list:
    """Mengekstrak semua modul yang di-import dari file Python."""
    imports = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (SyntaxError, FileNotFoundError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                level = node.level if node.level else 0
                if level > 0:
                    parts = list(file_path.parent.relative_to(BASE_DIR).parts)
                    module_name = ".".join(parts[:-level+1] + [node.module])
                    imports.append(module_name)
                else:
                    imports.append(node.module)
    return imports

def get_python_files(sub_dir: str) -> list:
    """Mengambil semua file .py dalam sub-direktori."""
    target_dir = PACKAGE_DIR / sub_dir
    if not target_dir.exists():
        return []
    return list(target_dir.rglob("*.py"))

# -------------------------------------------------------------------
# FUNGSI TES (Harus berawalan test_)
# -------------------------------------------------------------------

def test_contracts_do_not_import_concrete_implementations():
    contract_files = get_python_files("contracts")
    forbidden_imports = [
        f"{PACKAGE_NAME}.adapters",
        f"{PACKAGE_NAME}.workflow",
        f"{PACKAGE_NAME}.orchestration",
        f"{PACKAGE_NAME}.api"
    ]
    for file_path in contract_files:
        for imp in get_imports(file_path):
            for forbidden in forbidden_imports:
                assert not imp.startswith(forbidden), \
                    f"Kebocoran: Kontrak {file_path.name} mengimpor '{imp}'"

def test_workflow_nodes_do_not_import_api_or_orchestrator():
    workflow_files = get_python_files("workflow")
    forbidden_imports = [
        f"{PACKAGE_NAME}.api",
        f"{PACKAGE_NAME}.orchestration",
        "fastapi",
        "starlette"
    ]
    for file_path in workflow_files:
        for imp in get_imports(file_path):
            for forbidden in forbidden_imports:
                assert not imp.startswith(forbidden), \
                    f"Kebocoran: Workflow {file_path.name} mengimpor '{imp}'"

def test_adapters_do_not_import_workflow_or_api():
    adapter_files = get_python_files("adapters")
    forbidden_imports = [
        f"{PACKAGE_NAME}.workflow",
        f"{PACKAGE_NAME}.orchestration",
        f"{PACKAGE_NAME}.api"
    ]
    for file_path in adapter_files:
        for imp in get_imports(file_path):
            for forbidden in forbidden_imports:
                assert not imp.startswith(forbidden), \
                    f"Kebocoran: Adapter {file_path.name} mengimpor '{imp}'"