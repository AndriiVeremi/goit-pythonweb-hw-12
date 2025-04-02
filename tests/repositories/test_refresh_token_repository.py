import pytest
from datetime import datetime, timedelta
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import RefreshToken, User
from src.repositories.refresh_token_repository import RefreshTokenRepository


@pytest.fixture
def test_user_data() -> dict:
    return {
        "username": "testuser",
        "email": "test@example.com",
        "hash_password": "hashed_password",
        "role": "USER",
        "confirmed": True,
    }


@pytest.fixture
async def test_user(test_user_data: dict, session: AsyncSession) -> User:
    user = User(**test_user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def test_token_data(test_user: User) -> dict:
    return {
        "user_id": test_user.id,
        "token_hash": "test_token_hash",
        "expired_at": datetime.now() + timedelta(days=7),
        "ip_address": "127.0.0.1",
        "user_agent": "test_user_agent",
    }


@pytest.fixture
async def test_token(test_token_data: dict, session: AsyncSession) -> RefreshToken:
    token = RefreshToken(**test_token_data)
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token


@pytest.fixture
async def refresh_token_repository(
    session: AsyncSession,
) -> AsyncGenerator[RefreshTokenRepository, None]:
    yield RefreshTokenRepository(session)


@pytest.mark.asyncio
async def test_get_by_token_hash(
    refresh_token_repository: RefreshTokenRepository, test_token: RefreshToken
):
    result = await refresh_token_repository.get_by_token_hash(test_token.token_hash)
    assert result is not None
    assert result.id == test_token.id
    assert result.token_hash == test_token.token_hash


@pytest.mark.asyncio
async def test_get_active_token(
    refresh_token_repository: RefreshTokenRepository, test_token: RefreshToken
):
    current_time = datetime.now()
    result = await refresh_token_repository.get_active_token(
        test_token.token_hash, current_time
    )
    assert result is not None
    assert result.id == test_token.id
    assert result.token_hash == test_token.token_hash


@pytest.mark.asyncio
async def test_get_active_token_expired(
    refresh_token_repository: RefreshTokenRepository, test_token: RefreshToken
):
    # Встановлюємо час закінчення в минулому
    test_token.expired_at = datetime.now() - timedelta(days=1)
    await refresh_token_repository.db.commit()

    current_time = datetime.now()
    result = await refresh_token_repository.get_active_token(
        test_token.token_hash, current_time
    )
    assert result is None


@pytest.mark.asyncio
async def test_get_active_token_revoked(
    refresh_token_repository: RefreshTokenRepository, test_token: RefreshToken
):
    # Встановлюємо час відкликання
    test_token.revoked_at = datetime.now()
    await refresh_token_repository.db.commit()

    current_time = datetime.now()
    result = await refresh_token_repository.get_active_token(
        test_token.token_hash, current_time
    )
    assert result is None


@pytest.mark.asyncio
async def test_save_token(
    refresh_token_repository: RefreshTokenRepository, test_token_data: dict
):
    result = await refresh_token_repository.save_token(**test_token_data)
    assert result is not None
    assert result.user_id == test_token_data["user_id"]
    assert result.token_hash == test_token_data["token_hash"]
    assert result.ip_address == test_token_data["ip_address"]
    assert result.user_agent == test_token_data["user_agent"]


@pytest.mark.asyncio
async def test_revoke_token(
    refresh_token_repository: RefreshTokenRepository, test_token: RefreshToken
):
    await refresh_token_repository.revoke_token(test_token)

    # Перевіряємо, що токен відкликаний
    result = await refresh_token_repository.get_by_token_hash(test_token.token_hash)
    assert result is not None
    assert result.revoked_at is not None
