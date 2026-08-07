import ast
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INTEGRATIONS_DIR = BASE_DIR / "src" / "opticargo_agents" / "integrations"


def test_no_database_mutation_methods_in_graph_and_rag():
    """Memastikan adapter tidak memiliki statement insert/update/delete."""
    assert INTEGRATIONS_DIR.exists(), f"Direktori integrations tidak ditemukan di {INTEGRATIONS_DIR}"

    forbidden_calls = {"commit", "insert", "update", "delete", "create", "merge"}
    target_files = list(INTEGRATIONS_DIR.rglob("*.py"))
    assert target_files, "Tidak ada file adapter yang ditemukan untuk diperiksa"

    for file_path in target_files:
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