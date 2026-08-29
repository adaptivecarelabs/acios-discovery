FROM python:3.14-slim AS base

WORKDIR /app

# System dependencies: libpq for psycopg2, build tools for any
# source-built wheels (bcrypt, cryptography, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Install the project itself plus its declared dependencies.
# --break-system-packages matches the pattern used throughout
# local development in this project; the container has no
# competing system Python packages to worry about, so this is
# lower-risk here than on a shared dev machine.
RUN pip install --no-cache-dir --break-system-packages -e .

EXPOSE 8000

# Run migrations, then start the API. If migrations fail, the
# container exits non-zero rather than serving traffic against
# a schema it doesn't match.
CMD alembic upgrade head && \
    uvicorn acios_discovery.api.app:app --host 0.0.0.0 --port 8000
