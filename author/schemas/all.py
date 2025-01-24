from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel
from pydantic import ConfigDict


class AuthorBase(BaseModel):
    name: str
    biography: str | None = ""
    years: str | None = ""


class AuthorCreate(AuthorBase):
    pass


class AuthorRead(AuthorBase):
    id: int
    books: list[str]

    Config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
