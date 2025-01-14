"""Users table model."""

from __future__ import annotations

from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db import TimestampMixin
from db.base import Base


class User(Base, TimestampMixin):
    """
    User model for database interaction.

    This model represents a user entity within the application and contains the
    following fields:

    - id: The unique identifier for the user (Primary Key).
    - username: The user's unique username (indexed and required).
    - email: The user's email address (unique, default to None).
    - hashed_password: The user's password hashed for security.
    - full_name: The user's full name (default to None).
    - disabled: A boolean flag indicating whether the user's account is disabled.
    - scopes: A string representing the user's permission scopes.
    Default to empty string.

    This model is designed to interact with a SQLAlchemy database using
    asynchronous sessions.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The unique username associated with the user.
        email (str | None): The user's email address. Default to None.
        hashed_password (str): The user's hashed password.
        full_name (str | None): The user's full name. Default to None.
        disabled (bool): Whether the user is disabled or not. Default to False.
        scopes (str): A space-separated string of the user's permissions.
        Default to empty string.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        default=None,
        nullable=True,
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, default=None, nullable=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    scopes: Mapped[str] = mapped_column(String, default="")
