from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets

import bcrypt
import hashlib
import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from libgravatar import Gravatar

from src.conf.config import settings
from src.entity.models import User, UserRole
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate
from src.services.redis_service import RedisService

redis_client = redis.from_url(settings.REDIS_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(self.db)
        self.refresh_token_repository = RefreshTokenRepository(self.db)
        self.redis_service = RedisService()

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password.decode()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    def _hash_token(self, token: str):
        return hashlib.sha256(token.encode()).hexdigest()

    async def authenticate(self, username: str, password: str) -> User:
        user = await self.user_repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Електронна адреса не підтверджена",
            )

        if not self._verify_password(password, user.hash_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        # Кешуємо дані користувача після успішної автентифікації
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "confirmed": user.confirmed,
            "avatar": user.avatar,
            "hash_password": user.hash_password,
            "role": user.role.value if isinstance(user.role, UserRole) else user.role,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        await self.redis_service.set_user_data(user.id, user_data)
        return user

    async def register_user(self, user_data: UserCreate) -> User:
        if await self.user_repository.get_by_username(user_data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        if await self.user_repository.get_user_by_email(str(user_data.email)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        avatar = None
        try:
            g = Gravatar(user_data.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        hashed_password = self._hash_password(user_data.password)
        user = await self.user_repository.create_user(user_data, hashed_password, avatar)
        return user

    def create_access_token(self, username: str) -> str:
        expires_delta = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # у секундах
        return serializer.dumps(
            {
                "sub": username,
                "exp": datetime.now(timezone.utc).timestamp() + expires_delta,
            }
        )

    async def create_refresh_token(
        self, user_id: int, ip_address: Optional[str], user_agent: Optional[str]
    ) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        expired_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_token_repository.save_token(
            user_id, token_hash, expired_at, ip_address, user_agent
        )
        return token

    def decode_and_validate_access_token(self, token: str) -> dict:
        try:
            payload = serializer.loads(token, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            return payload
        except SignatureExpired:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except BadSignature:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        if await redis_client.exists(f"bl:{token}"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

        payload = self.decode_and_validate_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        # Отримуємо користувача з бази даних
        user = await self.user_repository.get_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        # Перевіряємо кеш
        cached_user = await self.redis_service.get_user_data(user.id)
        if cached_user:
            return User(**cached_user)

        # Якщо даних немає в кеші, кешуємо їх
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "confirmed": user.confirmed,
            "avatar": user.avatar,
            "hash_password": user.hash_password,
            "role": user.role.value if isinstance(user.role, UserRole) else user.role,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

        await self.redis_service.set_user_data(user.id, user_data)
        return user

    async def validate_refresh_token(self, token: str) -> User:
        token_hash = self._hash_token(token)
        current_time = datetime.now(timezone.utc)
        refresh_token = await self.refresh_token_repository.get_active_token(
            token_hash, current_time
        )
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        user = await self.user_repository.get_by_id(refresh_token.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        return user

    async def revoke_refresh_token(self, token: str) -> None:
        token_hash = self._hash_token(token)
        refresh_token = await self.refresh_token_repository.get_by_token_hash(token_hash)
        if refresh_token and not refresh_token.revoked_at:
            await self.refresh_token_repository.revoke_token(refresh_token)

    async def revoke_access_token(self, token: str) -> None:
        payload = self.decode_and_validate_access_token(token)
        exp = payload.get("exp")
        if exp:
            await redis_client.setex(
                f"bl:{token}", int(exp - datetime.now(timezone.utc).timestamp()), "1"
            )
            # Видаляємо дані користувача з кешу при виході
            username = payload.get("sub")
            if username:
                user = await self.user_repository.get_by_username(username)
                if user:
                    await self.redis_service.delete_user_data(user.id)
