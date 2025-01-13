"""Authors table model."""

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

if TYPE_CHECKING:
    from db import Book


class Author(Base):
    """
    Represents an author of books in the library system.

    Attributes:
        id (int): The unique identifier for the author.
        name (str): The full name of the author. Must be unique, with a maximum length
        of 50 characters.
        biography (str | None): A textual description of the author's life and work.
        Can be left blank.
        birthdate (Date): The author's date of birth. Defaults to "1900-01-01"
        if unspecified.
        deathdate (Date): The author's date of death. Defaults to "1900-01-01"
        if unspecified.
        books (list[Book]): A list of books written by the author.

    Relationships:
        - books: Establishes a many-to-many relationship with the `Book` class using the
          `book_author_association` table as the intermediary. This allows authors to be
          linked to multiple books and books to have multiple authors.

    Notes:
        - The `name` column is enforced as unique to prevent duplicate entries for
        the same author.
        - The `birthdate` and `deathdate` default to "1900-01-01", serving
        as placeholders if specific dates are unknown.
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    biography: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    birthdate: Mapped[Date] = mapped_column(Date, default="1900-01-01")
    deathdate: Mapped[Date] = mapped_column(Date, default="1900-01-01")
    books: Mapped[list[Book]] = relationship(
        "Book",
        secondary="book_author",
        back_populates="authors",
    )
