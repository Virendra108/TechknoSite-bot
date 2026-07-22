import sys
from pathlib import Path
import os

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _db_config() -> dict[str, object]:
    load_dotenv(ROOT / ".env")
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": _required("DB_NAME"),
        "user": _required("DB_USER"),
        "password": _required("DB_PASSWORD"),
    }


def ensure_database_exists() -> None:
    cfg = _db_config()
    with psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname="postgres",
        user=cfg["user"],
        password=cfg["password"],
    ) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (cfg["dbname"],))
            if cur.fetchone():
                return
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(str(cfg["dbname"]))))


def main() -> None:
    ensure_database_exists()
    cfg = _db_config()
    with psycopg2.connect(**cfg) as conn, conn.cursor() as cur:
        cur.execute((ROOT / "db" / "schema.sql").read_text(encoding="utf-8"))
    print("Database schema is ready.")


if __name__ == "__main__":
    main()
