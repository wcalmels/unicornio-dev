from pathlib import Path

from app.services.context import (
    CODE_EXTENSIONS,
    MAX_FILE_BYTES,
    bundle_file_contents,
    detect_language_from_path,
)

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".ruff_cache",
}


def detect_language(path: Path) -> str:
    return detect_language_from_path(str(path))


def read_text_file(path: Path, max_bytes: int = MAX_FILE_BYTES) -> str:
    data = path.read_bytes()
    if len(data) > max_bytes:
        data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")


def project_tree(root: Path, max_depth: int = 2) -> str:
    lines: list[str] = []

    def walk(directory: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            return
        entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        for index, entry in enumerate(entries):
            if entry.name in SKIP_DIRS:
                continue
            connector = "└── " if index == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir() and depth < max_depth:
                extension = "    " if index == len(entries) - 1 else "│   "
                walk(entry, prefix + extension, depth + 1)

    lines.append(f"{root.name}/")
    walk(root, "", 1)
    return "\n".join(lines[:80])


def collect_source_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    files: list[Path] = []
    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        if any(part in SKIP_DIRS for part in file_path.parts):
            continue
        if file_path.suffix.lower() not in CODE_EXTENSIONS:
            continue
        files.append(file_path)
    return files


def bundle_sources(path: Path, root: Path | None = None) -> tuple[str, str, list[dict[str, str]]]:
    root = root or (path if path.is_dir() else path.parent)
    files = collect_source_files(path)

    if not files:
        raise ValueError(f"No se encontraron archivos de código en {path}")

    file_payloads = [
        {"path": str(file_path.relative_to(root)), "content": read_text_file(file_path)}
        for file_path in files
    ]
    code = bundle_file_contents(file_payloads)
    tree = project_tree(root) if path.is_dir() else ""
    language = detect_language(files[0])

    if tree:
        code = f"Project tree:\n{tree}\n\n{code}"

    return code, language, file_payloads


def build_v2_payload(
    module: str,
    path: Path,
    *,
    error: str = "",
    context: str = "",
    project_name: str = "",
    description: str = "",
) -> dict:
    resolved = path.resolve()
    root = resolved if resolved.is_dir() else resolved.parent
    code, language, file_payloads = bundle_sources(resolved, root=root)
    tree = project_tree(root) if resolved.is_dir() else ""

    payload = {
        "module": module,
        "files": file_payloads,
        "context": {
            "project_root": str(root),
            "language": language,
            "tree": tree,
            "project_name": project_name,
            "description": description,
            "error": error,
            "extra": context,
        },
    }

    if module == "debug" and resolved.is_file():
        payload["context"]["extra"] = (
            f"{context}\n\nArchivo {resolved.name}:\n```\n{read_text_file(resolved)}\n```"
        ).strip()

    if not file_payloads and module != "architect":
        payload["files"] = [{"path": str(resolved.name), "content": code}]

    return payload
