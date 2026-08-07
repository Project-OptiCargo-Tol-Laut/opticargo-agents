import ast
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PACKAGE_DIR = BASE_DIR / "src" / "opticargo_agents"


def test_no_hardcoded_secret_defaults_in_functions():
    """Memastikan argument fungsi tidak memiliki nilai default berupa password/token."""
    assert PACKAGE_DIR.exists(), f"Package tidak ditemukan di {PACKAGE_DIR}"

    suspicious_args = {"api_key", "token", "password", "secret", "auth"}
    checked_any = False

    for file_path in PACKAGE_DIR.rglob("*.py"):
        checked_any = True
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for i, arg in enumerate(node.args.args):
                    arg_name = arg.arg.lower()
                    if any(susp in arg_name for susp in suspicious_args):
                        defaults = node.args.defaults
                        default_index = i - (len(node.args.args) - len(defaults))
                        if default_index >= 0:
                            default_node = defaults[default_index]
                            if isinstance(default_node, ast.Constant) and isinstance(default_node.value, str):
                                if len(default_node.value) > 0:
                                    pytest.fail(
                                        f"Keamanan Arsitektur: Nilai default hardcoded untuk '{arg.arg}' "
                                        f"ditemukan di fungsi {node.name}() dalam file {file_path.name}"
                                    )

    assert checked_any, "Tidak ada file .py yang ditemukan untuk diperiksa"