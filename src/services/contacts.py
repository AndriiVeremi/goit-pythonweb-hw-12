from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.contacts_repository import ContactRepository
from src.schemas.contact import (
    ContactSchema,
    ContactUpdateSchema,
)


class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactSchema):
        return await self.contact_repository.create_contact(body)

    async def get_contacts(self, limit: int, offset: int):
        return await self.contact_repository.get_contacts(limit, offset)

    async def get_contact(self, contact_id: int):
        return await self.contact_repository.get_contact_by_id(contact_id)

    async def update_contact(self, contact_id: int, body: ContactUpdateSchema):
        return await self.contact_repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        return await self.contact_repository.remove_contact(contact_id)

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
