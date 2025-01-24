from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Annotated
from typing import ClassVar

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AuthorRead(BaseModel):
    id: int
    name: str

    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class CategoryRead(BaseModel):
    id: int
    name: str

    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class ImageRead(BaseModel):
    id: int
    image_src: str

    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class BookRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    date: Annotated[date | None, Field(default=None)]
    google_book_id: str | None = None
    created_at: datetime
    updated_at: datetime
    authors: list[AuthorRead]
    categories: list[CategoryRead]
    image_src: ImageRead | None = None

    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
