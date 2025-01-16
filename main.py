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
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import authenticate_user
from auth.auth import create_access_token
from auth.token_schema import Token
from book.book import BookCreate
from book.create import create_book
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
    return await create_book(db, book_data)


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
