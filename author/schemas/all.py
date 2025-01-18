from __future__ import annotations

from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str
    biography: str | None = ""
    years: str | None = ""


class AuthorCreate(AuthorBase):
    pass


class AuthorRead(AuthorBase):
    id: int
    books: list[str]

    class Config:
        from_attributes = True
