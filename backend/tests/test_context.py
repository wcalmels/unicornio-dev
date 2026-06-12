from app.services.analyze import build_analyze_prompt
from app.services.context import bundle_file_contents, detect_language_from_path


def test_bundle_file_contents():
    files = [{"path": "a.py", "content": "x = 1"}, {"path": "b.py", "content": "y = 2"}]
    bundled = bundle_file_contents(files)
    assert "# File: a.py" in bundled
    assert "# File: b.py" in bundled


def test_detect_language_from_path():
    assert detect_language_from_path("src/main.py") == "python"
    assert detect_language_from_path("app.tsx") == "typescript"


def test_build_analyze_prompt_refactor():
    from app.schemas.v2 import AnalyzeContext, AnalyzeRequestV2, SourceFile

    req = AnalyzeRequestV2(
        module="refactor",
        files=[SourceFile(path="main.py", content="def foo(): pass")],
        context=AnalyzeContext(language="python"),
    )
    prompt, language = build_analyze_prompt(req)
    assert language == "python"
    assert "main.py" in prompt
    assert "refactoring" in prompt.lower() or "refactor" in prompt.lower()
