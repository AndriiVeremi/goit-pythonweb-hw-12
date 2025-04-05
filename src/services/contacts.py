from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repositories.contacts_repository import ContactRepository
from src.schemas.contact import (
    ContactSchema,
    ContactUpdateSchema,
)


class ContactService:
    """
    Сервіс для роботи з контактами.

    Забезпечує бізнес-логіку для операцій з контактами, включаючи створення,
    читання, оновлення, видалення та пошук контактів.
    """

    def __init__(self, db: AsyncSession):
        """
        Ініціалізація сервісу контактів.

        Args:
            db (AsyncSession): Асинхронна сесія бази даних
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactSchema, user: User):
        """
        Створення нового контакту.

        Args:
            body (ContactSchema): Схема даних нового контакту
            user (User): Користувач, який створює контакт

        Returns:
            Contact: Створений контакт
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, limit: int, offset: int, user: User):
        """
        Отримання списку контактів з пагінацією.

        Args:
            limit (int): Кількість контактів на сторінку
            offset (int): Зміщення від початку списку
            user (User): Користувач, чиї контакти потрібно отримати

        Returns:
            list[Contact]: Список контактів
        """
        return await self.contact_repository.get_contacts(limit, offset, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Отримання контакту за ідентифікатором.

        Args:
            contact_id (int): Ідентифікатор контакту
            user (User): Користувач, якому належить контакт

        Returns:
            Optional[Contact]: Знайдений контакт або None
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema, user: User):
        """
        Оновлення існуючого контакту.

        Args:
            contact_id (int): Ідентифікатор контакту
            body (ContactUpdateSchema): Схема даних для оновлення
            user (User): Користувач, якому належить контакт

        Returns:
            Optional[Contact]: Оновлений контакт або None
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Видалення контакту.

        Args:
            contact_id (int): Ідентифікатор контакту для видалення
            user (User): Користувач, якому належить контакт

        Returns:
            bool: True якщо контакт успішно видалено
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        user: User = None,
    ):
        """
        Пошук контактів за різними критеріями.

        Args:
            first_name (Optional[str]): Ім'я для пошуку
            last_name (Optional[str]): Прізвище для пошуку
            email (Optional[str]): Email для пошуку
            user (User): Користувач, чиї контакти потрібно знайти

        Returns:
            list[Contact]: Список знайдених контактів
        """
        return await self.contact_repository.search_contacts(first_name, last_name, email, user)

    async def get_upcoming_birthdays(self, days: int, user: User):
        """
        Отримання списку контактів з найближчими днями народження.

        Args:
            days (int): Кількість днів для перевірки
            user (User): Користувач, чиї контакти потрібно перевірити

        Returns:
            list[Contact]: Список контактів з найближчими днями народження
        """
        return await self.contact_repository.get_upcoming_birthdays(days, user)
