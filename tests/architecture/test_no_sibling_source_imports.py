import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKFLOW_DIR = BASE_DIR / "opticargo_agents" / "workflow"

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
    if not WORKFLOW_DIR.exists():
        return
        
    # Ambil semua folder/file yang merepresentasikan node individu
    node_files = list(WORKFLOW_DIR.rglob("*.py"))
    
    for file_path in node_files:
        imports = get_module_imports(file_path)
        for imp in imports:
            # Jika file intent.py mencoba import optimization.py
            if imp.startswith("opticargo_agents.workflow."):
                imported_module = imp.split(".")[-1]
                current_module = file_path.stem
                if imported_module != current_module and imported_module != "common":
                    pytest.fail(f"Coupling Bocor: Node '{current_module}' mengimpor saudaranya '{imported_module}' secara langsung.")