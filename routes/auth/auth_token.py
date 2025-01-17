import logging
import os
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import authenticate_user
from auth.auth import create_access_token
from auth.token_schema import Token
from db.utils import get_db

logger = logging.getLogger(__name__)

user_token_router = APIRouter()

TOKEN_TYPE = os.environ["TOKEN_TYPE"]
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


@user_token_router.post("/token")
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
