from datetime import datetime
import secrets
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.entity.models import PasswordResetToken


class PasswordResetRepository(BaseRepository):
    """
    Репозиторій для роботи з токенами скидання пароля.

    Надає методи для створення, отримання та управління токенами скидання пароля.
    Успадковує базові CRUD операції від BaseRepository.

    Args:
        session (AsyncSession): Асинхронна сесія для роботи з базою даних.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PasswordResetToken)

    async def save_token(self, user_id: int, expires_at: datetime) -> str:
        """
        Створює та зберігає новий токен для скидання пароля.

        Args:
            user_id (int): ID користувача.
            expires_at (datetime): Час закінчення терміну дії токена.

        Returns:
            str: Згенерований токен.
        """
        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            used=False,
            created_at=datetime.utcnow(),
        )
        await self.create(reset_token)
        return token

    async def get_token(self, token: str) -> PasswordResetToken | None:
        """
        Отримує токен скидання пароля за його значенням.

        Args:
            token (str): Значення токена для пошуку.

        Returns:
            PasswordResetToken | None: Знайдений токен або None, якщо токен не знайдено.
        """
        stmt = select(self.model).where(self.model.token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_token_as_used(self, token: str) -> None:
        """
        Позначає токен як використаний.

        Args:
            token (str): Значення токена для позначення.
        """
        stmt = select(self.model).where(self.model.token == token)
        result = await self.db.execute(stmt)
        reset_token = result.scalar_one_or_none()
        if reset_token:
            reset_token.used = True
            await self.db.commit()

    async def delete_expired_tokens(self) -> None:
        """
        Видаляє всі прострочені токени скидання пароля.
        """
        stmt = delete(self.model).where(self.model.expires_at < datetime.utcnow())
        await self.db.execute(stmt)
        await self.db.commit()
