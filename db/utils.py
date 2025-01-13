"""
Database-related utility functions for managing database sessions.

This module provides functions for accessing and interacting with the database,
specifically a utility to create and yield a session for database transactions
using SQLAlchemy.

Functions:
- get_db: An asynchronous generator that provides a database session for use in
  CRUD operations. The session is automatically cleaned up after use.
"""

import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")


DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{dbname}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an active SQLAlchemy database session for performing database queries.

    This function should be used as a dependency in FastAPI routes to provide
    access to the database session, automatically handling session lifecycle
    and closing the session after the request is completed.

    Returns:
        An AsyncSession object for interacting with the database.
    """
    async with SessionLocal() as session:
        yield session
