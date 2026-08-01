# Integration tests

## Tujuan

Memverifikasi concrete dependency adapter, compiled LangGraph, internal HTTP, Gateway proxy, metrics scrape, dan resource lifecycle.

## Kondisi eksekusi

Memerlukan wheel resmi dan stack test terisolasi. Dijalankan dengan marker eksplisit dan timeout keseluruhan.

## Tanggung jawab file test

| File | Skenario yang harus diverifikasi |
|---|---|
| `test_langgraph_compiled_route.py` | Memverifikasi integrasi nyata `test_langgraph_compiled_route.py` tanpa mock pada boundary yang dinyatakan. |
| `test_ml_models_http.py` | Memverifikasi integrasi nyata `test_ml_models_http.py` tanpa mock pada boundary yang dinyatakan. |
| `test_knowledge_graph_package.py` | Memverifikasi integrasi nyata `test_knowledge_graph_package.py` tanpa mock pada boundary yang dinyatakan. |
| `test_rag_package.py` | Memverifikasi integrasi nyata `test_rag_package.py` tanpa mock pada boundary yang dinyatakan. |
| `test_api_with_live_dependencies.py` | Memverifikasi integrasi nyata `test_api_with_live_dependencies.py` tanpa mock pada boundary yang dinyatakan. |
| `test_gateway_recommendation_call.py` | Memverifikasi integrasi nyata `test_gateway_recommendation_call.py` tanpa mock pada boundary yang dinyatakan. |
| `test_gateway_sse_proxy.py` | Memverifikasi integrasi nyata `test_gateway_sse_proxy.py` tanpa mock pada boundary yang dinyatakan. |
| `test_prometheus_scrape.py` | Memverifikasi integrasi nyata `test_prometheus_scrape.py` tanpa mock pada boundary yang dinyatakan. |
| `test_runtime_shutdown.py` | Memverifikasi integrasi nyata `test_runtime_shutdown.py` tanpa mock pada boundary yang dinyatakan. |

## Evidence minimum

- Container/image tag.
- Dependency version.
- Request/response trace ID.
- Cleanup dan log artifact.

## Aturan case

Setiap case harus menyatakan requirement, precondition, fixture/version, action, expected result, cleanup, dependency mode, dan evidence. Permanent skip, assertion semu, atau test yang hanya memeriksa bahwa fungsi tidak crash tidak memenuhi gate.
