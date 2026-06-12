from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
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
from app.services.queries import save_query

router = APIRouter(tags=["ai"])


@router.post("/architect/analyze", response_model=AnalysisResponse)
async def architect(
    req: ArchitectReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> AnalysisResponse:
    result = await claude.complete(architect_prompt(req.project_name, req.description))
    await save_query(
        db,
        user_id=current_user.id,
        module="architect",
        input_data=req.model_dump(),
        output_text=result,
    )
    return AnalysisResponse(project=req.project_name, analysis=result)


@router.post("/refactor/code", response_model=RefactorResponse)
async def refactor(
    req: CodeReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> RefactorResponse:
    result = await claude.complete(refactor_prompt(req.language, req.code))
    await save_query(
        db,
        user_id=current_user.id,
        module="refactor",
        input_data=req.model_dump(),
        output_text=result,
    )
    return RefactorResponse(language=req.language, result=result)


@router.post("/debug/solve", response_model=SolutionResponse)
async def debug(
    req: DebugReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> SolutionResponse:
    result = await claude.complete(debug_prompt(req.error, req.context))
    await save_query(
        db,
        user_id=current_user.id,
        module="debug",
        input_data=req.model_dump(),
        output_text=result,
    )
    return SolutionResponse(error=req.error, solution=result)


@router.post("/security/audit", response_model=AuditResponse)
async def security(
    req: CodeReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> AuditResponse:
    result = await claude.complete(security_prompt(req.language, req.code))
    await save_query(
        db,
        user_id=current_user.id,
        module="security",
        input_data=req.model_dump(),
        output_text=result,
    )
    return AuditResponse(language=req.language, audit=result)


@router.post("/performance/analyze", response_model=PerformanceResponse)
async def performance(
    req: CodeReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> PerformanceResponse:
    result = await claude.complete(performance_prompt(req.language, req.code))
    await save_query(
        db,
        user_id=current_user.id,
        module="performance",
        input_data=req.model_dump(),
        output_text=result,
    )
    return PerformanceResponse(language=req.language, analysis=result)
