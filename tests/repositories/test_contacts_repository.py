import pytest
from datetime import date, timedelta
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.repositories.contacts_repository import ContactRepository
from src.schemas.contact import ContactSchema, ContactUpdateSchema


@pytest.fixture
def test_contact_data() -> dict:
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "birthday": date(1990, 1, 1),
        "extra_info": "Test contact",
    }


@pytest.fixture
async def test_contact(
    test_user: User, test_contact_data: dict, session: AsyncSession
) -> Contact:
    contact = Contact(**test_contact_data, user_id=test_user.id)
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact


@pytest.fixture
async def contact_repository(
    session: AsyncSession,
) -> AsyncGenerator[ContactRepository, None]:
    yield ContactRepository(session)


@pytest.mark.asyncio
async def test_get_contacts(
    contact_repository: ContactRepository, test_user: User, test_contact: Contact
):
    contacts = await contact_repository.get_contacts(limit=10, offset=0, user=test_user)
    assert len(contacts) == 1
    assert contacts[0].id == test_contact.id


@pytest.mark.asyncio
async def test_get_contact_by_id(
    contact_repository: ContactRepository, test_user: User, test_contact: Contact
):
    contact = await contact_repository.get_contact_by_id(
        contact_id=test_contact.id, user=test_user
    )
    assert contact is not None
    assert contact.id == test_contact.id
    assert contact.first_name == test_contact.first_name
    assert contact.last_name == test_contact.last_name
    assert contact.email == test_contact.email


@pytest.mark.asyncio
async def test_create_contact(
    contact_repository: ContactRepository, test_user: User, test_contact_data: dict
):
    contact_schema = ContactSchema(**test_contact_data)
    contact = await contact_repository.create_contact(
        body=contact_schema, user=test_user
    )
    assert contact is not None
    assert contact.first_name == test_contact_data["first_name"]
    assert contact.last_name == test_contact_data["last_name"]
    assert contact.email == test_contact_data["email"]
    assert contact.user_id == test_user.id


@pytest.mark.asyncio
async def test_update_contact(
    contact_repository: ContactRepository, test_user: User, test_contact: Contact
):
    update_data = ContactUpdateSchema(first_name="Jane", last_name="Smith")
    updated_contact = await contact_repository.update_contact(
        contact_id=test_contact.id, body=update_data, user=test_user
    )
    assert updated_contact is not None
    assert updated_contact.first_name == "Jane"
    assert updated_contact.last_name == "Smith"
    assert updated_contact.email == test_contact.email  # Не змінилося


@pytest.mark.asyncio
async def test_remove_contact(
    contact_repository: ContactRepository, test_user: User, test_contact: Contact
):
    removed_contact = await contact_repository.remove_contact(
        contact_id=test_contact.id, user=test_user
    )
    assert removed_contact is not None
    assert removed_contact.id == test_contact.id

    # Перевіряємо, що контакт дійсно видалений
    contact = await contact_repository.get_contact_by_id(
        contact_id=test_contact.id, user=test_user
    )
    assert contact is None


@pytest.mark.asyncio
async def test_search_contacts(
    contact_repository: ContactRepository, test_contact: Contact
):
    # Пошук за ім'ям
    contacts = await contact_repository.search_contacts(first_name="John")
    assert len(contacts) == 1
    assert contacts[0].id == test_contact.id

    # Пошук за прізвищем
    contacts = await contact_repository.search_contacts(last_name="Doe")
    assert len(contacts) == 1
    assert contacts[0].id == test_contact.id

    # Пошук за email
    contacts = await contact_repository.search_contacts(email="john@example.com")
    assert len(contacts) == 1
    assert contacts[0].id == test_contact.id

    # Пошук з неправильними даними
    contacts = await contact_repository.search_contacts(first_name="NonExistent")
    assert len(contacts) == 0


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(
    contact_repository: ContactRepository, test_contact: Contact
):
    # Встановлюємо дату народження на завтра
    tomorrow = date.today() + timedelta(days=1)
    test_contact.birthday = tomorrow
    await contact_repository.db.commit()

    # Отримуємо контакти з днями народження протягом наступних 7 днів
    contacts = await contact_repository.get_upcoming_birthdays(days=7)
    assert len(contacts) == 1
    assert contacts[0].id == test_contact.id
