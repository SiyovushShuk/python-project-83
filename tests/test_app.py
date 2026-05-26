from page_analyzer import app


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Анализатор страниц" in html
    assert "bootstrap" in html.lower()
