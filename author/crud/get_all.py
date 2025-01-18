from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import Author


async def get_authors(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
) -> list[Author]:
    """
    Retrieve a paginated list of authors.

    Args:
        db: Database session.
        limit: Number of authors to retrieve.
        offset: Number of authors to skip (for pagination).

    Returns:
        A list of authors.
    """
    stmt = (
        select(Author)
        .options(selectinload(Author.books))
        .order_by(Author.id)
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)

    return list(result.scalars().all())
