"""Books table model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.timestamp import TimestampMixin

if TYPE_CHECKING:
    from db import Author
    from db import Category
    from db import Image


class Book(Base, TimestampMixin):
    """
    Represents a book available in the library system.

    Attributes:
        id (int): The unique identifier for the book.
        title (str): The title of the book. This field is required and cannot exceed
        200 characters.
        description (str | None): A textual description or summary of the book.
        Default to empty string.
        date (Date | None): The publication date of the book. Can be left blank.
        google_book_id (str | None): A unique identifier for the book, sourced from
        Google's Book API. Can be left blank.

    Relationships:
        - authors (list[Author]): A many-to-many relationship linking the book to its
        authors, using the `book_author` table as the intermediary.
        - categories (list[Category]): A many-to-many relationship linking the book to
        its categories, using the `book_category` table as the intermediary.
        - image_src (Image | None): A one-to-one relationship linking the book to its
        associated image, if any.

    Notes:
        - The relationships enable the association of books with multiple authors and
        categories.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[Date | None] = mapped_column(Date, default=None, nullable=True)
    google_book_id: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        default=None,
        nullable=True,
    )
    authors: Mapped[list[Author]] = relationship(
        "Author",
        secondary="book_author",
        back_populates="books",
    )
    categories: Mapped[list[Category]] = relationship(
        "Category",
        secondary="book_category",
        back_populates="books",
    )
    image_src: Mapped[Image | None] = relationship(
        "Image",
        uselist=False,
        back_populates="book",
    )
