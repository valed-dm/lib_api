from __future__ import annotations

from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Library
from db import Reader
from library.schemas import ReturnData


async def return_books_from_user(
    db: AsyncSession,
    return_data: list[ReturnData],
) -> JSONResponse:
    """
    Handle book returns based on lending data.

    Args:
        db (AsyncSession): Database session.
        return_data (list[LendingData]): List of return entries, each containing
        "user_id" and "book_id".

    Returns:
        JSONResponse: Details of the returned books or errors for failed operations.
    """
    return_details = []

    async with db.begin():
        for item in return_data:
            user_id = item.user_id
            book_id = item.book_id

            # Find reader entry
            reader_stmt = select(Reader).where(
                Reader.user_id == user_id,
                Reader.book_id == book_id,
            )
            reader_result = await db.execute(reader_stmt)
            reader_entry = reader_result.scalar_one_or_none()

            if not reader_entry:
                return JSONResponse(
                    status_code=404,
                    content={
                        "detail": f"Book {book_id} "
                        f"is not currently lent to user {user_id}.",
                    },
                )

            # Delete the reader entry
            await db.delete(reader_entry)

            # Update library entry
            library_stmt = select(Library).where(Library.book_id == book_id)
            library_result = await db.execute(library_stmt)
            library_entry = library_result.scalar_one_or_none()

            if not library_entry:
                return JSONResponse(
                    status_code=404,
                    content={
                        "detail": f"Book {book_id} does not exist in the library.",
                    },
                )

            library_entry.quantity_available += 1
            db.add(library_entry)

            return_details.append(
                {
                    "user_id": user_id,
                    "book_id": book_id,
                    "status": "Returned",
                },
            )

    return JSONResponse(
        status_code=200,
        content={"returned_books": return_details},
    )
