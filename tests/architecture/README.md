# Architecture tests

## Tujuan

Menjaga dependency direction dan ownership boundary yang tidak boleh rusak oleh refactor.

## Kondisi eksekusi

Berjalan cepat tanpa network, database, model, atau provider.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_internal_only_service.py` | Tidak terdapat public business route atau assumption browser-to-Agents. |
| `test_no_transaction_mutation.py` | Tidak ada booking/payment/user mutation client, SQL writer, atau persistence owner di package. |
| `test_no_sibling_source_imports.py` | RAG/KG/Shared dipakai sebagai installed distribution, bukan relative sys.path/sibling source. |
| `test_dependency_direction.py` | Node bergantung pada ports/state; adapter tidak bergantung kembali pada orchestrator business flow. |
| `test_no_eager_network_on_import.py` | Import package/app tidak membuka HTTP, Neo4j, atau Qdrant connection. |
| `test_no_secret_defaults.py` | Source/config tidak menyediakan production-like secret default. |

## Evidence minimum

- Import graph report.
- Forbidden dependency scan.
- Public route inventory.
- Secret/static scan result.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
