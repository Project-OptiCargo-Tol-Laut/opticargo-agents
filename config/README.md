# Configuration

Folder ini memisahkan kontrak Infra dari konfigurasi khusus Agents.

| File | Fungsi |
|---|---|
| `infra.example.env` | Salinan acuan environment lintas repository yang diberikan bersama dokumen proyek. Nilai port dan service name pada file ini menjadi referensi integrasi. |
| `agents.env.example` | Daftar key yang dibaca Agents. Nilai sengaja dikosongkan agar secret, model, threshold, dan policy tidak ditetapkan tanpa keputusan environment. |

## Aturan

- `.env` aktual tidak boleh masuk Git.
- `AGENTS_INTERNAL_URL` pada network Infra mengarah ke `http://agents:8000`.
- `ML_MODELS_INTERNAL_URL` mengarah ke `http://ml-models:8000`.
- `NEO4J_URI` dan `QDRANT_URL` memakai internal service DNS saat berjalan dalam Compose/Kubernetes.
- Host port tidak boleh ditambahkan hanya untuk convenience bila service memang internal-only.
- Semua secret berasal dari secret store atau environment injection.
- Perubahan key harus disinkronkan dengan Settings model, Infra manifest, operations guide, dan smoke test.
