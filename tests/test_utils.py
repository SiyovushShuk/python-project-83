import importlib

app_module = importlib.import_module("page_analyzer.app")


def test_truncate_200_empty():
    assert app_module.truncate_200(None) == ""
    assert app_module.truncate_200("") == ""


def test_truncate_200_short():
    assert app_module.truncate_200("hello") == "hello"


def test_truncate_200_long():
    value = "a" * 201
    truncated = app_module.truncate_200(value)
    assert truncated.endswith("...")
    assert len(truncated) == 203


def test_normalize_url():
    assert app_module.normalize_url("https://Hexly.edu.kz/path") == "https://hexly.edu.kz"


def test_validate_url_ok():
    assert app_module.validate_url("https://example.com") is None


def test_validate_url_invalid_cases():
    assert app_module.validate_url("") == "Некорректный URL"
    assert app_module.validate_url("not-a-url") == "Некорректный URL"
    assert app_module.validate_url("https://") == "Некорректный URL"
    assert app_module.validate_url("https://" + ("a" * 300) + ".com") == "Некорректный URL"


def test_extract_seo_data():
    html = """
    <html>
      <head>
        <title> Awesome page </title>
        <meta name="description" content="  Statements of great people  ">
      </head>
      <body>
        <h1> Do not expect a miracle, miracles yourself! </h1>
      </body>
    </html>
    """
    seo = app_module.extract_seo_data(html)
    assert seo["h1"] == "Do not expect a miracle, miracles yourself!"
    assert seo["title"] == "Awesome page"
    assert seo["description"] == "Statements of great people"


def test_extract_seo_data_missing_fields():
    seo = app_module.extract_seo_data("<html><body>No tags</body></html>")
    assert seo["h1"] is None
    assert seo["title"] is None
    assert seo["description"] is None
