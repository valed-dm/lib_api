from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


TOKEN_TYPE = os.environ["TOKEN_TYPE"]


class Token(BaseModel):
    """
    Represents an access token and its type returned after successful authentication.

    Attributes:
        access_token (str): The JWT token issued to the user after authentication.
        token_type (str): The type of the token, usually "bearer" for OAuth 2.0 tokens.
        Defaults to "bearer".
    """

    access_token: str
    token_type: str = TOKEN_TYPE


class TokenData(BaseModel):
    """
    Represents the data encoded within an access token. It usually includes
    user information such as username and scopes.

    Attributes:
        username (str): The username of the authenticated user.
        scopes (str): A string representing the OAuth 2.0 scopes associated with
        the user.
    """

    username: str
    scopes: str
