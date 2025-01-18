from __future__ import annotations

from datetime import date

from pydantic import BaseModel
from pydantic import Field


class LibraryCreate(BaseModel):
    book_id: int
    quantity_available: int


class LibraryRead(BaseModel):
    id: int
    book_id: int
    quantity_available: int

    class Config:
        from_attributes = True


class LendingData(BaseModel):
    user_id: int = Field(
        ...,
        title="User ID",
        description="The ID of the user borrowing the book",
    )
    book_id: int = Field(
        ...,
        title="Book ID",
        description="The ID of the book to be borrowed",
    )
    lent_till: date | None = Field(
        None,
        title="Lent Till",
        description="The date until which the book is lent "
        "(default: 14 days from the current date)",
    )


class LendingDataList(BaseModel):
    lending_data: list[LendingData] = Field(
        ...,
        title="Lending Data",
        description="A list of lending operations",
    )
