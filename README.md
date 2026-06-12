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
| `DATABASE_URL` | Conexión a base de datos | `sqlite+aiosqlite:///./unicornio.db` |
| `JWT_SECRET` | Secreto para firmar tokens | — (obligatorio en producción) |
| `API_KEY` | Bearer token legacy (deprecado) | vacío |
| `DEBUG` | Modo debug | `false` |
| `CORS_ORIGINS` | Orígenes permitidos (CSV) | `http://localhost:3000,http://localhost:5173` |
| `RATE_LIMIT` | Límite de peticiones | `30/minute` |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/health` | Estado del servicio |
| POST | `/api/v1/auth/register` | Registro de usuario |
| POST | `/api/v1/auth/login` | Inicio de sesión (JWT) |
| GET | `/api/v1/auth/me` | Perfil del usuario autenticado |
| GET | `/api/v1/projects` | Listar proyectos del usuario |
| POST | `/api/v1/projects` | Crear proyecto |
| GET | `/api/v1/queries/history` | Historial de consultas IA |
| POST | `/api/v1/architect/analyze` | Análisis de arquitectura |
| POST | `/api/v1/refactor/code` | Refactor de código |
| POST | `/api/v1/debug/solve` | Resolución de errores |
| POST | `/api/v1/security/audit` | Auditoría de seguridad |
| POST | `/api/v1/performance/analyze` | Análisis de performance |

## CLI (Fase 2)

Instala el comando `unicornio` en tu terminal:

```bash
cd backend
pip install -r requirements/dev.txt
pip install -e . --no-deps    # registra el comando `unicornio`
# Alternativa sin instalar: python -m cli
```

### Configuración

```bash
unicornio config --api-url http://localhost:8000
unicornio register          # o unicornio login
unicornio whoami
```

### Comandos

```bash
unicornio architect "Mi App" --description "API REST de tareas"
unicornio refactor src/auth.py
unicornio refactor ./backend          # carpeta completa
unicornio debug --error "KeyError: id" --file src/main.py
unicornio audit src/
unicornio performance src/handlers.py
unicornio history --limit 10
unicornio logout
```

Variables de entorno:

| Variable | Descripción |
|----------|-------------|
| `UNICORNIO_API_URL` | URL de la API (alternativa a `unicornio config`) |

El token JWT se guarda en `~/.unicornio/config.json`.

### API v2 (Fase 3)

Endpoint unificado con múltiples archivos y streaming:

```bash
# El CLI usa v2 automáticamente para comandos con archivos
unicornio refactor src/auth.py --stream
unicornio architect "Mi App" -d "descripción" --path ./backend
```

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v2/analyze` | Análisis con múltiples archivos |
| POST | `/api/v2/analyze/stream` | Igual, con respuesta SSE en tiempo real |

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

## Deploy automático

Cada push a `main` ejecuta tests y, si pasan, despliega según la plataforma que actives.

### Opción A — Render (recomendada, más simple)

1. Crea cuenta en [render.com](https://render.com)
2. Ve a **New → Blueprint** y conecta este repositorio
3. Render leerá `render.yaml` y creará:
   - **unicornio-api** — backend Docker
   - **unicornio-dev** — frontend estático
4. En el dashboard, agrega el secret `CLAUDE_API_KEY` (y `API_KEY` si quieres auth)
5. Cada push a `main` redespliega automáticamente

### Opción B — Fly.io + GitHub Pages (vía GitHub Actions)

En **Settings → Secrets and variables → Actions**:

**Secrets:**
| Secret | Descripción |
|--------|-------------|
| `FLY_API_TOKEN` | Token de [fly.io/user/tokens](https://fly.io/user/tokens) |
| `CLAUDE_API_KEY` | Clave de Anthropic |
| `API_KEY` | (opcional) Bearer token de la API |

**Variables:**
| Variable | Valor |
|----------|-------|
| `ENABLE_FLY_DEPLOY` | `true` |
| `ENABLE_GITHUB_PAGES` | `true` |
| `VITE_API_URL` | `https://unicornio-api.fly.dev` |
| `CORS_ORIGINS` | `https://wcalmels.github.io` |

Primera vez en Fly.io:

```bash
cd backend
fly auth login
fly launch --no-deploy --copy-config --name unicornio-api
fly secrets set CLAUDE_API_KEY=tu-clave
```

Habilita GitHub Pages en **Settings → Pages → Source: GitHub Actions**.

### Opción C — Render con deploy hooks

Si ya tienes servicios en Render, activa hooks en GitHub Actions:

| Variable | Valor |
|----------|-------|
| `ENABLE_RENDER_HOOKS` | `true` |

| Secret | Descripción |
|--------|-------------|
| `RENDER_DEPLOY_HOOK_API` | Deploy hook del servicio API |
| `RENDER_DEPLOY_HOOK_FRONTEND` | Deploy hook del frontend |

Los hooks están en Render → tu servicio → **Settings → Deploy Hook**.

## Licencia

MIT
