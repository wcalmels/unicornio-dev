from pathlib import Path

MAX_FILE_BYTES = 50_000
MAX_TOTAL_BYTES = 50_000
MAX_FILES = 20

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


def detect_language_from_path(path: str) -> str:
    return CODE_EXTENSIONS.get(Path(path).suffix.lower(), "text")


def bundle_file_contents(files: list[dict[str, str]]) -> str:
    if not files:
        return ""

    chunks: list[str] = []
    total = 0

    for file in files:
        path = file["path"]
        content = file["content"][:MAX_FILE_BYTES]
        block = f"# File: {path}\n{content}\n"
        if total + len(block) > MAX_TOTAL_BYTES:
            remaining = MAX_TOTAL_BYTES - total
            if remaining <= 0:
                break
            block = block[:remaining]
        chunks.append(block)
        total += len(block)
        if total >= MAX_TOTAL_BYTES:
            break

    return "\n".join(chunks)
