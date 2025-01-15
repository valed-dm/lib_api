"""Authors table model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.timestamp import TimestampMixin

if TYPE_CHECKING:
    from db import Book


class Author(Base, TimestampMixin):
    """
    Represents an author of books in the library system.

    Attributes:
        id (int): The unique identifier for the author.
        name (str): The full name of the author. Must be unique, max length 50.
        biography (str): A textual description. Defaults to empty string.
        years (str): The author's years of life, max length 10. Default to empty string.
        books (list[Book]): A list of books written by the author.

    Relationships:
        - books: Establishes a many-to-many relationship with the `Book` class using the
          `book_author` table as the intermediary. This allows authors to be
          linked to multiple books and books to have multiple authors.

    Notes:
        - The `name` column is enforced as unique.
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    biography: Mapped[str] = mapped_column(Text, default="")
    # Using a string to represent the years (birth - death)
    years: Mapped[str] = mapped_column(String(10), default="")
    books: Mapped[list[Book]] = relationship(
        "Book",
        secondary="book_author",
        back_populates="authors",
    )
