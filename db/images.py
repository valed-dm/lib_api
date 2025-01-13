"""Images table model."""

from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db import Base
from db.books import Book


class Image(Base):
    """
    Represents an image associated with a book.

    Attributes:
        id (int): The unique identifier for the image.
        image_src (str): The URL of the image. Maximum length is 200 characters.
        book_id (int | None): A foreign key referencing the ID of the associated book
         in the "books" table. This is unique, as each book can have at most one
         associated image.

    Relationships:
        - book: Establishes a one-to-one relationship with the `Book` class,
        linking a book to its associated image.

    Notes:
        - The `book_id` column enforces a unique constraint to ensure that
        a book cannot have multiple images.
    """

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_src: Mapped[str] = mapped_column(String(200), nullable=False)
    book_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("books.id"),
        unique=True,
    )
    book: Mapped[Book | None] = relationship(Book, back_populates="image_src")
