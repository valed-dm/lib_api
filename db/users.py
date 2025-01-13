"""Users table model."""

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from db import Base


class User(Base):
    """
    User model for database interaction.

    This model represents a user entity within the application and contains the
    following fields:

    - id: The unique identifier for the user (Primary Key).
    - username: The user's unique username (indexed and required).
    - email: The user's email address (unique, nullable).
    - hashed_password: The user's password (hashed for security).
    - full_name: The user's full name (nullable).
    - disabled: A boolean flag indicating whether the user's account is disabled.
    - scopes: A string representing the user's permission scopes (nullable).

    This model is designed to interact with a SQLAlchemy database using
    asynchronous sessions.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The unique username associated with the user.
        email (Optional[str]): The user's email address. Can be None.
        hashed_password (str): The user's hashed password.
        full_name (Optional[str]): The user's full name. Can be None.
        disabled (bool): Whether the user is disabled or not.
        scopes (Optional[str]): A space-separated string of the user's permissions.
        Can be None.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    disabled = Column(Boolean, default=False)
    scopes = Column(String, nullable=True)
