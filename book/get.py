from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import Author
from db import Book
from db import Category


async def get_books(db: AsyncSession, **kwargs) -> list[Book]:
    query = select(Book).options(
        selectinload(Book.authors),
        selectinload(Book.categories),
        selectinload(Book.image_src),
    )

    # Filters
    filters = []
    if title := kwargs.get("title"):
        filters.append(Book.title.ilike(f"%{title}%"))
    if author := kwargs.get("author"):
        filters.append(Book.authors.any(Author.name.ilike(f"%{author}%")))
    if category := kwargs.get("category"):
        filters.append(Book.categories.any(Category.name.ilike(f"%{category}%")))

    if filters:
        query = query.where(*filters)

    # Sorting
    sort_by = kwargs.get("sort_by", "date")
    order = kwargs.get("order", "desc")
    if sort_by in {"date", "title"}:
        sort_column = getattr(Book, sort_by)
        sort_order = sort_column.desc() if order == "desc" else sort_column.asc()
        query = query.order_by(sort_order)

    # Pagination
    limit = kwargs.get("limit", 10)
    offset = kwargs.get("offset", 0)
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())
