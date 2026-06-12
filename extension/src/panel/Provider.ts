import * as vscode from "vscode";
import { ModuleType, UnicornioApi } from "../api/client";
import { AuthStore, getApiUrl } from "../auth";
import { buildAnalyzePayload, executeAnalyze } from "../commands/runner";
import { getWebviewHtml } from "./html";

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
    this.post({ type: "runStart", module });

    const payload = buildAnalyzePayload(module, {
      projectName: form.project_name,
      description: form.description,
      error: form.error,
      context: form.context,
    });

    const result = await executeAnalyze(this.auth, payload, (chunk) => {
      this.post({ type: "runChunk", text: chunk });
    });

    this.post({ type: "runComplete", result, module });
  }
}
