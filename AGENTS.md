# AGENTS.md

## Cursor Cloud specific instructions

Unicornio Dev is a single product (an AI dev assistant) exposed through a FastAPI
backend plus three thin clients (React web UI, a Typer CLI, and a VS Code/Cursor
extension). The backend is the only mandatory service; every client just calls it.

Standard install/lint/test/run commands live in the root `Makefile`, `README.md`,
and `.github/workflows/tests.yml`. Prefer those instead of re-deriving commands.

### Services

| Service | Dir | Run (dev) | Notes |
|---------|-----|-----------|-------|
| Backend API | `backend` | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | Core service, port 8000. Docs at `/docs`, health at `/api/v1/health`. |
| Frontend web UI | `frontend` | `npm run dev -- --host 0.0.0.0` | Vite dev server, port 5173. Proxies `/api` → `http://localhost:8000` (see `vite.config.js`), so the backend must be running for the UI to work. |
| CLI | `backend/cli` | `python -m cli` or `unicornio` | Optional client; talks to the backend. |
| VS Code extension | `extension` | `npm run compile` | Optional client; needs an Extension Dev Host to actually run. |

### Non-obvious gotchas

- Python console scripts (`uvicorn`, `pytest`, `ruff`, `black`, `unicornio`) install
  to `~/.local/bin`, which is added to `PATH` via `~/.bashrc`. New non-login shells
  may need `export PATH="$HOME/.local/bin:$PATH"` before these commands resolve.
- `backend/.env` is **optional** for local dev: every setting in `app/config.py`
  has a default (SQLite DB, dev `JWT_SECRET`), so the backend starts without it.
  Copy `backend/.env.example` → `backend/.env` only to override defaults.
- AI endpoints (`/api/v1/architect`, `/refactor`, `/debug`, `/security`,
  `/performance`, and the v2 SSE routes) require a real `CLAUDE_API_KEY` and return
  HTTP 503 without one. Auth, projects, history, and health work without any key.
- Local DB defaults to SQLite at `backend/unicornio.db` (auto-created on startup,
  not committed). Postgres is only used by `docker-compose.yml` / production.
- Registration requires a valid email domain (e.g. `@example.com`); reserved TLDs
  like `.test` are rejected by `email-validator`. The register field is `name`
  (not `full_name`).
- Backend tests enforce `--cov-fail-under=80` (configured in CI). Run them from the
  `backend` dir: `pytest tests/`.
