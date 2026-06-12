# Unicornio Dev

Asistente de desarrollo con IA para arquitectura, refactor, debug, seguridad y performance.

## Stack

- **Backend:** FastAPI + Claude API (Anthropic)
- **Frontend:** React + Vite
- **Infra:** Docker, GitHub Actions

## Inicio rápido

### Requisitos

- Python 3.11+
- Node.js 20+
- Clave de API de Anthropic

### Backend

```bash
cd backend
cp .env.example .env
# Edita .env y agrega CLAUDE_API_KEY

pip install -r requirements/dev.txt
uvicorn app.main:app --reload
```

API disponible en `http://localhost:8000`  
Documentación interactiva: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI disponible en `http://localhost:5173`

### Con Docker

```bash
docker compose up --build
```

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `CLAUDE_API_KEY` | Clave de Anthropic | — |
| `CLAUDE_MODEL` | Modelo de Claude | `claude-sonnet-4-20250514` |
| `API_KEY` | Bearer token opcional para proteger endpoints | vacío |
| `DEBUG` | Modo debug | `false` |
| `CORS_ORIGINS` | Orígenes permitidos (CSV) | `http://localhost:3000,http://localhost:5173` |
| `RATE_LIMIT` | Límite de peticiones | `30/minute` |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/health` | Estado del servicio |
| POST | `/api/v1/architect/analyze` | Análisis de arquitectura |
| POST | `/api/v1/refactor/code` | Refactor de código |
| POST | `/api/v1/debug/solve` | Resolución de errores |
| POST | `/api/v1/security/audit` | Auditoría de seguridad |
| POST | `/api/v1/performance/analyze` | Análisis de performance |

## Desarrollo

```bash
make install   # instala dependencias
make test      # ejecuta tests del backend
make lint      # ruff + black
make run       # backend en modo desarrollo
make frontend  # frontend en modo desarrollo
```

## Seguridad

- Configura `API_KEY` en producción para exigir `Authorization: Bearer <token>`.
- No subas `.env` al repositorio.
- Rota cualquier credencial que haya quedado expuesta en remotos git.

## Licencia

MIT
