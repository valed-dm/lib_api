from __future__ import annotations

import datetime
import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Library
from db import Reader
from library.schemas import LendingData

load_dotenv()


DEFAULT_LIMIT = int(os.environ.get("DEFAULT_LIMIT", 10))
DEFAULT_LENDING_DURATION = int(os.environ.get("DEFAULT_LENDING_PERIOD", 14))


async def lend_books_to_user(
    db: AsyncSession,
    lending_data: list[LendingData],
) -> JSONResponse:
    """
    Process a list of lending transactions to lend books to readers.

    Args:
        db: The database session.
        lending_data: A list of dictionaries, each containing:
            - user_id: The ID of the user borrowing the book.
            - book_id: The ID of the book being borrowed.
            - lent_till: The time until lending is completed.

    Returns:
        A list of created `Reader` records.

    Raises:
        HTTPException: If any validation fails during the lending process.
    """
    lending_details = []

    async with db.begin():
        for item in lending_data:
            user_id = item.user_id
            book_id = item.book_id

            # Check user's book limit
            stmt = (
                select(func.count(Reader.id))
                .where(Reader.user_id == user_id)
                .where(Reader.lent_till >= func.current_date())
            )
            result = await db.execute(stmt)
            books_on_hand = result.scalar() or 0

            # Refuse if the user has reached their limit
            user_limit = DEFAULT_LIMIT
            if books_on_hand >= user_limit:
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": f"User {user_id} "
                        f"has reached the limit of {user_limit} books.",
                    },
                )

            # Check if the book is available in the library
            stmt = select(Library).where(Library.book_id == book_id)
            result = await db.execute(stmt)
            library_record = result.scalar_one_or_none()

            if not library_record or library_record.quantity_available <= 0:
                lending_details.append(
                    {
                        "user_id": user_id,
                        "book_id": book_id,
                        "status": "failure",
                        "message": f"Book {book_id} is not available in the library.",
                    },
                )
                continue

            # Check if the user has already borrowed the book
            stmt = select(Reader).where(
                Reader.user_id == user_id,
                Reader.book_id == book_id,
            )
            result = await db.execute(stmt)
            existing_reader_record = result.scalar_one_or_none()

            if existing_reader_record:
                lending_details.append(
                    {
                        "user_id": user_id,
                        "book_id": book_id,
                        "status": "failure",
                        "message": f"User {user_id} already borrowed book {book_id}.",
                    },
                )
                continue

            timezone_offset = 3.0
            tzinfo = datetime.timezone(timedelta(hours=timezone_offset))
            current_date = datetime.datetime.now(tz=tzinfo).date()

            # Process lending
            lent_till = (
                item.lent_till
                if item.lent_till
                else (current_date + timedelta(days=DEFAULT_LENDING_DURATION))
            )
            reader = Reader(
                user_id=user_id,
                book_id=book_id,
                lent_out=current_date,
                lent_till=lent_till,
            )
            db.add(reader)
            library_record.quantity_available -= 1

            lending_details.append(
                {
                    "user_id": user_id,
                    "book_id": book_id,
                    "status": "success",
                    "message": "Book lent successfully.",
                },
            )

    return JSONResponse(
        status_code=200,
        content={"details": lending_details},
    )
