from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User
from src.repositories.password_reset_repository import PasswordResetRepository
from src.services.email import send_password_reset_email
from src.repositories.user_repository import UserRepository
from src.services.auth import AuthService

class PasswordResetService:
    """
    Сервіс для управління процесом скидання пароля користувача.

    Attributes:
        db (AsyncSession): Асинхронна сесія бази даних
        password_reset_repository (PasswordResetRepository): Репозиторій для роботи з токенами скидання пароля
        user_repository (UserRepository): Репозиторій для роботи з користувачами
        auth_service (AuthService): Сервіс аутентифікації
    """

    def __init__(self, db: AsyncSession):
        """
        Ініціалізація сервісу скидання пароля.

        Args:
            db (AsyncSession): Асинхронна сесія бази даних
        """
        self.db = db
        self.password_reset_repository = PasswordResetRepository(db)
        self.user_repository = UserRepository(db)
        self.auth_service = AuthService(db)

    async def request_password_reset(self, email: str) -> None:
        """
        Запит на скидання пароля.

        Args:
            email (str): Email користувача

        Note:
            Якщо користувач з вказаним email існує, йому буде відправлено
            лист з токеном для скидання пароля.
        """
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return

        # Зберігаємо email перед закриттям сесії
        user_email = user.email

        # Створюємо токен скидання пароля
        reset_token = await self.password_reset_repository.save_token(
            user_id=user.id, expires_at=datetime.utcnow() + timedelta(minutes=30)
        )

        # Відправляємо email з токеном
        await send_password_reset_email(user_email, reset_token)

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        """
        Підтвердження скидання пароля та встановлення нового.

        Args:
            token (str): Токен скидання пароля
            new_password (str): Новий пароль

        Raises:
            HTTPException: При невалідному, простроченому або вже використаному токені
        """
        reset_token = await self.password_reset_repository.get_token(token)
        if not reset_token:
            raise HTTPException(
                status_code=400, detail="Недійсний або прострочений токен"
            )

        if reset_token.used:
            raise HTTPException(status_code=400, detail="Токен вже був використаний")

        if reset_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Токен прострочений")

        # Хешуємо новий пароль перед збереженням
        hashed_password = self.auth_service._hash_password(new_password)
        
        # Оновлюємо пароль користувача
        await self.user_repository.update_password(reset_token.user_id, hashed_password)

        # Позначаємо токен як використаний
        await self.password_reset_repository.mark_token_as_used(token)
