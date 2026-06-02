import importlib

app_module = importlib.import_module("page_analyzer.app")


def test_index_page_renders():
    client = app_module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'name="url"' in html
    assert "bootstrap" in html.lower()
