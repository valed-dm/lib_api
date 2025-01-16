"""
Database-related utility functions for managing database sessions.

This module provides functions for accessing and interacting with the database,
specifically a utility to create and yield a session for database transactions
using SQLAlchemy.

Functions:
- get_db: An asynchronous generator that provides a database session for use in
  CRUD operations. The session is automatically cleaned up after use.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

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


async def upsert_entity(db: AsyncSession, entity_model, name: str, name_field="name"):
    """Upsert a single entity into the database and return the entity."""
    # Perform upsert (insert if not exists)
    stmt = insert(entity_model).values({name_field: name}).on_conflict_do_nothing()
    await db.execute(stmt)

    # Fetch the entity and return it
    column: Column[Any] = getattr(entity_model, name_field)
    stmt = select(entity_model).where(column == name)
    result = await db.execute(stmt)
    return result.scalar_one()


async def upsert_entities(
    db: AsyncSession,
    entity_model,
    names: list[str],
    name_field="name",
):
    """Upsert multiple entities, ensuring they exist and returning them."""
    entities = []

    # Ensure the name_field is valid in the model
    if name_field not in entity_model.__table__.columns:
        err_msg = f"Invalid column name for model {entity_model.__name__}: {name_field}"
        raise ValueError(err_msg)

    # Upsert entities one by one and collect results
    for name in names:
        try:
            entity = await upsert_entity(db, entity_model, name, name_field)
            entities.append(entity)
        except IntegrityError as e:  # noqa: PERF203
            exc_msg = (
                f"Integrity error on {name} with model {entity_model.__name__}: {e}"
            )
            raise ValueError(exc_msg) from e

    return entities
