from __future__ import annotations

import page_analyzer.db as db_module


class FakeCursor:
    def __init__(self, fetchone_results=None, fetchall_results=None):
        self._fetchone_results = list(fetchone_results or [])
        self._fetchall_results = fetchall_results
        self.queries: list[tuple[str, tuple | None]] = []

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchone(self):
        if not self._fetchone_results:
            return None
        return self._fetchone_results.pop(0)

    def fetchall(self):
        return self._fetchall_results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, cursor: FakeCursor):
        self._cursor = cursor

    def cursor(self, row_factory=None):
        return self._cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_get_database_url_env_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    try:
        db_module.get_database_url()
    except RuntimeError as e:
        assert "DATABASE_URL is not set" in str(e)
    else:
        raise AssertionError("Expected RuntimeError")


def test_get_database_url_ok(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    assert db_module.get_database_url().startswith("postgresql://")


def test_get_connection_uses_psycopg(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    sentinel = object()
    monkeypatch.setattr(db_module.psycopg, "connect", lambda dsn: sentinel)
    assert db_module.get_connection() is sentinel



def test_create_url_created(monkeypatch):
    cursor = FakeCursor(fetchone_results=[{"id": 10}])
    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConnection(cursor))
    url_id, created = db_module.create_url("https://example.com")
    assert (url_id, created) == (10, True)


def test_create_url_existing(monkeypatch):
    cursor = FakeCursor(fetchone_results=[None, {"id": 5}])
    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConnection(cursor))
    url_id, created = db_module.create_url("https://example.com")
    assert (url_id, created) == (5, False)


def test_get_url(monkeypatch):
    cursor = FakeCursor(fetchone_results=[{"id": 1, "name": "https://example.com"}])
    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConnection(cursor))
    assert db_module.get_url(1)["id"] == 1


def test_list_urls(monkeypatch):
    rows = [{"id": 1, "name": "https://example.com"}]
    cursor = FakeCursor(fetchall_results=rows)
    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConnection(cursor))
    assert db_module.list_urls() == rows


def test_create_check(monkeypatch):
    cursor = FakeCursor(fetchone_results=[{"id": 7}])
    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConnection(cursor))
    assert (
        db_module.create_check(1, 200, "h1", "title", "desc")
        == 7
    )


def test_list_checks(monkeypatch):
    rows = [{"id": 1, "status_code": 200}]
    cursor = FakeCursor(fetchall_results=rows)
    monkeypatch.setattr(db_module, "get_connection", lambda: FakeConnection(cursor))
    assert db_module.list_checks(1) == rows
