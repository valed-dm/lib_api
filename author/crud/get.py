from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import Author


async def get_author_by_name(db: AsyncSession, name: str) -> Author:
    """Retrieve a single author by name."""
    stmt = (
        select(Author)
        .options(selectinload(Author.books))
        .where(Author.name.ilike(f"%{name}%"))
    )
    result = await db.execute(stmt)
    author = result.scalars().first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author
