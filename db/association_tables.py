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

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table

from db import Base

book_author_association = Table(
    "book_author",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


book_category_association = Table(
    "book_category",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)
