from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repositories.contacts_repository import ContactRepository
from src.schemas.contact import (
    ContactSchema,
    ContactUpdateSchema,
)


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactSchema, user: User):
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, limit: int, offset: int, user: User):
        return await self.contact_repository.get_contacts(limit, offset, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema, user: User):
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ):
        return await self.contact_repository.search_contacts(
            first_name, last_name, email
        )

    async def get_upcoming_birthdays(self, days: int):
        return await self.contact_repository.get_upcoming_birthdays(days)
