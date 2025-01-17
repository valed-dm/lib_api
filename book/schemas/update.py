from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel
from pydantic import Field


class BookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    date: Annotated[date | None, Field(default=None)]
    google_book_id: str | None = None
    authors: list[str] | None = None
    categories: list[str] | None = None
    image_src: str | None = None

    class Config:
        from_attributes = True
