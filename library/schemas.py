from pydantic import BaseModel


class LibraryCreate(BaseModel):
    book_id: int
    quantity_available: int


class LibraryRead(BaseModel):
    id: int
    book_id: int
    quantity_available: int

    class Config:
        from_attributes = True
