"""Library's readers lent out books model."""

from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.base import Base
from db.timestamp import TimestampMixin


class Reader(Base, TimestampMixin):
    """
    Represents a record of a user borrowing a book from the library.

    Attributes:
        id (int): The primary key for the reader entry.
        user_id (int): The foreign key referencing the user who borrowed the book.
        Links to the `users` table.
        book_id (int): The foreign key referencing the borrowed book (`books` table).
        lent_out (Date): The date when the book was borrowed.
        lent_till (Date): The date by which the book must be returned.
        limit (int): The maximum number of books a user can borrow. Defaults to 5.
    """

    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    lent_out: Mapped[Date] = mapped_column(Date, nullable=False)
    lent_till: Mapped[Date] = mapped_column(Date, nullable=False)
    limit: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
