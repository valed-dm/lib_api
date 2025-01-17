from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from book.crud.delete_all import delete_all_books
from book.schemas.delete import DeleteBooksResponse
from db import User
from db.utils import get_db
from user.get import get_current_active_user

delete_all_books_router = APIRouter()


@delete_all_books_router.delete(
    "/books/all",
    response_model=DeleteBooksResponse,
    status_code=200,
)
async def delete_all_books_route(
    db: Annotated[AsyncSession, Depends(get_db)],
    confirm: Annotated[
        bool,
        Query(description="Confirm the deletion of all books"),
    ],
    _: Annotated[User, Security(get_current_active_user, scopes=["superuser"])],
):
    """
    Route for deleting all books.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required to delete all books.",
        )

    try:
        deleted_count = await delete_all_books(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting all books: {e!s}",
        ) from e

    return DeleteBooksResponse(
        message="Book(s) deleted successfully"
        if deleted_count > 0
        else "No book found to delete",
        deleted_count=deleted_count,
    )
