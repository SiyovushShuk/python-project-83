import os
from datetime import date

import psycopg
from psycopg.rows import dict_row


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return database_url


def get_connection():
    return psycopg.connect(get_database_url())


def create_url(name: str) -> tuple[int, bool]:
    query = """
        INSERT INTO urls (name, created_at)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING
        RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (name, date.today()))
            row = cur.fetchone()
            if row:
                return row["id"], True

            cur.execute("SELECT id FROM urls WHERE name = %s;", (name,))
            return cur.fetchone()["id"], False


def get_url(url_id: int):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT id, name, created_at FROM urls WHERE id = %s;", (url_id,))
            return cur.fetchone()


def list_urls():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, name, created_at
                FROM urls
                ORDER BY id DESC;
                """
            )
            return cur.fetchall()
