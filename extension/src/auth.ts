import * as vscode from "vscode";

const TOKEN_KEY = "unicornio.jwt";

export class AuthStore {
  constructor(private readonly secrets: vscode.SecretStorage) {}

  async getToken(): Promise<string | undefined> {
    return this.secrets.get(TOKEN_KEY);
  }

  async setToken(token: string): Promise<void> {
    await this.secrets.store(TOKEN_KEY, token);
  }

  async clearToken(): Promise<void> {
    await this.secrets.delete(TOKEN_KEY);
  }
}

export function getApiUrl(): string {
  return vscode.workspace.getConfiguration("unicornio").get<string>("apiUrl", "http://localhost:8000").replace(/\/$/, "");
}

export function useStreaming(): boolean {
  return vscode.workspace.getConfiguration("unicornio").get<boolean>("useStreaming", true);
}
