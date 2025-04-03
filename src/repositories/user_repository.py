import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repositories.base import BaseRepository
from src.schemas.user import UserCreate

logger = logging.getLogger("uvicorn.error")


class UserRepository(BaseRepository):
    """
    Репозиторій для роботи з користувачами.

    Надає методи для CRUD операцій з користувачами, а також додаткові методи
    для роботи з профілем користувача та підтвердженням email.

    Args:
        session (AsyncSession): Асинхронна сесія для роботи з базою даних.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        """
        Отримує користувача за іменем користувача.

        Args:
            username (str): Ім'я користувача для пошуку.

        Returns:
            User | None: Знайдений користувач або None, якщо користувач не знайдений.
        """
        stmt = select(self.model).where(self.model.username == username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Отримує користувача за email.

        Args:
            email (str): Email користувача для пошуку.

        Returns:
            User | None: Знайдений користувач або None, якщо користувач не знайдений.
        """
        stmt = select(self.model).where(self.model.email == email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(
        self, user_data: UserCreate, hashed_password: str, avatar: str
    ) -> User:
        """
        Створює нового користувача.

        Args:
            user_data (UserCreate): Дані для створення користувача.
            hashed_password (str): Хешований пароль користувача.
            avatar (str): URL аватара користувача.

        Returns:
            User: Створений користувач.
        """
        user = User(
            **user_data.model_dump(exclude_unset=True, exclude={"password"}),
            hash_password=hashed_password,
            avatar=avatar,
        )
        return await self.create(user)

    async def confirmed_email(self, email: str) -> None:
        """
        Підтверджує email користувача.

        Args:
            email (str): Email користувача для підтвердження.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Оновлює URL аватара користувача.

        Args:
            email (str): Email користувача.
            url (str): Новий URL аватара.

        Returns:
            User: Оновлений користувач.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, user_id: int, hashed_password: str) -> None:
        """
        Оновлює пароль користувача.

        Args:
            user_id (int): ID користувача.
            hashed_password (str): Новий хешований пароль.
        """
        user = await self.db.get(self.model, user_id)
        if user:
            user.hash_password = hashed_password
            await self.db.commit()
