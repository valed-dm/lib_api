from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class BookSearchSchema(BaseModel):
    title: str | None = Field(
        None,
        max_length=200,
        description="Filter by book title.",
    )
    author: str | None = Field(
        None,
        max_length=100,
        description="Filter by author name.",
    )
    category: str | None = Field(
        None,
        max_length=100,
        description="Filter by category name.",
    )
    sort_by: Literal["date", "title"] = Field(
        "date",
        description="Sort by field ('date' or 'title').",
    )
    order: Literal["asc", "desc"] = Field(
        "desc",
        description="Order of sorting ('asc' or 'desc').",
    )
    limit: int = Field(
        10,
        gt=0,
        le=100,
        description="Number of results to return (max: 100).",
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of results to skip for pagination.",
    )
