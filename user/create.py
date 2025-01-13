"""Create a new user module."""

import logging

from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import get_password_hash
from db.users import User
from user.get import get_user
from user.user import UserCreate

logger = logging.getLogger("CREATE_USER")


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Ensures that the username and email are unique before adding the user.
    Handles race conditions gracefully by catching database-level integrity
    errors and providing meaningful responses to the user.

    Args:
        db (AsyncSession): The SQLAlchemy async database session.
        user (UserCreate): The input data for creating a user.

    Returns:
        User: The newly created user object.

    Raises:
        HTTPException: If the username is already registered.
        HTTPException: If the email is already registered.
        HTTPException: For any unexpected database integrity errors.

    Example:
        ```python
        new_user = await create_user(db, UserCreate(
            username="new_user",
            email="new_user@example.com",
            password="securepassword123",
        ))
        ```
    """
    db_user_by_username = await get_user(db, user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user_by_email = await db.execute(select(User).where(User.email == user.email))
    if db_user_by_email.scalars().first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=str(user.email) or None,
        hashed_password=hashed_password,
        full_name=user.full_name,
        disabled=user.disabled,
        scopes=user.scopes or "me reader",
    )

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    except IntegrityError as e:
        # Rollback on any database integrity errors
        await db.rollback()
        logger.warning(
            "Database IntegrityError",
            extra={
                "constraint": str(e.orig),
                "username": user.username,
                "email": user.email,
            },
        )

        if "users_username_key" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail="Username already taken.",
            ) from e
        if "users_email_key" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail="Email already taken.",
            ) from e

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred.",
        ) from e

    return db_user
