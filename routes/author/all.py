from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from author.crud.create import create_author
from author.crud.delete import delete_hovering_author
from author.crud.get import get_author_by_name
from author.crud.get_all import get_authors
from author.schemas.all import AuthorBase
from author.schemas.all import AuthorCreate
from author.schemas.all import AuthorRead
from db.users import User
from db.utils import get_db
from user.get import get_current_active_user

author_router = APIRouter(prefix="/authors", tags=["authors"])


@author_router.post("/", response_model=AuthorBase, status_code=201)
async def create_author_endpoint(
    author_data: AuthorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["create"])],
):
    """
    Create a new author in the database.

    This endpoint accepts the author's details and creates a new record in the
    authors table. It requires authentication, and the user must have the "create"
    scope to perform this action.

    **Fields**:
    - `author_data` (AuthorCreate): The data for the new author, including name,
    biography, etc.

    **Response**:
    - Returns the created author with their basic details in `AuthorBase` format.
    - HTTP Status: 201 Created.

    **Permissions**:
    - The user must have an active session and the "create" scope to execute this
    operation.
    """
    return await create_author(db, author_data.model_dump())


@author_router.get("/", response_model=list[AuthorRead])
async def list_authors(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["read"])],
    limit: int = 10,
    offset: int = 0,
):
    """
    Retrieve a list of all authors from the database.

    This endpoint retrieves a paginated list of authors, and it requires authentication.
    The user must have the "read" scope to access the list of authors.

    **Query Parameters**:
    - `limit` (int, default=10): The maximum number of authors to retrieve per page.
    - `offset` (int, default=0): The starting point (index) from which authors are
    fetched.

    **Response**:
    - Returns a list of authors, with each author object serialized to the `AuthorRead`.
    - The list can be paginated by `limit` and `offset`.
    - HTTP Status: 200 OK.

    **Permissions**:
    - The user must have an active session and the "read" scope to execute this.
    """
    return await get_authors(db, limit, offset)


@author_router.get("/{name}", response_model=AuthorRead)
async def get_author_endpoint(
    name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["read"])],
):
    """
    Retrieve a single author from the database by their name.

    This endpoint fetches the author whose name matches the provided `name`.
    It requires the user to be authenticated and to have the "read" scope.

    **Path Parameter**:
    - `name` (str): The name of the author to be retrieved.

    **Response**:
    - Returns the author details serialized into the `AuthorRead` format.
    - HTTP Status: 200 OK if the author exists, or 404 Not Found if no author matches.

    **Permissions**:
    - The user must be authenticated and have the "read" scope to access this.
    """
    return await get_author_by_name(db, name)


@author_router.delete("/{name}", response_model=AuthorBase, status_code=200)
async def delete_author_endpoint(
    name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["delete_author"])],
):
    """
    Delete an author from the database who is not linked to any books.

    This endpoint attempts to delete an author from the database by their name.
    The deletion will only be allowed if the author is not linked to any books.
    It requires the user to be authenticated and to have the "delete_author" scope.

    **Path Parameter**:
    - `name` (str): The name of the author to be deleted.

    **Response**:
    - Returns the author details that were deleted, serialized into the `AuthorBase`.
    - HTTP Status: 200 OK if the author is successfully deleted.
    - HTTP Status: 400 if the author is linked to books.
    - HTTP Status: 404 if the author cannot be found.

    **Permissions**:
    - The user must be authenticated and have the "delete_author" scope to access this.
    """
    return await delete_hovering_author(db, name)
