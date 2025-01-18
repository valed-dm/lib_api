from sqlalchemy.ext.asyncio import AsyncSession

from db import Author


async def create_author(db: AsyncSession, author_data: dict) -> Author:
    """Create a new author."""
    new_author = Author(**author_data)
    async with db.begin():
        db.add(new_author)

    await db.refresh(new_author)
    return new_author
