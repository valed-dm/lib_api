from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from sqlalchemy.ext.asyncio import AsyncSession

from db import User
from db.utils import get_db
from library.add import intake_books
from library.schemas import LibraryCreate
from library.schemas import LibraryRead
from user.get import get_current_active_user

library_router = APIRouter(prefix="/library", tags=["Library"])


@library_router.post("/", response_model=list[LibraryRead], status_code=201)
async def library_intake(
    intake_data: list[LibraryCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Security(get_current_active_user, scopes=["manage_library"])],
):
    """
    Add or update books in the library.
    - If the book already exists, increment its quantity.
    - If the book does not exist, create a new entry.
    """
    return await intake_books(db, [book.model_dump() for book in intake_data])
