# Smoke tests

## Tujuan

Membuktikan artifact dapat di-install, import, dikonfigurasi, diboot, dan mencapai dependency dasar sebelum E2E.

## Kondisi eksekusi

Sebagian test berjalan offline setelah wheel tersedia; connectivity/readiness memerlukan Infra aktif.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_repository_structure.py` | Menjalankan preflight `test_repository_structure.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_package_import.py` | Menjalankan preflight `test_package_import.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_package_metadata.py` | Menjalankan preflight `test_package_metadata.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_environment_contract.py` | Menjalankan preflight `test_environment_contract.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_shared_wheel.py` | Menjalankan preflight `test_shared_wheel.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_rag_wheel.py` | Menjalankan preflight `test_rag_wheel.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_knowledge_graph_wheel.py` | Menjalankan preflight `test_knowledge_graph_wheel.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_app_routes.py` | Menjalankan preflight `test_app_routes.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_liveness.py` | Menjalankan preflight `test_liveness.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_readiness.py` | Menjalankan preflight `test_readiness.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_metrics_endpoint.py` | Menjalankan preflight `test_metrics_endpoint.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_healthcheck_command.py` | Menjalankan preflight `test_healthcheck_command.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_doctor_command.py` | Menjalankan preflight `test_doctor_command.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |
| `test_dependency_connectivity.py` | Menjalankan preflight `test_dependency_connectivity.py` dan gagal cepat dengan pesan yang dapat ditindaklanjuti. |

## Evidence minimum

- Package version.
- Route inventory.
- Dependency wheel checksum/version.
- Readiness/metrics response.
- Infra endpoint report.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
