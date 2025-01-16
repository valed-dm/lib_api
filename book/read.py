from __future__ import annotations

from datetime import date
from datetime import datetime

from pydantic import BaseModel


class AuthorRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ImageRead(BaseModel):
    id: int
    image_src: str

    class Config:
        from_attributes = True


class BookRead(BaseModel):
    id: int
    title: str
    description: str | None
    date: date | None
    google_book_id: str | None
    created_at: datetime
    updated_at: datetime
    authors: list[AuthorRead]
    categories: list[CategoryRead]
    image_src: ImageRead | None

    class Config:
        from_attributes = True
