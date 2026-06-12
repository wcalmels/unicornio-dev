import httpx

from cli.config import get_api_url, get_token


class ApiError(Exception):
    pass


class UnicornioClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = (base_url or get_api_url()).rstrip("/")
        self.token = token or get_token()

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        try:
            response = httpx.request(
                method,
                f"{self.base_url}{path}",
                headers=self._headers(),
                json=json,
                timeout=120,
            )
        except httpx.HTTPError as exc:
            raise ApiError(f"No se pudo conectar con {self.base_url}") from exc

        data = response.json() if response.content else {}
        if response.status_code >= 400:
            detail = data.get("detail", f"Error {response.status_code}")
            raise ApiError(detail)
        return data

    def register(self, email: str, name: str, password: str) -> str:
        data = self._request(
            "POST",
            "/api/v1/auth/register",
            {"email": email, "name": name, "password": password},
        )
        return data["access_token"]

    def login(self, email: str, password: str) -> str:
        data = self._request(
            "POST",
            "/api/v1/auth/login",
            {"email": email, "password": password},
        )
        return data["access_token"]

    def me(self) -> dict:
        return self._request("GET", "/api/v1/auth/me")

    def history(self, limit: int = 20) -> list[dict]:
        response = httpx.get(
            f"{self.base_url}/api/v1/queries/history",
            headers=self._headers(),
            params={"limit": limit},
            timeout=30,
        )
        if response.status_code >= 400:
            data = response.json()
            raise ApiError(data.get("detail", f"Error {response.status_code}"))
        return response.json()

    def architect(self, project_name: str, description: str) -> str:
        data = self._request(
            "POST",
            "/api/v1/architect/analyze",
            {"project_name": project_name, "description": description},
        )
        return data["analysis"]

    def refactor(self, code: str, language: str) -> str:
        data = self._request(
            "POST",
            "/api/v1/refactor/code",
            {"code": code, "language": language},
        )
        return data["result"]

    def debug(self, error: str, context: str = "") -> str:
        data = self._request(
            "POST",
            "/api/v1/debug/solve",
            {"error": error, "context": context},
        )
        return data["solution"]

    def security(self, code: str, language: str) -> str:
        data = self._request(
            "POST",
            "/api/v1/security/audit",
            {"code": code, "language": language},
        )
        return data["audit"]

    def performance(self, code: str, language: str) -> str:
        data = self._request(
            "POST",
            "/api/v1/performance/analyze",
            {"code": code, "language": language},
        )
        return data["analysis"]
