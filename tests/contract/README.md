# Contract tests

## Tujuan

Memastikan schema, header, route, SSE, package version, dan dependency ports kompatibel lintas repository.

## Kondisi eksekusi

Berjalan tanpa live dependency; memakai JSON/schema snapshot atau fake adapter.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_gateway_recommendation_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_gateway_recommendation_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_gateway_chat_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_gateway_chat_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_sse_event_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_sse_event_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_error_envelope.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_error_envelope.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_health_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_health_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_metrics_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_metrics_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_internal_auth_header.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_internal_auth_header.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_dependency_protocols.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_dependency_protocols.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_shared_version_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_shared_version_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_rag_package_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_rag_package_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_knowledge_graph_package_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_knowledge_graph_package_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_ml_models_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_ml_models_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |
| `test_version_contract.py` | Memverifikasi contract yang dinyatakan oleh nama file `test_version_contract.py` termasuk unknown field, enum, optionality, dan version behavior. |

## Evidence minimum

- Schema snapshot/diff.
- Backward compatibility result.
- Header dan SSE golden samples.
- Dependency distribution/version evidence.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
