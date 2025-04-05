import json
from typing import Optional
import redis.asyncio as redis
from src.conf.config import settings

redis_client = redis.from_url(settings.REDIS_URL)


class RedisService:
    @staticmethod
    async def set_user_data(user_id: int, user_data: dict, expire_time: int = 3600) -> None:
        """
        Зберігає дані користувача в Redis

        Args:
            user_id: ID користувача
            user_data: Дані користувача для кешування
            expire_time: Час життя кешу в секундах (за замовчуванням 1 година)
        """
        key = f"user:{user_id}"
        await redis_client.setex(key, expire_time, json.dumps(user_data))

    @staticmethod
    async def get_user_data(user_id: int) -> Optional[dict]:
        """
        Отримує дані користувача з Redis

        Args:
            user_id: ID користувача

        Returns:
            dict: Дані користувача або None, якщо дані не знайдено
        """
        key = f"user:{user_id}"
        data = await redis_client.get(key)
        return json.loads(data) if data else None

    @staticmethod
    async def delete_user_data(user_id: int) -> None:
        """
        Видаляє дані користувача з Redis

        Args:
            user_id: ID користувача
        """
        key = f"user:{user_id}"
        await redis_client.delete(key)
