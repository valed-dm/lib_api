"""Categories table model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.timestamp import TimestampMixin

if TYPE_CHECKING:
    from db import Book


class Category(Base, TimestampMixin):
    """
    Represents a category or genre for organizing books.

    Attributes:
        id (int): The unique identifier for the category.
        name (str): The name of the category. Must be unique, with a maximum length
        of 30 characters.
        books (list[Book]): A list of books associated with this category.

    Relationships:
        - books: Establishes a many-to-many relationship with the `Book` class using the
          `book_category_association` table as the intermediary. This allows books to
          belong to multiple categories and categories to include multiple books.

    Notes:
        - The `name` column is enforced as unique to prevent duplicate categories.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    books: Mapped[list[Book]] = relationship(
        "Book",
        secondary="book_category",
        back_populates="categories",
    )
