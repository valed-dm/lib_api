from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from book.crud.get import get_books
from book.schemas.read import BookRead
from book.schemas.search import BookSearchSchema
from db import User
from db.utils import get_db
from user.get import get_current_active_user

get_books_router = APIRouter()


@get_books_router.get("/books/", response_model=list[BookRead], status_code=200)
async def get_books_endpoint(
    search_args: Annotated[BookSearchSchema, Depends(BookSearchSchema)],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["read"])],
):
    """
    Get a list of books with optional filtering, sorting, and pagination.

    Query Parameters:
    - **title** (`str`, optional): Search for books by a partial match on the title.
    - **author** (`str`, optional): Search for books by a partial match on the name.
    - **category** (`str`, optional): Search for books by a partial match on the name.
    - **sort_by** (`str`, default=`"date"`): Sort by (`"date"` or `"title"`).
    - **order** (`str`, default=`"desc"`): Sorting order, either `"asc"` or `"desc"`.
    - **limit** (`int`, default=`10`): Number of books per page.
    - **offset** (`int`, default=`0`): Number of records to skip for pagination.

        Responses:
        - **200 OK**: A list of books matching the criteria.
        - **400 Bad Request**: Invalid input or query parameters.
        - **401 Unauthorized**: User authentication is required.
        - **403 Forbidden**: The user lacks necessary scopes to access this resource.

        Returns:
        - `list[BookRead]`: A list of books matching the search and filtering criteria.
    """
    try:
        books = await get_books(db=db, **search_args.model_dump(exclude_none=True))

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    else:
        return books
