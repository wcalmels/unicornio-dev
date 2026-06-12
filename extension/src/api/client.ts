import { getApiUrl } from "../auth";

export type ModuleType = "architect" | "refactor" | "debug" | "security" | "performance";

export interface SourceFile {
  path: string;
  content: string;
}

export interface AnalyzeContext {
  project_root?: string;
  language?: string;
  tree?: string;
  project_name?: string;
  description?: string;
  error?: string;
  extra?: string;
}

export interface AnalyzePayload {
  module: ModuleType;
  files: SourceFile[];
  context: AnalyzeContext;
}

export class ApiError extends Error {}

export class UnicornioApi {
  constructor(
    private readonly token: string,
    private readonly baseUrl: string = getApiUrl(),
  ) {}

  private headers(): Record<string, string> {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.token}`,
    };
  }

  private async parseError(response: Response): Promise<string> {
    try {
      const data = (await response.json()) as { detail?: string };
      return data.detail ?? `Error ${response.status}`;
    } catch {
      return `Error ${response.status}`;
    }
  }

  async login(email: string, password: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      throw new ApiError(await this.parseError(response));
    }
    const data = (await response.json()) as { access_token: string };
    return data.access_token;
  }

  async register(email: string, name: string, password: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, name, password }),
    });
    if (!response.ok) {
      throw new ApiError(await this.parseError(response));
    }
    const data = (await response.json()) as { access_token: string };
    return data.access_token;
  }

  async me(): Promise<{ name: string; email: string; plan: string }> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/me`, {
      headers: this.headers(),
    });
    if (!response.ok) {
      throw new ApiError(await this.parseError(response));
    }
    return response.json() as Promise<{ name: string; email: string; plan: string }>;
  }

  async history(limit = 20): Promise<Array<Record<string, unknown>>> {
    const response = await fetch(`${this.baseUrl}/api/v1/queries/history?limit=${limit}`, {
      headers: this.headers(),
    });
    if (!response.ok) {
      throw new ApiError(await this.parseError(response));
    }
    return response.json() as Promise<Array<Record<string, unknown>>>;
  }

  async analyze(payload: AnalyzePayload): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/v2/analyze`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new ApiError(await this.parseError(response));
    }
    const data = (await response.json()) as { result: string };
    return data.result;
  }

  async analyzeStream(
    payload: AnalyzePayload,
    onChunk: (text: string) => void,
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/v2/analyze/stream`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new ApiError(await this.parseError(response));
    }

    if (!response.body) {
      throw new ApiError("Streaming no disponible");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let result = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data:")) {
          continue;
        }
        const raw = line.slice(5).trim();
        if (!raw) {
          continue;
        }
        const event = JSON.parse(raw) as { text?: string; error?: string; done?: boolean };
        if (event.error) {
          throw new ApiError(event.error);
        }
        if (event.text) {
          result += event.text;
          onChunk(event.text);
        }
      }
    }

    return result;
  }
}
