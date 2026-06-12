import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cli.context import bundle_sources, detect_language, project_tree


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    config_dir = tmp_path / ".unicornio"
    config_file = config_dir / "config.json"
    monkeypatch.setattr("cli.config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("cli.config.CONFIG_FILE", config_file)
    return config_file


def test_detect_language():
    assert detect_language(Path("main.py")) == "python"
    assert detect_language(Path("app.tsx")) == "typescript"


def test_bundle_sources_single_file(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("def foo():\n    pass\n", encoding="utf-8")
    code, language = bundle_sources(source)
    assert language == "python"
    assert "def foo():" in code


def test_project_tree(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text("x", encoding="utf-8")
    tree = project_tree(tmp_path)
    assert "app" in tree


def test_login_command(runner, config_file):
    with patch("cli.main.UnicornioClient") as mock_cls:
        mock_cls.return_value.login.return_value = "jwt-token-123"
        result = runner.invoke(
            __import__("cli.main", fromlist=["app"]).app,
            ["login", "--email", "u@example.com", "--password", "password123"],
        )

    assert result.exit_code == 0
    assert "Sesión iniciada" in result.stdout
    saved = json.loads(config_file.read_text())
    assert saved["token"] == "jwt-token-123"


def test_logout_command(runner, config_file):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps({"token": "abc"}), encoding="utf-8")

    result = runner.invoke(__import__("cli.main", fromlist=["app"]).app, ["logout"])
    assert result.exit_code == 0
    saved = json.loads(config_file.read_text())
    assert "token" not in saved


def test_refactor_requires_login(runner, config_file, tmp_path):
    source = tmp_path / "code.py"
    source.write_text("x=1", encoding="utf-8")

    result = runner.invoke(
        __import__("cli.main", fromlist=["app"]).app,
        ["refactor", str(source)],
    )
    assert result.exit_code == 1
    assert "No has iniciado sesión" in result.stdout


def test_refactor_with_auth(runner, config_file, tmp_path):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps({"token": "jwt-token"}), encoding="utf-8")

    source = tmp_path / "code.py"
    source.write_text("x=1", encoding="utf-8")

    with patch("cli.main.UnicornioClient") as mock_cls:
        instance = mock_cls.return_value
        instance.refactor.return_value = "código mejorado"
        result = runner.invoke(
            __import__("cli.main", fromlist=["app"]).app,
            ["refactor", str(source)],
        )

    assert result.exit_code == 0
    assert "código mejorado" in result.stdout
    instance.refactor.assert_called_once()
    sent_code, sent_lang = instance.refactor.call_args[0]
    assert sent_lang == "python"
    assert "x=1" in sent_code


def test_config_command(runner, config_file):
    result = runner.invoke(
        __import__("cli.main", fromlist=["app"]).app,
        ["config", "--api-url", "https://api.example.com"],
    )
    assert result.exit_code == 0
    saved = json.loads(config_file.read_text())
    assert saved["api_url"] == "https://api.example.com"
