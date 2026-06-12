from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    claude_configured: bool


class AnalysisResponse(BaseModel):
    project: str
    analysis: str


class RefactorResponse(BaseModel):
    language: str
    result: str


class SolutionResponse(BaseModel):
    error: str
    solution: str


class AuditResponse(BaseModel):
    language: str
    audit: str


class PerformanceResponse(BaseModel):
    language: str
    analysis: str


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Recurso no encontrado"])
