FROM python:3.10-slim

WORKDIR /app

# Set PYTHONPATH so absolute imports work
ENV PYTHONPATH=/app/src

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) If in production, you would copy the shared libraries and install them here as well
# COPY ../opticargo-shared /shared
# RUN pip install -e /shared

# Copy the rest of the application
COPY . .

# Install the agent package itself
RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "opticargo_agents.orchestrator.serve:app", "--host", "0.0.0.0", "--port", "8000"]
