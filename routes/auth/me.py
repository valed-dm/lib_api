from typing import Annotated

from fastapi import APIRouter
from fastapi import Security

from user.get import get_current_active_user
from user.user import User

user_me_router = APIRouter()


@user_me_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])],
):
    return current_user
