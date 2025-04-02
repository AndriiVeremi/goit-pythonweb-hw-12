import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate


@pytest.fixture
def user_repository(session: AsyncSession):
    return UserRepository(session)


@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123456",
    }


@pytest.mark.asyncio
async def test_get_by_username(user_repository: UserRepository, test_user_data: dict):
    # Спочатку створюємо користувача
    user = await user_repository.create_user(
        UserCreate(**test_user_data), "hashed_password", "avatar.jpg"
    )
    # Потім отримуємо його за username
    found_user = await user_repository.get_by_username(test_user_data["username"])
    assert found_user is not None
    assert found_user.username == test_user_data["username"]


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository: UserRepository, test_user_data: dict):
    # Спочатку створюємо користувача
    user = await user_repository.create_user(
        UserCreate(**test_user_data), "hashed_password", "avatar.jpg"
    )
    # Потім отримуємо його за email
    found_user = await user_repository.get_user_by_email(test_user_data["email"])
    assert found_user is not None
    assert found_user.email == test_user_data["email"]


@pytest.mark.asyncio
async def test_create_user(user_repository: UserRepository, test_user_data: dict):
    user = await user_repository.create_user(
        UserCreate(**test_user_data), "hashed_password", "avatar.jpg"
    )
    assert user.username == test_user_data["username"]
    assert user.email == test_user_data["email"]
    assert user.hash_password == "hashed_password"
    assert user.avatar == "avatar.jpg"
    assert user.role == "USER"
    assert not user.confirmed


@pytest.mark.asyncio
async def test_confirmed_email(user_repository: UserRepository, test_user_data: dict):
    # Спочатку створюємо користувача
    user = await user_repository.create_user(
        UserCreate(**test_user_data), "hashed_password", "avatar.jpg"
    )
    # Підтверджуємо email
    await user_repository.confirmed_email(test_user_data["email"])
    # Перевіряємо, що email підтверджено
    found_user = await user_repository.get_user_by_email(test_user_data["email"])
    assert found_user.confirmed is True


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository: UserRepository, test_user_data: dict):
    # Спочатку створюємо користувача
    user = await user_repository.create_user(
        UserCreate(**test_user_data), "hashed_password", "avatar.jpg"
    )
    # Оновлюємо URL аватара
    new_avatar_url = "new_avatar.jpg"
    updated_user = await user_repository.update_avatar_url(
        test_user_data["email"], new_avatar_url
    )
    assert updated_user.avatar == new_avatar_url


@pytest.mark.asyncio
async def test_update_password(user_repository: UserRepository, test_user_data: dict):
    # Спочатку створюємо користувача
    user = await user_repository.create_user(
        UserCreate(**test_user_data), "hashed_password", "avatar.jpg"
    )
    # Оновлюємо пароль
    new_hashed_password = "new_hashed_password"
    await user_repository.update_password(user.id, new_hashed_password)
    # Перевіряємо, що пароль оновлено
    found_user = await user_repository.get_user_by_email(test_user_data["email"])
    assert found_user.hash_password == new_hashed_password
