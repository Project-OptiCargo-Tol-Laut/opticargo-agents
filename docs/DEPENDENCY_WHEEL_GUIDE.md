# Dependency wheel guide

Agents membutuhkan immutable distributions:

```text
opticargo-shared==1.0.0
opticargo-rag-pipeline==1.0.0
opticargo-knowledge-graph==1.0.0
```

## Build umum

Pada masing-masing repository source resmi:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip build
python -m build --wheel
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip build
python -m build --wheel
```

## Verification

- Checkout tag/commit yang disetujui.
- Periksa distribution name/version dalam wheel metadata.
- Catat Python compatibility.
- Hitung SHA-256.
- Install pada clean environment.
- Jalankan contract/import smoke.
- Simpan source repository, tag/commit, builder version, checksum, dan verification result pada manifest.

## Distribution

Private registry atau GitHub Release artifact lebih disarankan. `vendor/` hanya untuk mode offline dan wheel diabaikan Git secara default.
