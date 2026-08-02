# Fixture `ml`

Fixture pada folder ini mendukung pengujian Agents tanpa memasukkan data production. Semua file data masih kosong.

## File

- `trained_score.json` — data untuk scenario yang dinyatakan pada nama file.
- `heuristic_score.json` — data untuk scenario yang dinyatakan pada nama file.
- `invalid_score.json` — data untuk scenario yang dinyatakan pada nama file.
- `hard_constraint_failure.json` — data untuk scenario yang dinyatakan pada nama file.

## Aturan fixture

- Gunakan stable UUID dan timestamp UTC yang reproducible.
- Tandai data synthetic serta versi schema/dataset.
- Jangan memasukkan token, API key, PII nyata, document content lengkap, atau raw payment/provider data.
- Expected result harus berasal dari requirement/contract, bukan disalin dari output implementation yang sedang diuji.
- Fixture dependency harus menyatakan model mode, graph/index version, dan score/evidence assumptions.
