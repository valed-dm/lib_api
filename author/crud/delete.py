from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import Author


async def delete_hovering_author(db: AsyncSession, name: str) -> Author:
    """
    Delete an author not linked to any books.

    Args:
        db: Database session.
        name: Name of the author to delete.
    """
    async with db.begin():  # Automatically handles commit/rollback
        stmt = (
            select(Author)
            .where(Author.name == name)
            .options(selectinload(Author.books))
        )
        result = await db.execute(stmt)
        author = result.scalars().first()

        if not author:
            raise HTTPException(status_code=404, detail="Author not found")

        if author.books:  # The author is linked to books
            raise HTTPException(
                status_code=400,
                detail="Cannot delete author linked to books. Remove the books first.",
            )

        await db.execute(delete(Author).where(Author.id == author.id))
        return author
