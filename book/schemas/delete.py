from __future__ import annotations

from pydantic import BaseModel


class DeleteBooksResponse(BaseModel):
    message: str
    deleted_count: int
    deleted_books: list[int] | None = None
