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

export interface AnalyzeOptions {
  content?: string;
  filePath?: string;
  error?: string;
  context?: string;
  projectName?: string;
  description?: string;
}

export function buildAnalyzePayload(
  module: ModuleType,
  options?: AnalyzeOptions,
): AnalyzePayload {
  const editor = vscode.window.activeTextEditor;
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  let content = options?.content;
  let filePath = options?.filePath;

  if (content === undefined && editor) {
    if (module === "refactor") {
      content = editor.document.getText(editor.selection) || editor.document.getText();
      filePath = editor.document.uri.fsPath;
    } else if (module === "security" || module === "performance") {
      content = editor.document.getText();
      filePath = editor.document.uri.fsPath;
    } else if (module === "debug") {
      const selection = editor.document.getText(editor.selection);
      if (selection) {
        content = selection;
        filePath = editor.document.uri.fsPath;
      }
    }
  }

  if (!content && module !== "architect") {
    if (module === "debug" && options?.error) {
      // debug puede ejecutarse solo con el mensaje de error del formulario
    } else if (module === "security" || module === "performance") {
      throw new Error("Abre un archivo para analizar.");
    } else if (module === "refactor") {
      throw new Error("Selecciona código o abre un archivo.");
    } else if (module === "debug") {
      throw new Error("Describe el error o selecciona código con contexto.");
    } else {
      throw new Error("No hay texto seleccionado ni archivo activo.");
    }
  }

  const language = filePath ? detectLanguage(filePath) : "text";
  return {
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
}

export async function executeAnalyze(
  auth: AuthStore,
  payload: AnalyzePayload,
  onChunk?: (chunk: string) => void,
): Promise<string> {
  const api = await ensureApi(auth);

  if (useStreaming()) {
    if (onChunk) {
      return api.analyzeStream(payload, onChunk);
    }

    const channel = getOutputChannel();
    channel.clear();
    channel.show(true);
    const title = MODULE_TITLES[payload.module];
    channel.appendLine(`=== ${title} ===\n`);
    const result = await api.analyzeStream(payload, (chunk) => channel.append(chunk));
    channel.appendLine("\n");
    return result;
  }

  if (onChunk) {
    return api.analyze(payload);
  }

  return vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Unicornio: ${MODULE_TITLES[payload.module]}`,
      cancellable: false,
    },
    async () => api.analyze(payload),
  );
}

const MODULE_TITLES: Record<ModuleType, string> = {
  architect: "Arquitectura",
  refactor: "Refactor",
  debug: "Debug",
  security: "Seguridad",
  performance: "Performance",
};

export async function runAnalyze(
  auth: AuthStore,
  payload: AnalyzePayload,
  title: string,
): Promise<string> {
  const result = await executeAnalyze(auth, payload);

  if (!useStreaming()) {
    await showResultDocument(title, result);
  }

  return result;
}

export async function analyzeEditorContent(
  auth: AuthStore,
  module: ModuleType,
  options?: AnalyzeOptions,
): Promise<string> {
  const payload = buildAnalyzePayload(module, options);
  return runAnalyze(auth, payload, MODULE_TITLES[module]);
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
