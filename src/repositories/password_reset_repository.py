from datetime import datetime
import secrets
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.entity.models import PasswordResetToken


class PasswordResetRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PasswordResetToken)

    async def save_token(self, user_id: int, expires_at: datetime) -> str:
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
        stmt = select(self.model).where(self.model.token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_token_as_used(self, token: str) -> None:
        stmt = select(self.model).where(self.model.token == token)
        result = await self.db.execute(stmt)
        reset_token = result.scalar_one_or_none()
        if reset_token:
            reset_token.used = True
            await self.db.commit()

    async def delete_expired_tokens(self) -> None:
        stmt = delete(self.model).where(self.model.expires_at < datetime.utcnow())
        await self.db.execute(stmt)
        await self.db.commit()
