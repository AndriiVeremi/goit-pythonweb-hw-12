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
    def __init__(self, db: AsyncSession):
        self.db = db
        self.password_reset_repository = PasswordResetRepository(db)
        self.user_repository = UserRepository(db)
        self.auth_service = AuthService(db)

    async def request_password_reset(self, email: str) -> None:
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
