"""Library's books available model."""

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.base import Base


class Library(Base):
    """
    Represents the library inventory that tracks the available quantity of books.

    Attributes:
        id (int): The unique identifier for the library entry.
        book_id (int): A foreign key referencing the ID of a book in the "books" table.
        quantity_available (int): The number of copies of the book available
        in the library. Defaults to 0.

    Relationships:
        - book_id: Establishes a relationship with the "books" table,
        linking a book to its availability in the library.
    """

    __tablename__ = "libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
