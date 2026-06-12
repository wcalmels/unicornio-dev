import * as vscode from "vscode";
import { AnalyzePayload, ModuleType, UnicornioApi } from "../api/client";
import { AuthStore, getApiUrl, useStreaming } from "../auth";
import { detectLanguage, relativePath } from "../utils/language";

export async function ensureApi(auth: AuthStore): Promise<UnicornioApi> {
  const token = await auth.getToken();
  if (!token) {
    throw new Error("Inicia sesión desde el panel de Unicornio Dev.");
  }
  return new UnicornioApi(token, getApiUrl());
}

export async function runAnalyze(
  auth: AuthStore,
  payload: AnalyzePayload,
  title: string,
): Promise<string> {
  const api = await ensureApi(auth);
  const stream = useStreaming();
  let result = "";

  if (stream) {
    const channel = getOutputChannel();
    channel.clear();
    channel.show(true);
    channel.appendLine(`=== ${title} ===\n`);

    result = await api.analyzeStream(payload, (chunk) => {
      channel.append(chunk);
    });
    channel.appendLine("\n");
  } else {
    result = await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `Unicornio: ${title}`,
        cancellable: false,
      },
      async () => api.analyze(payload),
    );
    await showResultDocument(title, result);
  }

  return result;
}

export async function analyzeEditorContent(
  auth: AuthStore,
  module: ModuleType,
  options?: {
    content?: string;
    filePath?: string;
    error?: string;
    context?: string;
    projectName?: string;
    description?: string;
  },
): Promise<string> {
  const editor = vscode.window.activeTextEditor;
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  const content = options?.content ?? editor?.document.getText(editor.selection);
  const filePath = options?.filePath ?? editor?.document.uri.fsPath;

  if (!content && module !== "architect") {
    throw new Error("No hay texto seleccionado ni archivo activo.");
  }

  const language = filePath ? detectLanguage(filePath) : "text";
  const payload: AnalyzePayload = {
    module,
    files: content
      ? [
          {
            path: filePath ? relativePath(filePath, workspaceRoot) : "selection",
            content,
          },
        ]
      : [],
    context: {
      project_root: workspaceRoot ?? "",
      language,
      project_name: options?.projectName ?? "",
      description: options?.description ?? "",
      error: options?.error ?? "",
      extra: options?.context ?? "",
    },
  };

  const titles: Record<ModuleType, string> = {
    architect: "Arquitectura",
    refactor: "Refactor",
    debug: "Debug",
    security: "Seguridad",
    performance: "Performance",
  };

  return runAnalyze(auth, payload, titles[module]);
}

export async function analyzeActiveFile(auth: AuthStore, module: ModuleType): Promise<string> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    throw new Error("No hay archivo activo.");
  }
  return analyzeEditorContent(auth, module, {
    content: editor.document.getText(),
    filePath: editor.document.uri.fsPath,
  });
}

export async function showResultDocument(title: string, content: string): Promise<void> {
  const doc = await vscode.workspace.openTextDocument({
    content,
    language: "markdown",
  });
  await vscode.window.showTextDocument(doc, { preview: false });
  vscode.window.showInformationMessage(`Unicornio: ${title} completado.`);
}

let outputChannel: vscode.OutputChannel | undefined;

export function getOutputChannel(): vscode.OutputChannel {
  if (!outputChannel) {
    outputChannel = vscode.window.createOutputChannel("Unicornio Dev");
  }
  return outputChannel;
}

export async function handleCommandError(error: unknown): Promise<void> {
  const message = error instanceof Error ? error.message : String(error);
  vscode.window.showErrorMessage(`Unicornio: ${message}`);
}
