# Vendor artifacts

Folder ini hanya untuk mode offline atau competition environment yang tidak memiliki private package registry.

Artifact yang mungkin diperlukan:

```text
opticargo_shared-1.0.0-py3-none-any.whl
opticargo_rag_pipeline-1.0.0-py3-none-any.whl
opticargo_knowledge_graph-1.0.0-py3-none-any.whl
```

Wheel tidak dibundel pada struktur awal dan diabaikan oleh Git. Sumber repository, tag/commit, build command, distribution name, version, Python compatibility, SHA-256, dan verification result harus dicatat pada manifest terpisah. Detail terdapat pada [`docs/DEPENDENCY_WHEEL_GUIDE.md`](../docs/DEPENDENCY_WHEEL_GUIDE.md).
