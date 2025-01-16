from __future__ import annotations

from datetime import date
from typing import Annotated

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator


class BookCreate(BaseModel):
    title: str = Field(..., max_length=200)  # Mandatory with a max length
    description: str = Field(default="")
    date: Annotated[date | None, Field(default=None)]
    google_book_id: str | None = Field(default=None, max_length=30)
    authors: list[str]  # A mandatory list of author names
    categories: list[str] | None = Field(default=None)
    image_src: str | None = Field(default=None)

    class Config:
        from_attributes = True

    @classmethod
    @model_validator(mode="before")
    def validate_authors_and_categories(cls, values):
        authors = values.get("authors")
        categories = values.get("categories")

        if (
            not authors
            or not isinstance(authors, list)
            or not all(isinstance(a, str) and a.strip() for a in authors)
        ):
            errmsg = "Authors must be a non-empty list of strings."
            raise ValueError(errmsg)

        if categories and (
            not isinstance(categories, list)
            or not all(isinstance(c, str) and c.strip() for c in categories)
        ):
            errmsg = "Categories must be a list of strings or None."
            raise ValueError(errmsg)

        return values
