# syntax=docker/dockerfile:1
FROM python:3.10

ENV PYTHONUNBUFFERED=1

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

WORKDIR /app/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy workspace manifests first so dependency install layer is cached.
# NOTE: BuildKit --mount flags are intentionally avoided here because
# Railway's image builder does not parse them.
COPY pyproject.toml uv.lock /app/
COPY ./backend/pyproject.toml /app/backend/pyproject.toml

# Install dependencies (without the workspace package itself)
RUN uv sync --frozen --no-install-workspace --package app

COPY ./backend/scripts /app/backend/scripts

COPY ./backend/alembic.ini /app/backend/alembic.ini

COPY ./backend/app /app/backend/app

# Sync the project
RUN uv sync --frozen --package app

WORKDIR /app/backend/

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
