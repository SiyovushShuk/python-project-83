import os
from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from requests import RequestException

from page_analyzer.db import create_check, create_url, get_url, list_checks, list_urls

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")


@app.template_filter("truncate_200")
def truncate_200(value: str | None) -> str:
    if not value:
        return ""
    return value if len(value) <= 200 else f"{value[:200]}..."


@app.get("/")
def index():
    return render_template("index.html")


def normalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()
    return f"{scheme}://{netloc}"


def validate_url(raw_url: str) -> str | None:
    if not raw_url:
        return "Некорректный URL"
    if len(raw_url) > 255:
        return "Некорректный URL"
    if not validators.url(raw_url):
        return "Некорректный URL"
    normalized = normalize_url(raw_url)
    if len(normalized) > 255:
        return "Некорректный URL"
    if normalized in ("http://", "https://"):
        return "Некорректный URL"
    return None


def extract_seo_data(html: str) -> dict[str, str | None]:
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    title = soup.find("title")
    description_meta = soup.find(
        "meta", attrs={"name": lambda v: isinstance(v, str) and v.lower() == "description"}
    )

    description = None
    if description_meta is not None:
        content = description_meta.get("content")
        if isinstance(content, str):
            description = content.strip() or None

    return {
        "h1": h1.get_text(strip=True) if h1 else None,
        "title": title.get_text(strip=True) if title else None,
        "description": description,
    }


@app.post("/urls")
def urls_create():
    raw_url = request.form.get("url", "").strip()
    error = validate_url(raw_url)
    if error:
        flash(error, "danger")
        return render_template("index.html", url=raw_url, error=error), 422

    normalized = normalize_url(raw_url)
    url_id, created = create_url(normalized)
    if created:
        flash("Страница успешно добавлена", "success")
    else:
        flash("Страница уже существует", "info")
    return redirect(url_for("urls_show", url_id=url_id))


@app.get("/urls")
def urls_index():
    urls = list_urls()
    return render_template("urls/index.html", urls=urls)


@app.get("/urls/<int:url_id>")
def urls_show(url_id: int):
    url = get_url(url_id)
    if not url:
        return "Not Found", 404
    checks = list_checks(url_id)
    return render_template("urls/show.html", url=url, checks=checks)


@app.post("/urls/<int:url_id>/checks")
def url_checks_create(url_id: int):
    url = get_url(url_id)
    if not url:
        return "Not Found", 404

    try:
        response = requests.get(
            url["name"],
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PageAnalyzer/1.0)"},
        )
        response.raise_for_status()
        seo = extract_seo_data(response.text)
        create_check(
            url_id,
            response.status_code,
            seo["h1"],
            seo["title"],
            seo["description"],
        )
        flash("Страница успешно проверена", "success")
    except RequestException:
        flash("Произошла ошибка при проверке", "danger")
    return redirect(url_for("urls_show", url_id=url_id))
