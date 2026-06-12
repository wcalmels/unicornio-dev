from fastapi import APIRouter, Depends

from app.dependencies import verify_api_key
from app.prompts import (
    architect_prompt,
    debug_prompt,
    performance_prompt,
    refactor_prompt,
    security_prompt,
)
from app.schemas.requests import ArchitectReq, CodeReq, DebugReq
from app.schemas.responses import (
    AnalysisResponse,
    AuditResponse,
    PerformanceResponse,
    RefactorResponse,
    SolutionResponse,
)
from app.services.claude import ClaudeService, get_claude_service

router = APIRouter(
    tags=["ai"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/architect/analyze", response_model=AnalysisResponse)
async def architect(
    req: ArchitectReq,
    claude: ClaudeService = Depends(get_claude_service),
) -> AnalysisResponse:
    result = await claude.complete(architect_prompt(req.project_name, req.description))
    return AnalysisResponse(project=req.project_name, analysis=result)


@router.post("/refactor/code", response_model=RefactorResponse)
async def refactor(
    req: CodeReq,
    claude: ClaudeService = Depends(get_claude_service),
) -> RefactorResponse:
    result = await claude.complete(refactor_prompt(req.language, req.code))
    return RefactorResponse(language=req.language, result=result)


@router.post("/debug/solve", response_model=SolutionResponse)
async def debug(
    req: DebugReq,
    claude: ClaudeService = Depends(get_claude_service),
) -> SolutionResponse:
    result = await claude.complete(debug_prompt(req.error, req.context))
    return SolutionResponse(error=req.error, solution=result)


@router.post("/security/audit", response_model=AuditResponse)
async def security(
    req: CodeReq,
    claude: ClaudeService = Depends(get_claude_service),
) -> AuditResponse:
    result = await claude.complete(security_prompt(req.language, req.code))
    return AuditResponse(language=req.language, audit=result)


@router.post("/performance/analyze", response_model=PerformanceResponse)
async def performance(
    req: CodeReq,
    claude: ClaudeService = Depends(get_claude_service),
) -> PerformanceResponse:
    result = await claude.complete(performance_prompt(req.language, req.code))
    return PerformanceResponse(language=req.language, analysis=result)
