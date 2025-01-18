from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from db import User
from db.utils import get_db
from library.add import intake_books
from library.book_return import return_books_from_user
from library.lend import lend_books_to_user
from library.schemas import LendingDataList
from library.schemas import LibraryCreate
from library.schemas import LibraryRead
from library.schemas import ReturnDataList
from user.get import get_current_active_user

library_router = APIRouter(prefix="/library", tags=["Library"])


@library_router.post("/", response_model=list[LibraryRead], status_code=201)
async def library_intake(
    intake_data: list[LibraryCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["librarian"])],
):
    """
    Add or update books in the library.
    - If the book already exists, increment its quantity.
    - If the book does not exist, create a new entry.
    """
    return await intake_books(db, [book.model_dump() for book in intake_data])


@library_router.post("/lend/", status_code=200)
async def lend_books(
    data: LendingDataList,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        User,
        Security(get_current_active_user, scopes=["librarian"]),
    ],
):
    """
    Endpoint to lend books to a user.

    Args:
        data (LendingDataList): List of books to borrow.
        db (AsyncSession): Async database session.
        _: Check if user is authenticated as librarian.

    Returns:
        JSONResponse: Response with returned book details or errors.
    """
    try:
        return await lend_books_to_user(db, data.lending_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@library_router.post("/return", status_code=200)
async def return_books(
    data: ReturnDataList,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        User,
        Security(get_current_active_user, scopes=["librarian"]),
    ],
):
    """
    Endpoint to return books lent to a user.

    Args:
        data (ReturnDataList): List of books to return.
        db (AsyncSession): Async database session.
        _: Check if user is authenticated as librarian.

    Returns:
        JSONResponse: Response with returned book details or errors.
    """
    try:
        return await return_books_from_user(db, data.return_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
