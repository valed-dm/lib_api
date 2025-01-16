import logging
import os
from datetime import timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Security
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import authenticate_user
from auth.auth import create_access_token
from auth.token_schema import Token
from book.crud.create import create_book
from book.crud.get import get_books
from book.schemas.create import BookCreate
from book.schemas.read import BookRead
from book.schemas.search import BookSearchSchema
from db.utils import get_db
from user.create import create_user
from user.get import get_current_active_user
from user.user import User
from user.user import UserCreate
from user.user import UserOut

load_dotenv()
app = FastAPI()

logger = logging.getLogger(__name__)

TOKEN_TYPE = os.environ["TOKEN_TYPE"]
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


@app.post("/register", response_model=UserOut)
async def register_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Register a new user in the system.

    This endpoint creates a new user by first ensuring that the username and email
    are unique. Then, it proceeds with hashing the password and storing the user's
    data in the database. If a user with the given username or email already exists,
    an appropriate error message is returned.

    Args:
        user (UserCreate): The data required to create the new user, such as
                            username, email, password, etc.
        db (AsyncSession): The database session used to interact with the database.

    Returns:
        UserOut: The newly created user information, as outputted by the UserOut
                 Pydantic model (response model).

    Raises:
        HTTPException: If the username or email is already taken, an HTTP error
                       is raised with an appropriate message.
    """
    return await create_user(db, user)


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Login for access token using username and password.

    This endpoint authenticates a user using their username and password.
    If the authentication is successful, it generates an access token (JWT)
    that can be used for making authenticated requests to the system.

    The generated access token contains the user's username and scopes
    in its payload and is returned with a Bearer authentication type.

    Args:
        form_data (OAuth2PasswordRequestForm): Form data that includes the username
                                                and password used for authentication.
        db (AsyncSession): Asynchronous database session used for fetching the user
                           and verifying the credentials.

    Returns:
        Token: A response model containing the access token in a Bearer format.

    Raises:
        HTTPException: If the authentication fails (incorrect username or password),
                       a 401 Unauthorized error is raised with a specific message.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)

    if user is None:
        warning_msg = f"Failed login attempt for username: {form_data.username}"
        logger.warning(warning_msg)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type=TOKEN_TYPE)


@app.post("/books/", status_code=201)
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


@app.get("/books/", response_model=list[BookRead], status_code=200)
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


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["items"])],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/status/")
async def read_system_status(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["admin"])],
):
    return {"status": "ok", "admin": current_user.username}
