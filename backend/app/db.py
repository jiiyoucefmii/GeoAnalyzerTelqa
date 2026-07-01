from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import get_settings


pool = ConnectionPool(
    conninfo=get_settings().database_url,
    min_size=1,
    max_size=10,
    kwargs={"row_factory": dict_row},
    open=False,
)


def open_pool() -> None:
    if pool.closed:
        pool.open(wait=True)


def initialize_database() -> None:
    settings = get_settings()
    if not settings.auto_init_database:
        return
    schema_dir = find_schema_dir()
    if not schema_dir:
        return
    sql_files = [schema_dir / "001_schema.sql", schema_dir / "002_seed.sql"]
    with get_conn() as conn:
        for sql_file in sql_files:
            if sql_file.exists():
                conn.execute(sql_file.read_text(encoding="utf-8"))


def find_schema_dir() -> Path | None:
    current = Path(__file__).resolve()
    candidates = [
        current.parents[2] / "database" / "init",
        current.parents[1] / "database" / "init",
    ]
    for candidate in candidates:
        if (candidate / "001_schema.sql").exists():
            return candidate
    return None


def close_pool() -> None:
    pool.close()


@contextmanager
def get_conn() -> Iterator:
    with pool.connection() as conn:
        yield conn


def normalize_record(value):
    if isinstance(value, dict):
        return {key: normalize_record(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_record(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    return value
