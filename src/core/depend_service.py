from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, UserRole
from src.services.auth import AuthService, oauth2_scheme
from src.services.user import UserService


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Отримання екземпляру сервісу аутентифікації.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних

    Returns:
        AuthService: Екземпляр сервісу аутентифікації
    """
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)
):
    """
    Отримання поточного користувача з токену.

    Args:
        token (str): Токен доступу
        auth_service (AuthService): Сервіс аутентифікації

    Returns:
        User: Поточний користувач
    """
    return await auth_service.get_current_user(token)


def get_current_moderator_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Перевіряє, чи є поточний користувач адміністратором.

    Args:
        current_user (User): Поточний користувач

    Returns:
        User: Поточний користувач, якщо він є адміністратором

    Raises:
        HTTPException: Якщо користувач не є адміністратором
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки адміністратори можуть виконувати цю дію",
        )
    return current_user
