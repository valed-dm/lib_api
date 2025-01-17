import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from book.crud.update import update_book
from book.schemas.read import BookRead
from book.schemas.update import BookUpdate
from db import User
from db.utils import get_db
from user.get import get_current_active_user

logger = logging.getLogger(__name__)

patch_book_router = APIRouter()


@patch_book_router.patch("/books/{book_id}", response_model=BookRead)
async def update_book_route(
    book_id: int,
    book_data: BookUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["update"])],
):
    """
    Update an existing book by its ID.

    **Parameters**:
    - `book_id`: The ID of the book to be updated.
    - `book_data`: Partial data for updating the book. Missing fields stay unchanged.

    **Return**:
    - The updated book record as a BookRead model.

    **Error Responses**:
    - `404 Not Found`: If the book with the given ID is not found.
    """
    try:
        updated_book = await update_book(db, book_id, book_data)
    except HTTPException as e:
        exc_msg = f"HTTPException occurred: {e.detail}"
        logger.exception(exc_msg)
        raise

    return updated_book
