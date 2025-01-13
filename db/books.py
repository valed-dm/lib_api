"""Books table model."""

from __future__ import annotations

from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db import Base
from db.association_tables import book_author_association
from db.association_tables import book_category_association
from db.authors import Author
from db.categories import Category
from db.images import Image


class Book(Base):
    """
    Represents a book available in the library system.

    Attributes:
        id (int): The unique identifier for the book.
        title (str): The title of the book. This field is required and cannot exceed
        200 characters.
        description (str | None): A textual description or summary of the book.
        Defaults to an empty string if not provided.
        date (Date): The publication date of the book. Defaults to "1900-01-01"
        if unspecified.
        google_book_id (str): A unique identifier for the book, sourced from
        Google's Book API. This field is required and must be unique.

    Relationships:
        - authors (list[Author]): A many-to-many relationship linking the book to its
        authors,
          using the `book_author_association` table as the intermediary.
        - categories (list[Category]): A many-to-many relationship linking the book to
        its categories,
          using the `book_category_association` table as the intermediary.
        - image_src (Image | None): A one-to-one relationship linking the book to its
        associated image, if any.

    Notes:
        - The `google_book_id` field ensures that each book in the database has a unique
         reference, avoiding duplicates.
        - The `date` defaults to "1900-01-01" to serve as a placeholder for missing
        publication dates.
        - The relationships enable the association of books with multiple authors and
        categories.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    date: Mapped[Date] = mapped_column(Date, default="1900-01-01")
    authors: Mapped[list[Author]] = relationship(
        "Author",
        secondary=book_author_association,
        back_populates="books",
    )
    categories: Mapped[list[Category]] = relationship(
        "Category",
        secondary=book_category_association,
        back_populates="books",
    )
    google_book_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    image_src: Mapped[Image | None] = relationship(
        "Image",
        uselist=False,
        back_populates="book",
    )
