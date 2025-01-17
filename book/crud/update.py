from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from book.schemas.update import BookUpdate
from db import Author
from db import Book
from db import Category
from db import Image
from db.utils import upsert_entities


async def update_book(
    db: AsyncSession,
    book_id: int,
    book_data: BookUpdate,
) -> Book:
    """
    Update a book with the provided data.

    Args:
        db (AsyncSession): The database session for performing database operations.
        book_id (int): The ID of the book to update.
        book_data (BookUpdate): A Pydantic model containing the update details for book.

    Returns:
        Book: The updated book instance from the database.

    Raises:
        HTTPException: If the book with the given ID is not found.
    """
    # Use a transaction to ensure consistency
    async with db.begin():
        # Fetch the book and related entities
        stmt = (
            select(Book)
            .where(Book.id == book_id)
            .options(
                selectinload(Book.authors),
                selectinload(Book.categories),
                selectinload(Book.image_src),
            )
        )
        result = await db.execute(stmt)
        book = result.scalars().first()

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Update fields dynamically
        updates = {
            "title": book_data.title,
            "description": book_data.description,
            "date": book_data.date if isinstance(book_data.date, date) else None,
            "google_book_id": book_data.google_book_id,
        }

        for field, value in updates.items():
            if value is not None:
                setattr(book, field, value)

        # Handle many-to-many relationships
        if book_data.authors is not None:
            book.authors = await upsert_entities(db, Author, book_data.authors)

        if book_data.categories is not None:
            book.categories = await upsert_entities(db, Category, book_data.categories)

        if book_data.image_src is not None:
            image = await upsert_entities(
                db,
                Image,
                [book_data.image_src],
                name_field="image_src",
            )
            book.image_src = image[0]

        # Add the updated book to the session
        db.add(book)

    # Commit and refresh
    await db.commit()
    await db.refresh(book)
    return book
