# Infra ports dan endpoints

Acuan berasal dari `config/infra.example.env`.

## Internal service endpoints

| Dependency | Endpoint container |
|---|---|
| Agents | `http://agents:8000` |
| ML Models | `http://ml-models:8000` |
| Neo4j Bolt | `bolt://neo4j:7687` |
| Qdrant | `http://qdrant:6333` |
| Gateway | `http://gateway-api:8000` |

## Host-facing ports pada acuan Infra

| Service | Host port |
|---|---:|
| Public HTTP/Nginx | 8080 |
| Gateway direct development mapping | 8000 |
| Grafana | 3001 |
| Prometheus | 9090 |
| Alertmanager | 9093 |
| MinIO Console | 9001 |
| Neo4j HTTP | 7474 |
| PostgreSQL | 5433 |

Agents tidak memiliki host/public port tersendiri pada acuan. Local direct run boleh memakai loopback port sementara yang tidak dianggap contract Infra.

## Command

```text
uvicorn opticargo_agents.api:app --host 0.0.0.0 --port 8000 --proxy-headers
```

## Rules

- Gunakan internal DNS saat container berjalan dalam network Infra.
- Jangan menggunakan `localhost` dari dalam container untuk dependency lain.
- Tidak menambahkan ingress public untuk Agents.
- Readiness harus memeriksa dependency yang diwajibkan environment.
