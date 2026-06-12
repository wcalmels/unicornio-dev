from typing import Literal

from pydantic import BaseModel, Field

ModuleType = Literal["architect", "refactor", "debug", "security", "performance"]


class SourceFile(BaseModel):
    path: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1, max_length=50_000)


class AnalyzeContext(BaseModel):
    project_root: str = Field(default="", max_length=500)
    language: str = Field(default="", max_length=50)
    tree: str = Field(default="", max_length=10_000)
    project_name: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=10_000)
    error: str = Field(default="", max_length=10_000)
    extra: str = Field(default="", max_length=10_000)


class AnalyzeRequestV2(BaseModel):
    module: ModuleType
    files: list[SourceFile] = Field(default_factory=list, max_length=20)
    context: AnalyzeContext = Field(default_factory=AnalyzeContext)


class AnalyzeResponseV2(BaseModel):
    module: ModuleType
    result: str
    files_analyzed: list[str]
    language: str
