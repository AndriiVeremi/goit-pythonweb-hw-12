import logging
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import RefreshToken
from src.repositories.base import BaseRepository
from src.schemas.user import UserCreate

logger = logging.getLogger("uvicorn.error")


class RefreshTokenRepository(BaseRepository):
    """
    Репозиторій для роботи з токенами оновлення.

    Надає методи для створення, отримання та відкликання токенів оновлення.
    Успадковує базові CRUD операції від BaseRepository.

    Args:
        session (AsyncSession): Асинхронна сесія для роботи з базою даних.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshToken)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Отримує токен оновлення за його хешем.

        Args:
            token_hash (str): Хеш токена для пошуку.

        Returns:
            RefreshToken | None: Знайдений токен або None, якщо токен не знайдено.
        """
        stmt = select(self.model).where(RefreshToken.token_hash == token_hash)
        token = await self.db.execute(stmt)
        return token.scalars().first()

    async def get_active_token(
        self, token_hash: str, current_time: datetime
    ) -> RefreshToken | None:
        """
        Отримує активний токен оновлення за його хешем.

        Args:
            token_hash (str): Хеш токена для пошуку.
            current_time (datetime): Поточний час для перевірки терміну дії.

        Returns:
            RefreshToken | None: Знайдений активний токен або None.
        """
        stmt = select(self.model).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expired_at > current_time,
            RefreshToken.revoked_at.is_(None),
        )
        token = await self.db.execute(stmt)
        return token.scalars().first()

    async def save_token(
        self,
        user_id: int,
        token_hash: str,
        expired_at: datetime,
        ip_address: str,
        user_agent: str,
    ) -> RefreshToken:
        """
        Зберігає новий токен оновлення.

        Args:
            user_id (int): ID користувача.
            token_hash (str): Хеш токена.
            expired_at (datetime): Час закінчення терміну дії токена.
            ip_address (str): IP-адреса, з якої було створено токен.
            user_agent (str): User-Agent браузера, з якого було створено токен.

        Returns:
            RefreshToken: Створений токен оновлення.
        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expired_at=expired_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.create(refresh_token)

    async def revoke_token(self, refresh_token: RefreshToken) -> None:
        """
        Відкликає токен оновлення.

        Args:
            refresh_token (RefreshToken): Токен для відкликання.
        """
        refresh_token.revoked_at = datetime.now()
        await self.db.commit()
