# Testing

## Tujuan

Menetapkan bukti berlapis dari package boundary sampai critical end-to-end workflow. Test harus membedakan deterministic unit behavior dari dependency integration aktual.

## Kondisi eksekusi

Unit/contract dapat berjalan tanpa Infra melalui fake ports. Smoke memerlukan package build. Integration/E2E/resilience memerlukan dependency wheel dan stack Infra yang sehat sesuai marker.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `architecture/` | Memverifikasi layer architecture. Detail per file terdapat pada README folder tersebut. |
| `contract/` | Memverifikasi layer contract. Detail per file terdapat pada README folder tersebut. |
| `unit/` | Memverifikasi layer unit. Detail per file terdapat pada README folder tersebut. |
| `unit/clients/` | Memverifikasi layer unit/clients. Detail per file terdapat pada README folder tersebut. |
| `unit/integrations/` | Memverifikasi layer unit/integrations. Detail per file terdapat pada README folder tersebut. |
| `unit/nodes/` | Memverifikasi layer unit/nodes. Detail per file terdapat pada README folder tersebut. |
| `unit/orchestrator/` | Memverifikasi layer unit/orchestrator. Detail per file terdapat pada README folder tersebut. |
| `unit/cli/` | Memverifikasi layer unit/cli. Detail per file terdapat pada README folder tersebut. |
| `smoke/` | Memverifikasi layer smoke. Detail per file terdapat pada README folder tersebut. |
| `integration/` | Memverifikasi layer integration. Detail per file terdapat pada README folder tersebut. |
| `e2e/` | Memverifikasi layer e2e. Detail per file terdapat pada README folder tersebut. |
| `resilience/` | Memverifikasi layer resilience. Detail per file terdapat pada README folder tersebut. |
| `evaluation/` | Memverifikasi layer evaluation. Detail per file terdapat pada README folder tersebut. |
| `performance/` | Memverifikasi layer performance. Detail per file terdapat pada README folder tersebut. |
| `security/` | Memverifikasi layer security. Detail per file terdapat pada README folder tersebut. |

## Evidence minimum

- Requirement ID dan acceptance yang diuji.
- Fixture/version dependency yang digunakan.
- Expected route, trace, response, metric, dan failure mode.
- Command reproducible serta artifact report untuk integration/performance/evaluation.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
