import os
import sys
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.entity.models import Base, User
from src.conf.config import settings

# Додаємо кореневу директорію проекту до PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Налаштовуємо політику циклу подій для Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Створюємо двигун для тестової бази даних
test_engine = create_async_engine(settings.test_database_url, echo=True, future=True)

# Створюємо фабрику сесій для тестів
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database and tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new session for each test."""
    async with TestingSessionLocal() as session:
        # Очищаємо базу даних перед кожним тестом
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture(scope="function")
async def test_user(session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hash_password="hashed_password",
        role="USER",
        confirmed=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
