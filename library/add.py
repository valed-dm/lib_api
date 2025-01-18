from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Book
from db import Library


async def intake_books(
    db: AsyncSession,
    intake_data: list[dict],
) -> list[Library]:
    """
    Add books to the library (initialize or update quantities).
    Args:
        db: AsyncSession - database session
        intake_data: list[dict] - [{'book_id': int, 'quantity_available': int}, ...]

    Returns:
        list[Library] - list of added or updated Library entries
    """
    updated_libraries = []
    async with db.begin():
        for entry in intake_data:
            book_id = entry["book_id"]
            quantity_available = entry["quantity_available"]

            # Ensure book exists in books table
            book_exists = await db.scalar(
                select(Book).where(Book.id == book_id),
            )
            if not book_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Book with id {book_id} does not exist",
                )

            # Insert or update quantity
            stmt = select(Library).where(Library.book_id == book_id)
            result = await db.execute(stmt)
            existing_record = result.scalar_one_or_none()

            if existing_record:
                # Update quantity if book already exists
                existing_record.quantity_available += quantity_available
            else:
                # Create a new library entry
                new_library = Library(
                    book_id=book_id,
                    quantity_available=quantity_available,
                )
                db.add(new_library)
                updated_libraries.append(new_library)

    return updated_libraries
