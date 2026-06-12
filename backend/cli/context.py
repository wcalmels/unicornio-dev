from pathlib import Path

MAX_FILE_BYTES = 50_000
MAX_TOTAL_BYTES = 50_000

CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".sql": "sql",
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
}

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
    return CODE_EXTENSIONS.get(path.suffix.lower(), "text")


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


def bundle_sources(path: Path, root: Path | None = None) -> tuple[str, str]:
    root = root or (path if path.is_dir() else path.parent)
    files = collect_source_files(path)

    if not files:
        raise ValueError(f"No se encontraron archivos de código en {path}")

    chunks: list[str] = []
    total = 0
    primary_language = detect_language(files[0])

    for file_path in files:
        content = read_text_file(file_path)
        header = f"# File: {file_path.relative_to(root)}"
        block = f"{header}\n{content}\n"
        if total + len(block) > MAX_TOTAL_BYTES:
            remaining = MAX_TOTAL_BYTES - total
            if remaining <= 0:
                break
            block = block[:remaining]
        chunks.append(block)
        total += len(block)
        if total >= MAX_TOTAL_BYTES:
            break

    tree = project_tree(root) if path.is_dir() else ""
    language = primary_language
    code = "\n".join(chunks)
    if tree:
        code = f"Project tree:\n{tree}\n\n{code}"
    return code, language
