from typing import TypeVar, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository:
    """
    Базовий репозиторій, який надає загальні CRUD операції для всіх моделей.

    Args:
        session (AsyncSession): Асинхронна сесія для роботи з базою даних.
        model (Type[ModelType]): Клас моделі, з якою працює репозиторій.
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.db = session
        self.model: Type[ModelType] = model

    async def get_all(self) -> list[ModelType]:
        """
        Отримує всі записи з бази даних.

        Returns:
            list[ModelType]: Список всіх записів моделі.
        """
        stmt = select(self.model)
        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())

    async def get_by_id(self, _id: int) -> ModelType | None:
        """
        Отримує запис за його ID.

        Args:
            _id (int): ID запису, який потрібно отримати.

        Returns:
            ModelType | None: Знайдений запис або None, якщо запис не знайдено.
        """
        stmt = select(self.model).filter_by(id=_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create(self, instance: ModelType) -> ModelType:
        """
        Створює новий запис у базі даних.

        Args:
            instance (ModelType): Екземпляр моделі для створення.

        Returns:
            ModelType: Створений запис з оновленими даними.
        """
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelType) -> ModelType:
        """
        Оновлює існуючий запис у базі даних.

        Args:
            instance (ModelType): Екземпляр моделі для оновлення.

        Returns:
            ModelType: Оновлений запис.
        """
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """
        Видаляє запис з бази даних.

        Args:
            instance (ModelType): Екземпляр моделі для видалення.
        """
        await self.db.delete(instance)
        await self.db.commit()
