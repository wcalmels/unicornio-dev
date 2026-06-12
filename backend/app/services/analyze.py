from app.prompts import (
    architect_prompt,
    debug_prompt,
    performance_prompt,
    refactor_prompt,
    security_prompt,
)
from app.schemas.v2 import AnalyzeRequestV2
from app.services.context import bundle_file_contents, detect_language_from_path


def _resolve_language(req: AnalyzeRequestV2) -> str:
    if req.context.language:
        return req.context.language
    if req.files:
        return detect_language_from_path(req.files[0].path)
    return "python"


def _bundle_context(req: AnalyzeRequestV2) -> str:
    parts: list[str] = []
    if req.context.tree:
        parts.append(f"Project tree:\n{req.context.tree}")
    bundled = bundle_file_contents([f.model_dump() for f in req.files])
    if bundled:
        parts.append(bundled)
    if req.context.extra:
        parts.append(req.context.extra)
    return "\n\n".join(parts)


def build_analyze_prompt(req: AnalyzeRequestV2) -> tuple[str, str]:
    language = _resolve_language(req)
    bundled = _bundle_context(req)

    if req.module == "architect":
        description = req.context.description
        if bundled:
            description = f"{description}\n\nContexto adicional:\n{bundled}"
        prompt = architect_prompt(req.context.project_name, description)
    elif req.module == "refactor":
        prompt = refactor_prompt(language, bundled)
    elif req.module == "debug":
        context = bundled or req.context.extra
        prompt = debug_prompt(req.context.error, context)
    elif req.module == "security":
        prompt = security_prompt(language, bundled)
    elif req.module == "performance":
        prompt = performance_prompt(language, bundled)
    else:
        raise ValueError(f"Módulo no soportado: {req.module}")

    return prompt, language
