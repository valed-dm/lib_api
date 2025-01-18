import logging

from fastapi import FastAPI
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from routes.admin.users import admin_router
from routes.auth.auth_token import user_token_router
from routes.auth.me import user_me_router
from routes.auth.register import user_register_router
from routes.author.all import author_router
from routes.books.create import create_book_router
from routes.books.delete import delete_books_router
from routes.books.delete_all import delete_all_books_router
from routes.books.get import get_books_router
from routes.books.patch import patch_book_router
from routes.library.all import library_router

app = FastAPI()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app.include_router(admin_router, tags=["Admin"])
app.include_router(user_register_router, tags=["Users"])
app.include_router(user_token_router, tags=["Users"])
app.include_router(user_me_router, tags=["Users"])
app.include_router(create_book_router, tags=["Books"])
app.include_router(get_books_router, tags=["Books"])
app.include_router(patch_book_router, tags=["Books"])
app.include_router(delete_books_router, tags=["Books"])
app.include_router(delete_all_books_router, tags=["Books"])
app.include_router(author_router, tags=["Authors"])
app.include_router(library_router, tags=["Library"])


@app.exception_handler(IntegrityError)
async def handle_integrity_error(request, exc: IntegrityError):
    err_msg = f"IntegrityError occurred: {exc}"
    logger.error(err_msg, exc_info=True)

    detail = "Integrity error occurred while processing the request."

    if "UNIQUE constraint failed" in str(exc.orig):
        detail = "Duplicate entry detected for a unique field."
    elif "FOREIGN KEY constraint failed" in str(exc.orig):
        detail = "A foreign key constraint failed."

    raise HTTPException(status_code=400, detail=detail)
