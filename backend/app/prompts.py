def architect_prompt(project_name: str, description: str) -> str:
    return f"""Eres un arquitecto de software senior.
Analiza estos requisitos y devuelve un análisis técnico completo:

Proyecto: {project_name}
Descripción: {description}

Incluye: arquitectura recomendada, tech stack, riesgos, timeline estimado."""


def refactor_prompt(language: str, code: str) -> str:
    return f"""Eres un experto en refactoring y clean code.
Mejora este código {language} siguiendo SOLID, DRY, KISS:

```{language}
{code}
```

Devuelve: problemas encontrados, código mejorado, explicación de cambios."""


def debug_prompt(error: str, context: str) -> str:
    return f"""Eres un debugger experto.
Analiza este error y proporciona la solución:

Error: {error}
Contexto: {context}

Devuelve: causa raíz, solución paso a paso, código corregido si aplica."""


def security_prompt(language: str, code: str) -> str:
    return f"""Eres un experto en ciberseguridad.
Audita este código en busca de vulnerabilidades:

```{language}
{code}
```

Devuelve: vulnerabilidades encontradas (con severidad), recomendaciones, código corregido."""


def performance_prompt(language: str, code: str) -> str:
    return f"""Eres un experto en optimización de performance.
Analiza este código:

```{language}
{code}
```

Devuelve: bottlenecks, complejidad temporal/espacial, optimizaciones recomendadas."""
