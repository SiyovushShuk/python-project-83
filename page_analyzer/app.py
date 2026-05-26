import os
from urllib.parse import urlparse

import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.db import create_url, get_url, list_urls

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")


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


@app.post("/urls")
def urls_create():
    raw_url = request.form.get("url", "").strip()
    error = validate_url(raw_url)
    if error:
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
    return render_template("urls/show.html", url=url)
