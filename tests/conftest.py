import os

import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from auth.auth import get_password_hash
from db import Base
from db import User
from main import app

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
dbname = "test_db"

STATUS_OK = 200
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
TEST_DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}/{dbname}"


@pytest.fixture
async def async_client():
    """Fixture for testing HTTP endpoints with AsyncClient."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as client:
        yield client


@pytest.fixture
async def test_user(db_session):
    """Creates a test user."""
    hashed_password = get_password_hash(TEST_PASSWORD)
    user_obj = User(
        username="test_user",
        email="test_user@example.com",
        hashed_password=hashed_password,
        full_name="Test User",
        scopes="me read superuser",
    )
    db_session.add(user_obj)
    await db_session.commit()
    await db_session.refresh(user_obj)
    return user_obj.username, TEST_PASSWORD


@pytest.fixture
async def db_session():
    """Fixture to provide a test database session."""

    # Create an async engine for the test database
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Configure Alembic migrations with the test DB
    alembic_cfg = Config(file_="alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)

    # Apply migrations
    command.upgrade(alembic_cfg, "head")

    # Create a new session factory
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    # Cleanup tables if needed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Yield the session to the test
    async with session_factory() as session:
        yield session
        await session.rollback()

    # Dispose the engine after tests
    await engine.dispose()
