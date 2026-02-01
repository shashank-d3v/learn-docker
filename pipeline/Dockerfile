FROM python:3.13.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked

# Copy both scripts
COPY scripts_ingest/ingest_data.py scripts_ingest/ingest_zones.py ./pipeline/

# Default command runs ingest_data, but you can override it at runtime
ENTRYPOINT ["python", "-m", "pipeline.ingest_data"]
