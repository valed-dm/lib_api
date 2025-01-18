from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Book
from db import Reader
from db import User
from library.schemas import BorrowedItem


async def get_me_borrowed_books(
    db: AsyncSession,
    current_user: User,
):
    """
    Fetch all borrowed books for the currently authenticated user.
    """
    stmt = (
        select(
            Reader.book_id,
            Book.title.label("book_title"),
            Reader.lent_till,
            (Reader.lent_till - func.current_date().label("days_to_return_left")).label(
                "days_to_return_left",
            ),
        )
        .join(Book, Reader.book_id == Book.id)
        .where(Reader.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    borrowed_books = [
        BorrowedItem(
            book_id=row.book_id,
            book_title=row.book_title,
            lent_till=row.lent_till,
            days_to_return_left=int(row.days_to_return_left or 0),
        )
        for row in result.fetchall()
    ]
    return borrowed_books  # noqa: RET504
