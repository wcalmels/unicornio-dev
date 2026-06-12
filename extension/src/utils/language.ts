const EXTENSIONS: Record<string, string> = {
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
};

export function detectLanguage(filePath: string): string {
  const dot = filePath.lastIndexOf(".");
  if (dot === -1) {
    return "text";
  }
  return EXTENSIONS[filePath.slice(dot).toLowerCase()] ?? "text";
}

export function relativePath(filePath: string, workspaceRoot?: string): string {
  if (!workspaceRoot) {
    return filePath.split(/[\\/]/).pop() ?? filePath;
  }
  const normalized = filePath.replace(/\\/g, "/");
  const root = workspaceRoot.replace(/\\/g, "/");
  if (normalized.startsWith(root)) {
    return normalized.slice(root.length).replace(/^\//, "");
  }
  return normalized.split("/").pop() ?? filePath;
}
