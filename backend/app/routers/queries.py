from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.auth import QueryHistoryItem
from app.services.queries import get_user_queries

router = APIRouter(prefix="/queries", tags=["queries"])


@router.get("/history", response_model=list[QueryHistoryItem])
async def query_history(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[QueryHistoryItem]:
    records = await get_user_queries(db, current_user.id, limit=limit)
    return [
        QueryHistoryItem(
            id=r.id,
            module=r.module,
            input_data=r.input_data,
            output_text=r.output_text,
            project_id=r.project_id,
            created_at=r.created_at,
        )
        for r in records
    ]
