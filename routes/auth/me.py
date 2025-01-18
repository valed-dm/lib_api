from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from db.utils import get_db
from library.me_items import get_me_borrowed_books
from user.get import get_current_active_user
from user.user import User

user_me_router = APIRouter()


@user_me_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["me"])],
):
    return current_user


@user_me_router.get("/users/me/items/")
async def get_user_borrowed_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        User,
        Security(get_current_active_user, scopes=["read"]),
    ],
):
    return await get_me_borrowed_books(db, current_user)
