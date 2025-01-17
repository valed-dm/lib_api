from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from book.crud.delete import delete_books
from db import User
from db.utils import get_db
from user.get import get_current_active_user

delete_books_router = APIRouter()


@delete_books_router.delete("/books/", status_code=204)
async def delete_books_route(
    db: Annotated[AsyncSession, Depends(get_db)],
    book_ids: list[int],
    _: Annotated[User, Security(get_current_active_user, scopes=["delete_books"])],
):
    """
    Route for deleting books.

    - Provide a list of `book_ids` to delete specific books.
    """
    try:
        deleted_count = await delete_books(db=db, book_ids=book_ids)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting books: {e!s}",
        ) from e

    return {"detail": f"{deleted_count} book(s) successfully deleted."}
