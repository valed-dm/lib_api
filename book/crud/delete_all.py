from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete

from db import Book


async def delete_all_books(db: AsyncSession) -> int:
    """
    Service function to delete all books from the database.

    Returns the number of rows deleted.
    """
    async with db.begin():
        stmt = delete(Book)
        result = await db.execute(stmt)

    await db.commit()  # Commit the changes

    return result.rowcount
