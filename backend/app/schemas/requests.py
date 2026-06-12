from pydantic import BaseModel, Field


class ArchitectReq(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=10_000)


class CodeReq(BaseModel):
    code: str = Field(..., min_length=1, max_length=50_000)
    language: str = Field(default="python", min_length=1, max_length=50)


class DebugReq(BaseModel):
    error: str = Field(..., min_length=1, max_length=10_000)
    context: str = Field(default="", max_length=10_000)
