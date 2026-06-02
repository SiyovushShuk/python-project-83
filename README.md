
[![Actions Status](https://github.com/SiyovushShuk/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/SiyovushShuk/python-project-83/actions)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=SiyovushShuk_python-project-83&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=SiyovushShuk_python-project-83)

## Page Analyzer

Page Analyzer - web app that lets you add websites, run checks, and view basic SEO analysis results:
- page availability (HTTP status code)
- `<h1>`
- `<title>`
- `<meta name="description">`

### Demo (Render)

You can check a website for availability and basic SEO with this URL:

https://python-project-83-sjyn.onrender.com/

### How to use

- Open the demo homepage or your locally running app
- Enter a URL and click “Check” — the site will be saved to the database
- Open the “Sites” page and choose the added URL
- Click “Run check” — a new record will appear in the checks table

### Dependencies

| Package | Purpose |
| --- | --- |
| Flask | Web framework (routing, request handling, templates). |
| gunicorn | WSGI server for running the app in production. |
| python-dotenv | Loads environment variables from `.env` for local development. |
| psycopg[binary] | PostgreSQL driver for database connections and queries. |
| requests | HTTP client for fetching pages during checks. |
| beautifulsoup4 | HTML parsing to extract `<h1>`, `<title>`, and `description`. |
| validators | URL validation before saving and checking websites. |
| pytest | Test framework (dev dependency). |
| ruff | Linter (dev dependency). |
| playwright | Browser automation framework used for end-to-end testing (runs real Chromium browser). | 

### Local run

```bash
make install
make dev
```

Alternative commands:
- Production mode (gunicorn): `make start` (defaults to `PORT=8000`)

### Deploy to Render

Service commands:
- Build Command: `make build`
- Start Command: `make render-start`

Environment variables:
- `SECRET_KEY` — required
- `PORT` — Render sets it automatically (commands already use `$(PORT)`)

If you run into a Python version error on Render, try removing the `.python-version` file from the repository.
