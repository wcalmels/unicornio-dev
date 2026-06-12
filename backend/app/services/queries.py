from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Query


async def save_query(
    db: AsyncSession,
    *,
    user_id: int,
    module: str,
    input_data: dict,
    output_text: str,
    project_id: int | None = None,
) -> Query:
    record = Query(
        user_id=user_id,
        project_id=project_id,
        module=module,
        input_data=input_data,
        output_text=output_text,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_user_queries(db: AsyncSession, user_id: int, limit: int = 50) -> list[Query]:
    result = await db.execute(
        select(Query)
        .where(Query.user_id == user_id)
        .order_by(Query.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
