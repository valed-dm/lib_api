from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from book.book import BookCreate
from db import Author
from db import Book
from db import Category
from db import Image
from db.utils import upsert_entities


async def create_book(db: AsyncSession, book_data: BookCreate) -> Book:
    """
    Description:
        Creates a new book entry along with its associated authors,categories,
        and optional image.

    Parameters:
        db (AsyncSession): Database session.
        book_data (BookCreate): Book data to create.

    Returns:
        The created Book instance.

    Exceptions:
        ValueError: Raised if a database integrity error occurs.

    Dependencies:
        Database must enforce unique constraints on:
        - Author.name, - Category.name, - Image.image_src.

    Database Operations:
        Uses INSERT ... ON CONFLICT DO NOTHING to prevent duplicate rows.
        :param db:
        :param book_data:
        :return: Book instance.

    Sample Request Body:
        ```python
        {
            "title": "New Book Title",
            "description": "A brief description",
            "date": "2025-01-15",
            "google_book_id": "GID12345",
            "authors": ["Author One", "Author Two"],
            "categories": ["Fiction", "Adventure"],
            "image_src": "https://example.com/image.jpg"
        }
        ```
    """
    # Upsert authors
    author_names = [name.strip() for name in book_data.authors if name.strip()]
    authors = await upsert_entities(db, Author, author_names)

    # Upsert categories if provided
    cats = []
    if book_data.categories:
        category_names = [
            cat_name.strip() for cat_name in book_data.categories if cat_name.strip()
        ]
        cats = await upsert_entities(db, Category, category_names)

    # Upsert image if provided
    image = None
    if book_data.image_src:
        stmt = (
            insert(Image).values(image_src=book_data.image_src).on_conflict_do_nothing()
        )
        await db.execute(stmt)
        img_result = await db.execute(
            select(Image).where(Image.image_src == book_data.image_src),
        )
        image = img_result.scalar_one()

    # Create the book
    try:
        new_book = Book(
            title=book_data.title,
            description=book_data.description or "",
            date=book_data.date or None,
            google_book_id=book_data.google_book_id or None,
            authors=authors,
            categories=cats,
            image_src=image,
        )
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)
    except IntegrityError as e:
        await db.rollback()
        exc_msg = f"Failed to create book due to integrity error: {e!s}"
        raise ValueError(exc_msg) from e

    return new_book
