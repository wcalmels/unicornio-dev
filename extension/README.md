# Unicornio Dev — Extensión VS Code / Cursor

Panel lateral con las 5 herramientas de IA integradas al editor.

## Instalación (desarrollo)

```bash
cd extension
npm install
npm run compile
```

En VS Code / Cursor:
1. `F5` o Run → **Run Extension**
2. Se abre una ventana de desarrollo con la extensión cargada
3. Clic en el icono **Unicornio** en la barra de actividad

## Configuración

| Setting | Default | Descripción |
|---------|---------|-------------|
| `unicornio.apiUrl` | `http://localhost:8000` | URL de la API |
| `unicornio.useStreaming` | `true` | Streaming SSE en tiempo real |

## Comandos

| Comando | Acción |
|---------|--------|
| `Unicornio: Refactorizar selección` | Refactor del código seleccionado |
| `Unicornio: Refactorizar archivo` | Refactor del archivo activo |
| `Unicornio: Auditar seguridad del archivo` | Auditoría de seguridad |
| `Unicornio: Analizar performance del archivo` | Análisis de performance |
| `Unicornio: Debug con selección` | Debug con selección + error |

Clic derecho en el editor → menú **Unicornio** (con texto seleccionado).

## Requisitos

- API de Unicornio Dev en ejecución (`uvicorn app.main:app --reload`)
- Cuenta registrada (desde el panel o la web)
