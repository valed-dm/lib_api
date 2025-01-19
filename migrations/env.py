import contextlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection
from sqlalchemy import MetaData
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from db.associations import BookAuthorAssociation
from db.associations import BookCategoryAssociation
from db.authors import Author
from db.books import Book
from db.categories import Category
from db.images import Image
from db.library import Library
from db.readers import Reader
from db.users import User

# Get alembic config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Create a temporary metadata object for the authors table
target_metadata = MetaData()
User.metadata.tables["users"].to_metadata(target_metadata)
Author.metadata.tables["authors"].to_metadata(target_metadata)
Category.metadata.tables["categories"].to_metadata(target_metadata)
Book.metadata.tables["books"].to_metadata(target_metadata)
Image.metadata.tables["images"].to_metadata(target_metadata)
BookAuthorAssociation.metadata.tables["book_author"].to_metadata(target_metadata)
BookCategoryAssociation.metadata.tables["book_category"].to_metadata(target_metadata)
Library.metadata.tables["libraries"].to_metadata(target_metadata)
Reader.metadata.tables["readers"].to_metadata(target_metadata)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def do_migrations(conn: Connection):
        """Configure the context and run migrations."""
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    async with connectable.connect() as connection:
        await connection.run_sync(do_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    try:
        # Check if we are in a running event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, safe to use `asyncio.run`
        asyncio.run(run_migrations_online())
    else:
        # Already in a running loop
        with contextlib.suppress(RuntimeError):
            asyncio.get_running_loop().run_until_complete(run_migrations_online())
