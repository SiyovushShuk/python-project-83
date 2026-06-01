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

### Hexlet tests and linter status:
[![Actions Status](https://github.com/SiyovushShuk/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/SiyovushShuk/python-project-83/actions)

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
