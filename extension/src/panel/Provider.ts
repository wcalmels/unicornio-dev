import * as vscode from "vscode";
import { ModuleType, UnicornioApi } from "../api/client";
import { AuthStore, getApiUrl, useStreaming } from "../auth";
import {
  analyzeActiveFile,
  analyzeEditorContent,
  ensureApi,
  getOutputChannel,
} from "../commands/runner";
import { getWebviewHtml } from "./html";
import { detectLanguage, relativePath } from "../utils/language";

export class UnicornioPanelProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "unicornio.sidebar";
  private view?: vscode.WebviewView;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private readonly auth: AuthStore,
  ) {}

  resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ): void {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.extensionUri],
    };
    webviewView.webview.html = getWebviewHtml();

    webviewView.webview.onDidReceiveMessage(async (message) => {
      try {
        await this.handleMessage(message);
      } catch (error) {
        const text = error instanceof Error ? error.message : String(error);
        this.post({ type: "runError", message: text });
      }
    });
  }

  private post(message: Record<string, unknown>): void {
    this.view?.webview.postMessage(message);
  }

  private async handleMessage(message: Record<string, unknown>): Promise<void> {
    switch (message.type) {
      case "ready":
        await this.bootstrap();
        break;
      case "login":
        await this.login(
          String(message.email ?? ""),
          String(message.password ?? ""),
        );
        break;
      case "register":
        await this.register(
          String(message.email ?? ""),
          String(message.password ?? ""),
          String(message.name ?? ""),
        );
        break;
      case "logout":
        await this.auth.clearToken();
        this.post({ type: "authRequired" });
        break;
      case "loadHistory":
        await this.loadHistory();
        break;
      case "run":
        await this.runModule(
          message.module as ModuleType,
          (message.form as Record<string, string>) ?? {},
        );
        break;
    }
  }

  private async bootstrap(): Promise<void> {
    const token = await this.auth.getToken();
    if (!token) {
      this.post({ type: "authRequired" });
      return;
    }
    try {
      const api = new UnicornioApi(token, getApiUrl());
      const user = await api.me();
      this.post({ type: "authenticated", user });
      await this.loadHistory();
    } catch {
      await this.auth.clearToken();
      this.post({ type: "authRequired" });
    }
  }

  private async login(email: string, password: string): Promise<void> {
    const api = new UnicornioApi("", getApiUrl());
    const token = await api.login(email, password);
    await this.auth.setToken(token);
    await this.bootstrap();
  }

  private async register(email: string, password: string, name: string): Promise<void> {
    const api = new UnicornioApi("", getApiUrl());
    const token = await api.register(email, name, password);
    await this.auth.setToken(token);
    await this.bootstrap();
  }

  private async loadHistory(): Promise<void> {
    const token = await this.auth.getToken();
    if (!token) {
      return;
    }
    const api = new UnicornioApi(token, getApiUrl());
    const items = await api.history(15);
    this.post({ type: "history", items });
  }

  private async runModule(module: ModuleType, form: Record<string, string>): Promise<void> {
    this.post({ type: "runStart" });

    if (module === "architect") {
      const result = await analyzeEditorContent(this.auth, module, {
        projectName: form.project_name,
        description: form.description,
      });
      this.post({ type: "runComplete", result });
      return;
    }

    if (module === "debug") {
      const result = await analyzeEditorContent(this.auth, module, {
        error: form.error,
        context: form.context,
      });
      this.post({ type: "runComplete", result });
      return;
    }

    if (module === "refactor") {
      const editor = vscode.window.activeTextEditor;
      const content = editor?.document.getText(editor.selection) || editor?.document.getText();
      if (!content) {
        throw new Error("Selecciona código o abre un archivo.");
      }
      const result = await this.runWithStream(module, content, editor?.document.uri.fsPath);
      this.post({ type: "runComplete", result });
      return;
    }

    const result = await analyzeActiveFile(this.auth, module);
    this.post({ type: "runComplete", result });
  }

  private async runWithStream(
    module: ModuleType,
    content: string,
    filePath?: string,
  ): Promise<string> {
    const api = await ensureApi(this.auth);
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    const payload = {
      module,
      files: [{ path: filePath ? relativePath(filePath, workspaceRoot) : "selection", content }],
      context: {
        project_root: workspaceRoot ?? "",
        language: filePath ? detectLanguage(filePath) : "text",
      },
    };

    if (useStreaming()) {
      return api.analyzeStream(payload, (chunk) => {
        this.post({ type: "runChunk", text: chunk });
        getOutputChannel().append(chunk);
      });
    }

    return api.analyze(payload);
  }
}
