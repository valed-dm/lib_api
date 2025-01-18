from __future__ import annotations

from typing import Any

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Book
from db import Reader
from db import User


async def get_borrowed_books_grouped_by_user(
    db: AsyncSession,
    name: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, list[dict[str, Any]]]:
    """
    Retrieve all borrowed books grouped by user_id.

    Args:
        db (AsyncSession): Database session.
        name (str, optional): Username to filter books by.
        limit (int, optional): Number of books to return.
        offset (int, optional): Offset.

    Returns:
        dict: Grouped data by user_id.
    """
    stmt = (
        select(
            User.username,
            User.id,
            Reader.book_id,
            Book.title.label("book_title"),
            Reader.lent_till,
            (func.date(Reader.lent_till) - func.current_date()).label(
                "days_to_return_left",
            ),
        )
        .join(Reader, User.id == Reader.user_id)
        .join(Book, Reader.book_id == Book.id)
    )

    if name:
        stmt = stmt.where(User.username == name)

    stmt = stmt.order_by(User.username).limit(limit).offset(offset)

    result = await db.execute(stmt)

    # Grouping by username
    books_by_user: dict[str, list[dict[str, Any]]] = {}
    for (
        username,
        user_id,
        book_id,
        book_title,
        lent_till,
        days_to_return_left,
    ) in result:
        if username not in books_by_user:
            books_by_user[username] = []
        books_by_user[username].append(
            {
                "user_id": user_id,
                "book_id": book_id,
                "book_title": book_title,
                "lent_till": lent_till,
                "days_to_return_left": days_to_return_left,
            },
        )

    return books_by_user
