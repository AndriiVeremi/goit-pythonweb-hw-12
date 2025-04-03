import logging
from typing import Sequence, Optional, List, Any, Coroutine
from datetime import date, timedelta

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

logger = logging.getLogger("uvicorn.error")


class ContactRepository:
    """
    Репозиторій для роботи з контактами.

    Надає методи для CRUD операцій з контактами, а також додаткові методи
    для пошуку та фільтрації контактів.

    Args:
        session (AsyncSession): Асинхронна сесія для роботи з базою даних.
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, limit: int, offset: int, user: User
    ) -> Sequence[Contact]:
        """
        Отримує список контактів користувача з пагінацією.

        Args:
            limit (int): Максимальна кількість контактів для отримання.
            offset (int): Зміщення для пагінації.
            user (User): Користувач, чиї контакти потрібно отримати.

        Returns:
            Sequence[Contact]: Послідовність контактів користувача.
        """
        stmt = (
            select(Contact)
            .filter_by(user_id=user.id)
            .offset(offset)
            .limit(limit)
            .offset(offset)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Отримує контакт за ID та користувачем.

        Args:
            contact_id (int): ID контакту.
            user (User): Користувач, якому належить контакт.

        Returns:
            Contact | None: Знайдений контакт або None, якщо контакт не знайдено.
        """
        stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactSchema, user: User) -> Contact:
        """
        Створює новий контакт.

        Args:
            body (ContactSchema): Дані для створення контакту.
            user (User): Користувач, який створює контакт.

        Returns:
            Contact: Створений контакт.
        """
        contact = Contact(**body.model_dump(), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdateSchema, user: User
    ) -> Contact | None:
        """
        Оновлює існуючий контакт.

        Args:
            contact_id (int): ID контакту для оновлення.
            body (ContactUpdateSchema): Дані для оновлення контакту.
            user (User): Користувач, якому належить контакт.

        Returns:
            Contact | None: Оновлений контакт або None, якщо контакт не знайдено.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            update_data = body.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Видаляє контакт.

        Args:
            contact_id (int): ID контакту для видалення.
            user (User): Користувач, якому належить контакт.

        Returns:
            Contact | None: Видалений контакт або None, якщо контакт не знайдено.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Sequence[Contact]:
        """
        Пошук контактів за різними параметрами.

        Args:
            first_name (Optional[str]): Ім'я для пошуку.
            last_name (Optional[str]): Прізвище для пошуку.
            email (Optional[str]): Email для пошуку.

        Returns:
            Sequence[Contact]: Послідовність знайдених контактів.
        """
        stmt = select(Contact)

        if first_name:
            stmt = stmt.filter(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.filter(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.filter(Contact.email.ilike(f"%{email}%"))

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_upcoming_birthdays(self, days: int) -> list[Contact]:
        """
        Отримує список контактів, у яких день народження настане протягом вказаної кількості днів.

        Args:
            days (int): Кількість днів для перевірки майбутніх днів народження.

        Returns:
            list[Contact]: Список контактів з майбутніми днями народження.
        """
        today = date.today()
        end_date = today + timedelta(days=days)

        query = (
            select(Contact)
            .where(
                or_(
                    func.date_part("day", Contact.birthday).between(
                        func.date_part("day", today), func.date_part("day", end_date)
                    ),
                    and_(
                        func.date_part("day", end_date) < func.date_part("day", today),
                        or_(
                            func.date_part("day", Contact.birthday)
                            >= func.date_part("day", today),
                            func.date_part("day", Contact.birthday)
                            <= func.date_part("day", end_date),
                        ),
                    ),
                )
            )
            .order_by(func.date_part("day", Contact.birthday).asc())
        )

        result = await self.db.execute(query)
        return result.scalars().all()
