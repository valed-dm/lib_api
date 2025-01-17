from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete

from db import Book


async def delete_books(
    db: AsyncSession,
    book_ids: list[int],
) -> int | None:
    """
    Service function to delete books.

    - If `book_ids` is provided, only those books are deleted.

    Returns the number of rows deleted.
    """
    async with db.begin():
        stmt = delete(Book).where(Book.id.in_(book_ids))
        result = await db.execute(stmt)

        if not book_ids and result.rowcount == 0:
            msg = "No books were found to delete."
            raise ValueError(msg)

    await db.commit()

    return result.rowcount
