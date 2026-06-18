"""Vercel Python serverless entry point for the FastAPI backend.

Vercel routes every request matching `/api/(.*)` to this module (see vercel.json
rewrites) and serves the exported ASGI `app`. The original request path is
preserved, so FastAPI matches its `/api/v1/...` routes normally.
"""
import os
import re
import sys

# The application package lives in ../backend/app
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, BACKEND_DIR)


def _bootstrap_env() -> None:
    """Translate the env vars injected by the Vercel/Neon Postgres integration
    into the names the backend's Settings model expects, and provide sane
    defaults for the few non-secret app vars. This lets the function run with
    only the database connection wired through the Vercel Storage integration.
    """

    def _from_url(url: str) -> dict:
        m = re.match(
            r"postgres(?:ql)?://([^:]+):([^@]+)@([^/:]+)(?::(\d+))?/([^?]+)", url
        )
        if not m:
            return {}
        user, pw, host, port, db = m.groups()
        return {
            "user": user,
            "pw": pw,
            "host": host,
            "port": port or "5432",
            "db": db,
        }

    # Prefer the discrete PG* vars; fall back to parsing a connection URL.
    url = (
        os.environ.get("POSTGRES_URL")
        or os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or os.environ.get("DATABASE_URL_UNPOOLED")
        or ""
    )
    parts = _from_url(url)
    host = os.environ.get("PGHOST") or os.environ.get("POSTGRES_HOST") or parts.get("host")
    user = os.environ.get("PGUSER") or os.environ.get("POSTGRES_USER") or parts.get("user")
    pw = os.environ.get("PGPASSWORD") or os.environ.get("POSTGRES_PASSWORD") or parts.get("pw")
    db = os.environ.get("PGDATABASE") or os.environ.get("POSTGRES_DATABASE") or parts.get("db")

    if host and "POSTGRES_SERVER" not in os.environ:
        os.environ["POSTGRES_SERVER"] = host
    if user:
        os.environ["POSTGRES_USER"] = user
    if pw:
        os.environ["POSTGRES_PASSWORD"] = pw
    if db:
        os.environ["POSTGRES_DB"] = db
    os.environ.setdefault("POSTGRES_PORT", parts.get("port", "5432"))

    os.environ.setdefault("PROJECT_NAME", "Full Stack FastAPI Template")
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
    os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "changethis123")


_bootstrap_env()

from app.main import app  # noqa: E402

# Vercel's Python runtime detects the ASGI `app` object and serves it.
__all__ = ["app"]
