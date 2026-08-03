FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/workspace/opticargo-shared/src:/workspace/opticargo-knowledge-graph/src:/workspace/opticargo-rag-pipeline/src:/workspace/opticargo-agents/src

WORKDIR /workspace

COPY opticargo-shared ./opticargo-shared
COPY opticargo-knowledge-graph ./opticargo-knowledge-graph
COPY opticargo-rag-pipeline ./opticargo-rag-pipeline
COPY opticargo-agents ./opticargo-agents

RUN python -m pip install --upgrade pip \
    && python -m pip install ./opticargo-shared ./opticargo-knowledge-graph ./opticargo-rag-pipeline ./opticargo-agents \
    && python -m pip install "uvicorn>=0.30,<1.0"

EXPOSE 8000

CMD ["uvicorn", "opticargo_agents.api:app", "--host", "0.0.0.0", "--port", "8000"]
