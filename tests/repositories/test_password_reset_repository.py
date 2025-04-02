import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import PasswordResetToken, User
from src.repositories.password_reset_repository import PasswordResetRepository
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate


@pytest.fixture
def password_reset_repository(session: AsyncSession):
    return PasswordResetRepository(session)


@pytest.fixture
async def test_user(session: AsyncSession):
    user_repository = UserRepository(session)
    user_data = {
        "username": "reset_test_user",
        "email": "reset_test@example.com",
        "password": "test123456",
    }
    user = await user_repository.create_user(
        UserCreate(**user_data), "hashed_password", "avatar.jpg"
    )
    return user


@pytest.fixture
def test_token_data(test_user):
    return {
        "user_id": test_user.id,
        "expires_at": datetime.utcnow() + timedelta(hours=1),
    }


@pytest.mark.asyncio
async def test_save_token(
    password_reset_repository: PasswordResetRepository, test_token_data: dict
):
    token = await password_reset_repository.save_token(
        user_id=test_token_data["user_id"], expires_at=test_token_data["expires_at"]
    )
    assert token is not None
    assert isinstance(token, str)
    # Перевіряємо, що токен збережений в базі даних
    saved_token = await password_reset_repository.get_token(token)
    assert saved_token is not None
    assert saved_token.user_id == test_token_data["user_id"]
    assert saved_token.expires_at == test_token_data["expires_at"]
    assert not saved_token.used


@pytest.mark.asyncio
async def test_get_token(
    password_reset_repository: PasswordResetRepository, test_token_data: dict
):
    # Спочатку створюємо токен
    token = await password_reset_repository.save_token(
        user_id=test_token_data["user_id"], expires_at=test_token_data["expires_at"]
    )
    # Потім отримуємо його
    found_token = await password_reset_repository.get_token(token)
    assert found_token is not None
    assert found_token.token == token
    assert found_token.user_id == test_token_data["user_id"]


@pytest.mark.asyncio
async def test_mark_token_as_used(
    password_reset_repository: PasswordResetRepository, test_token_data: dict
):
    # Спочатку створюємо токен
    token = await password_reset_repository.save_token(
        user_id=test_token_data["user_id"], expires_at=test_token_data["expires_at"]
    )
    # Позначаємо токен як використаний
    await password_reset_repository.mark_token_as_used(token)
    # Перевіряємо, що токен позначений як використаний
    found_token = await password_reset_repository.get_token(token)
    assert found_token.used is True


@pytest.mark.asyncio
async def test_delete_expired_tokens(
    password_reset_repository: PasswordResetRepository, test_user
):
    # Створюємо кілька токенів з різними термінами дії
    expired_token = await password_reset_repository.save_token(
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    valid_token = await password_reset_repository.save_token(
        user_id=test_user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )

    # Видаляємо прострочені токени
    await password_reset_repository.delete_expired_tokens()

    # Перевіряємо, що прострочений токен видалений, а валідний залишився
    deleted_token = await password_reset_repository.get_token(expired_token)
    assert deleted_token is None

    valid_token = await password_reset_repository.get_token(valid_token)
    assert valid_token is not None
