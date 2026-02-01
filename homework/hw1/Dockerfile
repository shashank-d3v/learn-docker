FROM python:3.13.11-slim

# uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# uv creates /app/.venv by default for projects
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only dependency manifests first for better layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies (expects uv.lock to exist if you want fully reproducible builds)
RUN uv sync --frozen

# Copy your repo structure
COPY scripts_ingest/ ./scripts_ingest/
COPY extraction/ ./extraction/
COPY main.py ./main.py
COPY README.md ./README.md

# Ensure data directory exists (useful when mounting volumes too)
RUN mkdir -p /app/extraction/data

# Default: run green parquet ingestion
# Override at runtime to run zone lookup ingestion:
# docker run ... <image> scripts_ingest/ingest_zone_lookup.py --user ...
ENTRYPOINT ["python"]
CMD ["scripts_ingest/ingest_green_parquet.py"]
