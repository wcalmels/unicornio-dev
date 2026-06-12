# API Documentation

Base URL: `http://localhost:8000/api/v1`

## Health

### `GET /health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "claude_configured": true
}
```

## AI Endpoints

Todos los endpoints POST aceptan JSON y devuelven JSON. Si `API_KEY` está configurado en el servidor, incluye el header:

```
Authorization: Bearer <API_KEY>
```

### `POST /architect/analyze`

**Request**

```json
{
  "project_name": "Mi App",
  "description": "API REST para gestión de tareas"
}
```

**Response**

```json
{
  "project": "Mi App",
  "analysis": "..."
}
```

### `POST /refactor/code`

**Request**

```json
{
  "code": "def foo(): pass",
  "language": "python"
}
```

**Response**

```json
{
  "language": "python",
  "result": "..."
}
```

### `POST /debug/solve`

**Request**

```json
{
  "error": "KeyError: 'id'",
  "context": "al leer usuario"
}
```

**Response**

```json
{
  "error": "KeyError: 'id'",
  "solution": "..."
}
```

### `POST /security/audit`

**Request**

```json
{
  "code": "eval(user_input)",
  "language": "python"
}
```

**Response**

```json
{
  "language": "python",
  "audit": "..."
}
```

### `POST /performance/analyze`

**Request**

```json
{
  "code": "for i in range(n): ...",
  "language": "python"
}
```

**Response**

```json
{
  "language": "python",
  "analysis": "..."
}
```

## Errores comunes

| Código | Significado |
|--------|-------------|
| 401 | Falta token de autenticación |
| 403 | Token inválido |
| 422 | Datos de entrada inválidos |
| 502 | Error al comunicarse con Claude |
| 503 | `CLAUDE_API_KEY` no configurada |
| 429 | Rate limit excedido |
