from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from book.crud.create import create_book
from book.schemas.create import BookCreate
from db import User
from db.utils import get_db
from user.get import get_current_active_user

create_book_router = APIRouter()


@create_book_router.post("/books/", status_code=201)
async def create_book_route(
    book_data: BookCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["create"])],
):
    """
    Create a new book.

    This endpoint allows creating a new book by providing required details such as
    title, description, authors, categories, and other book-related information.

    **Request Body:**
    - **title** (`str`, required): The title of the book. (max length: 255)
    - **description** (`str`, optional): A short description of the book.
    - **date** (`date`, optional): The publication date of the book (optional).
    - **google_book_id** (`str`, optional): The Google Books API ID (optional).
    - **authors** (`List[str]`, required): A list of author names for a book.
    - **categories** (`List[str]`, required): A list of category names for a book.
    - **image_src** (`str`, optional): URL of an image for the book.

    **Request Example:**

    ```json
    {
      "title": "The Great Python",
      "description": "An in-depth guide to Python programming.",
      "date": "2025-03-01",
      "google_book_id": "google-id-1234",
      "authors": ["John Doe", "Jane Doe"],
      "categories": ["Programming", "Python"],
      "image_src": "https://example.com/book-image.jpg"
    }
    ```

    **Responses:**
    - **201 Created**: The book was successfully created.
        - Returns the book object in the response body.

    **Response Body (201):**
    ```json
    {
      "id": 3,
      "title": "The Great Python",
      "description": "An in-depth guide to Python programming.",
      "date": "2025-03-01",
      "google_book_id": "google-id-1234",
      "created_at": "2025-03-01T00:00:00Z",
      "updated_at": "2025-03-01T00:00:00Z",
      "authors": ["John Doe", "Jane Doe"],
      "categories": ["Programming", "Python"]
    }
    ```

    - **400 Bad Request**: The request data is invalid or incomplete.
        - Returns an error message describing what went wrong.

    **Raises**:
    - **ValidationError**: If the book data is not valid or violates schema rules
    (e.g., required fields missing).
    - **HTTPException**: If an error occurs while creating the book in the database.

    This endpoint only allows users with the `"create"` scope to access it.

    **Security**:
    - Only authenticated users with the `create` permission can create a book.
    Unauthorized access will return a `401 Unauthorized` response.
    """
    return await create_book(db, book_data)
