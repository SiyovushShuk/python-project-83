### Hexlet tests and linter status:
[![Actions Status](https://github.com/SiyovushShuk/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/SiyovushShuk/python-project-83/actions)

### Render

https://python-project-83-sjyn.onrender.com/

### Локальный запуск

```bash
make install
make dev
```

Альтернативные команды:
- Продакшен-режим (gunicorn): `make start` (по умолчанию `PORT=8000`)

### Деплой на Render

Команды сервиса:
- Build Command: `make build`
- Start Command: `make render-start`

Переменные окружения:
- `SECRET_KEY` — обязательно задай в Render
- `PORT` — Render выставляет сам (команды уже используют `$(PORT)`)

Если на Render будет ошибка, связанная с версией Python, попробуй удалить файл `.python-version` из репозитория.
