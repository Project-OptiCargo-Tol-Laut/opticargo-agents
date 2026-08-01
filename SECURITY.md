# Security

Jangan commit `.env`, internal service token, LLM API key, dependency credential, payment data, atau PII nyata. Endpoint `/internal/v1/*` wajib memakai internal authentication dan hanya tersedia pada private network. Prompt, log, trace, metric label, SSE error, dan dependency exception wajib melalui allowlist/redaction. Agents tidak boleh menjalankan booking/payment mutation atau menerima credential transaksi. Kanal pelaporan privat belum tercantum pada materi proyek dan harus ditentukan oleh pemilik organisasi.
