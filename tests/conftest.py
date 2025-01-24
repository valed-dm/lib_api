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
from db.utils import get_db
from main import app

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
TEST_DB_NAME = os.getenv("TEST_DB_NAME")

TEST_USERNAME = os.getenv("TEST_USERNAME")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")
TEST_EMAIL = os.getenv("TEST_EMAIL")
TEST_FULL_NAME = os.getenv("TEST_FULL_NAME")
TEST_SCOPES = os.getenv("TEST_SCOPES")


TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{TEST_DB_NAME}"
)

STATUS_OK = 200


@pytest.fixture
async def async_client():
    """Fixture for testing HTTP endpoints with AsyncClient."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as client:
        yield client


@pytest.fixture
async def test_user(test_db_session):
    """Creates a test user."""
    user = User(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        hashed_password=get_password_hash(TEST_PASSWORD),
        full_name=TEST_FULL_NAME,
        scopes=TEST_SCOPES,
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user.username, TEST_PASSWORD


@pytest.fixture
async def test_db_session():
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


@pytest.fixture
def override_get_db(test_db_session):
    async def _override_get_db():
        yield test_db_session

    return _override_get_db


@pytest.fixture
def _override_dependencies(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
