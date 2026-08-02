# Fixture `requests`

Fixture pada folder ini mendukung pengujian Agents tanpa memasukkan data production. Semua file data masih kosong.

## File

- `recommendation.json` — data untuk scenario yang dinyatakan pada nama file.
- `chat_regulation.json` — data untuk scenario yang dinyatakan pada nama file.
- `chat_matching.json` — data untuk scenario yang dinyatakan pada nama file.
- `chat_route.json` — data untuk scenario yang dinyatakan pada nama file.
- `chat_analytics.json` — data untuk scenario yang dinyatakan pada nama file.

## Aturan fixture

- Gunakan stable UUID dan timestamp UTC yang reproducible.
- Tandai data synthetic serta versi schema/dataset.
- Jangan memasukkan token, API key, PII nyata, document content lengkap, atau raw payment/provider data.
- Expected result harus berasal dari requirement/contract, bukan disalin dari output implementation yang sedang diuji.
- Fixture dependency harus menyatakan model mode, graph/index version, dan score/evidence assumptions.
