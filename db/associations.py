"""
book_author_association:
Represents the many-to-many relationship between books and authors.

Columns:
    - book_id (int): Foreign key referencing the `id` field in the `books` table.
    Acts as a primary key in this table.
    - author_id (int): Foreign key referencing the `id` field in the `authors` table.
    Acts as a primary key in this table.

Purpose:
    - This table allows each book to have multiple authors and each author to be linked
    to multiple books.

book_category_association:
Represents the many-to-many relationship between books and categories.

Columns:
    - book_id (int): Foreign key referencing the `id` field in the `books` table.
    Acts as a primary key in this table.
    - category_id (int): Foreign key referencing the `id` field in the `categories`
    table. Acts as a primary key in this table.

Purpose:
    - This table enables the association of each book with multiple categories and each
    category to include multiple books.
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.base import Base


class BookAuthorAssociation(Base):
    """
    Association table for the many-to-many relationship between books and authors.
    """

    __tablename__ = "book_author"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), primary_key=True)


class BookCategoryAssociation(Base):
    """
    Association table for the many-to-many relationship between books and categories.
    """

    __tablename__ = "book_category"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        primary_key=True,
    )
