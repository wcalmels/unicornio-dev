import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.v2 import AnalyzeRequestV2, AnalyzeResponseV2
from app.services.analyze import build_analyze_prompt
from app.services.claude import ClaudeService, get_claude_service
from app.services.queries import save_query

router = APIRouter(prefix="/api/v2", tags=["ai-v2"])


def _validate_request(req: AnalyzeRequestV2) -> None:
    if req.module == "architect":
        if not req.context.project_name or not req.context.description:
            raise HTTPException(
                status_code=422,
                detail="architect requiere context.project_name y context.description",
            )
    if req.module == "debug" and not req.context.error:
        raise HTTPException(status_code=422, detail="debug requiere context.error")
    if req.module in {"refactor", "security", "performance"} and not req.files:
        raise HTTPException(
            status_code=422,
            detail=f"{req.module} requiere al menos un archivo",
        )


async def _save_analyze_query(
    db: AsyncSession,
    *,
    user_id: int,
    req: AnalyzeRequestV2,
    result: str,
) -> None:
    await save_query(
        db,
        user_id=user_id,
        module=req.module,
        input_data=req.model_dump(),
        output_text=result,
    )


@router.post("/analyze", response_model=AnalyzeResponseV2)
async def analyze_v2(
    req: AnalyzeRequestV2,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> AnalyzeResponseV2:
    _validate_request(req)
    prompt, language = build_analyze_prompt(req)
    result = await claude.complete(prompt)
    await _save_analyze_query(db, user_id=current_user.id, req=req, result=result)
    return AnalyzeResponseV2(
        module=req.module,
        result=result,
        files_analyzed=[f.path for f in req.files],
        language=language,
    )


@router.post("/analyze/stream")
async def analyze_stream_v2(
    req: AnalyzeRequestV2,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    claude: ClaudeService = Depends(get_claude_service),
) -> StreamingResponse:
    _validate_request(req)
    prompt, language = build_analyze_prompt(req)

    async def event_stream() -> AsyncGenerator[str, None]:
        chunks: list[str] = []
        try:
            async for text in claude.stream_complete(prompt):
                chunks.append(text)
                yield f"data: {json.dumps({'text': text})}\n\n"
            result = "".join(chunks)
            await _save_analyze_query(db, user_id=current_user.id, req=req, result=result)
            yield f"data: {json.dumps({'done': True, 'language': language})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
