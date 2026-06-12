import json
import os
from pathlib import Path

DEFAULT_API_URL = "http://localhost:8000"
CONFIG_DIR = Path.home() / ".unicornio"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_api_url() -> str:
    if url := os.getenv("UNICORNIO_API_URL"):
        return url.rstrip("/")
    config = load_config()
    return config.get("api_url", DEFAULT_API_URL).rstrip("/")


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def save_config(*, api_url: str | None = None, token: str | None = None) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = load_config()
    if api_url is not None:
        config["api_url"] = api_url.rstrip("/")
    if token is not None:
        config["token"] = token
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_token() -> str | None:
    return load_config().get("token")


def clear_token() -> None:
    config = load_config()
    config.pop("token", None)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
