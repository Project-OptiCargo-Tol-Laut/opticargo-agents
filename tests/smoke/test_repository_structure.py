from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def test_essential_directories_exist():
    """Memastikan struktur folder inti tidak terhapus atau berubah nama."""
    essential_paths = [
        "src/opticargo_agents/cli",
        "src/opticargo_agents/clients",
        "src/opticargo_agents/integrations",
        "src/opticargo_agents/nodes",
        "src/opticargo_agents/orchestrator"
    ]
    
    for rel_path in essential_paths:
        path = BASE_DIR / rel_path
        assert path.exists() and path.is_dir(), f"Folder esensial hilang: {rel_path}"

def test_essential_files_exist():
    """Memastikan file konfigurasi (pyproject.toml, dll) selalu ada."""
    essential_files = [
        "pyproject.toml",
        "src/opticargo_agents/config.py",
        "src/opticargo_agents/api.py"
    ]
    for rel_path in essential_files:
        path = BASE_DIR / rel_path
        assert path.exists() and path.is_file(), f"File esensial hilang: {rel_path}"