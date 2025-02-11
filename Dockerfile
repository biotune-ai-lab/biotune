FROM python:3.11-slim-bookworm

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

# Install uv in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -LsSf https://astral.sh/uv/0.5.21/install.sh | sh && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

COPY models/ /app/models/

COPY .python-version config.py llm_client.py models.py models.yaml service.py pyproject.toml uv.lock /app/

RUN uv sync

ENTRYPOINT ["uv", "run", "uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]
