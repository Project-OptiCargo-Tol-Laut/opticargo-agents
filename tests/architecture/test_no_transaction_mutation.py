import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGE_DIR = BASE_DIR / "opticargo_agents"

def test_no_database_mutation_methods_in_graph_and_rag():
    """Memastikan adapter tidak memiliki statement insert/update/delete."""
    target_dirs = [PACKAGE_DIR / "adapters" / "graph", PACKAGE_DIR / "adapters" / "rag"]
    forbidden_calls = {"commit", "insert", "update", "delete", "create", "merge"}
    
    for t_dir in target_dirs:
        if not t_dir.exists():
            continue
            
        for file_path in t_dir.rglob("*.py"):
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
                
            for node in ast.walk(tree):
                # Deteksi pemanggilan metode seperti session.commit() atau tx.create()
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in forbidden_calls:
                        pytest.fail(
                            f"Arsitektur Mutasi Terdeteksi: Adapter AI '{file_path.name}' "
                            f"menggunakan metode perubahan data (.{node.func.attr}()). AI agents harus bersifat read-only."
                        )