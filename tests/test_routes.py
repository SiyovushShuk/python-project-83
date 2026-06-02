from __future__ import annotations

import importlib

import requests

app_module = importlib.import_module("page_analyzer.app")


def test_urls_show_not_found(monkeypatch):
    monkeypatch.setattr(app_module, "get_url", lambda url_id: None)
    client = app_module.app.test_client()
    resp = client.get("/urls/1")
    assert resp.status_code == 404


def test_url_checks_create_not_found(monkeypatch):
    monkeypatch.setattr(app_module, "get_url", lambda url_id: None)
    client = app_module.app.test_client()
    resp = client.post("/urls/1/checks")
    assert resp.status_code == 404


def test_urls_create_invalid_url_shows_flash(monkeypatch):
    client = app_module.app.test_client()
    resp = client.post("/urls", data={"url": "not-a-url"})
    assert resp.status_code == 422
    html = resp.data.decode("utf-8")
    assert "Некорректный URL" in html
    assert "alert" in html


def test_urls_create_new_url_redirects(monkeypatch):
    monkeypatch.setattr(app_module, "create_url", lambda name: (1, True))
    monkeypatch.setattr(
        app_module,
        "get_url",
        lambda url_id: {"id": 1, "name": "https://example.com", "created_at": "2026-01-01"},
    )
    monkeypatch.setattr(app_module, "list_checks", lambda url_id: [])

    client = app_module.app.test_client()
    resp = client.post("/urls", data={"url": "https://example.com"}, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Страница успешно добавлена" in html
    assert "https://example.com" in html


def test_urls_create_existing_url_redirects(monkeypatch):
    monkeypatch.setattr(app_module, "create_url", lambda name: (1, False))
    monkeypatch.setattr(
        app_module,
        "get_url",
        lambda url_id: {"id": 1, "name": "https://example.com", "created_at": "2026-01-01"},
    )
    monkeypatch.setattr(app_module, "list_checks", lambda url_id: [])

    client = app_module.app.test_client()
    resp = client.post("/urls", data={"url": "https://example.com"}, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Страница уже существует" in html


def test_urls_index_renders_table(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "list_urls",
        lambda: [
            {
                "id": 1,
                "name": "https://example.com",
                "created_at": "2026-01-01",
                "last_check": None,
                "last_status_code": None,
            }
        ],
    )
    client = app_module.app.test_client()
    resp = client.get("/urls")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert 'data-test="urls"' in html
    assert "https://example.com" in html


def test_url_checks_create_success_creates_check(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "get_url",
        lambda url_id: {"id": 1, "name": "https://example.com", "created_at": "2026-01-01"},
    )
    monkeypatch.setattr(
        app_module,
        "list_checks",
        lambda url_id: [],
    )

    created: dict[str, object] = {}

    def fake_create_check(url_id, status_code, h1, title, description):
        created.update(
            {
                "url_id": url_id,
                "status_code": status_code,
                "h1": h1,
                "title": title,
                "description": description,
            }
        )
        return 1

    monkeypatch.setattr(app_module, "create_check", fake_create_check)

    class FakeResponse:
        status_code = 200
        text = "<html><head><title>T</title></head><body><h1>H</h1></body></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(app_module.requests, "get", lambda *a, **k: FakeResponse())

    client = app_module.app.test_client()
    resp = client.post("/urls/1/checks", follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Страница успешно проверена" in html
    assert created["url_id"] == 1
    assert created["status_code"] == 200
    assert created["h1"] == "H"
    assert created["title"] == "T"


def test_url_checks_create_failure_does_not_create_check(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "get_url",
        lambda url_id: {"id": 1, "name": "https://example.com", "created_at": "2026-01-01"},
    )
    monkeypatch.setattr(app_module, "list_checks", lambda url_id: [])

    called = {"create_check": False}

    def fake_create_check(*args, **kwargs):
        called["create_check"] = True
        return 1

    monkeypatch.setattr(app_module, "create_check", fake_create_check)

    def raising(*args, **kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(app_module.requests, "get", raising)

    client = app_module.app.test_client()
    resp = client.post("/urls/1/checks", follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Произошла ошибка при проверке" in html
    assert called["create_check"] is False


def test_url_checks_create_http_error_does_not_create_check(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "get_url",
        lambda url_id: {"id": 1, "name": "https://example.com", "created_at": "2026-01-01"},
    )
    monkeypatch.setattr(app_module, "list_checks", lambda url_id: [])

    called = {"create_check": False}

    def fake_create_check(*args, **kwargs):
        called["create_check"] = True
        return 1

    monkeypatch.setattr(app_module, "create_check", fake_create_check)

    class FakeResponse:
        status_code = 500
        text = ""

        def raise_for_status(self):
            raise requests.HTTPError("server error")

    monkeypatch.setattr(app_module.requests, "get", lambda *a, **k: FakeResponse())

    client = app_module.app.test_client()
    resp = client.post("/urls/1/checks", follow_redirects=True)
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Произошла ошибка при проверке" in html
    assert called["create_check"] is False
