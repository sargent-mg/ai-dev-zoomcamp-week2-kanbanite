# Kanbanite

A small Kanban board app with a static HTML/CSS/JS frontend and a FastAPI backend.

## Project structure

- `frontent/` — static frontend UI files.
- `backend/` — FastAPI backend package and tests.
- `openapi.yaml` — OpenAPI contract.

## Run the frontend

Serve the static frontend locally:

```sh
cd "/Users/adrianlr/Documents/Courses/AI Dev Tools Zoomcamp 2026/ai-dev-zoomcamp-week2-kanbanite"
python3 -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/index.html
```

## Run the backend

From the backend directory:

```sh
cd "/Users/adrianlr/Documents/Courses/AI Dev Tools Zoomcamp 2026/ai-dev-zoomcamp-week2-kanbanite/backend"
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

The frontend API client points to:

```text
http://127.0.0.1:8001
```

## Run tests

```sh
cd "/Users/adrianlr/Documents/Courses/AI Dev Tools Zoomcamp 2026/ai-dev-zoomcamp-week2-kanbanite/backend"
uv run pytest tests/test_api.py
```

## Current implementation notes

- The frontend uses a centralized request wrapper in `frontent/api.js`.
- The backend exposes the Kanban board contract through `/board`, `/board/reset`, `/cards/{card_id}`, and `/cards/{card_id}/move`.
- A SQLAlchemy-backed store abstraction lives in `backend/src/backend/store.py` and keeps the API database-agnostic.
