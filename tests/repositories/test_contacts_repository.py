# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession
# from unittest.mock import AsyncMock, Mock
#
# from src.entity.models import Contact, User
# from src.repositories.contacts_repository import ContactRepository
# from src.schemas.contact import ContactSchema, ContactUpdateSchema
#
# @pytest.fixture
# def mock_session():
#     session = AsyncMock(spec=AsyncSession)
#     # session.execute = AsyncMock()
#     # session.commit = AsyncMock()
#     # session.refresh = AsyncMock()
#     # session.add = Mock()
#     # session.delete = AsyncMock()
#     return session
#
# @pytest.fixture
# def mock_user():
#     return User(id=1, username="test_user")
#
# @pytest.fixture
# def contacts_repository(mock_session):
#     return ContactRepository(mock_session)
#
# @pytest.mark.asyncio
# async def test_get_contacts(contacts_repository, mock_session, mock_user):
#     # Arrange
#     limit = 10
#     offset = 0
#     mock_contacts = [Contact(id=1, title="Test Contact"), Contact(id=2, title="Another Contact")]
#     mock_result = Mock()
#     mock_result.scalars.return_value.all.return_value = mock_contacts
#     mock_session.execute.return_value = mock_result
#
#     # Act
#     result = await contacts_repository.get_contacts(limit, offset, mock_user)
#
#     # Assert
#     assert result == mock_contacts
#     mock_session.execute.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_get_contact_by_id(contacts_repository, mock_session, mock_user):
#     # Arrange
#     contact_id = 1
#     mock_contact = Contact(id=contact_id, title="Test Contact")
#     mock_result = Mock()
#     mock_result.scalar_one_or_none.return_value = mock_contact
#     mock_session.execute.return_value = mock_result
#
#     # Act
#     result = await contacts_repository.get_contact_by_id(contact_id, mock_user)
#
#     # Assert
#     assert result == mock_contact
#     mock_session.execute.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_create_contact(contacts_repository, mock_session, mock_user):
#     # Arrange
#     contact_data = ContactSchema(title="New Contact", description="Test Description")
#     mock_contact = Contact(
#         id=1,
#         title=contact_data.title,
#         description=contact_data.description,
#         user_id=mock_user.id
#     )
#
#     async def mock_refresh(contact):
#         return mock_contact
#
#
#     mock_session.refresh.side_effect = mock_refresh
#
#
#     # Act
#     result = await contacts_repository.create_contact(contact_data, mock_user)
#
#     # Assert
#     assert result.title == mock_contact.title
#     assert result.description == mock_contact.description
#     assert result.user_id == mock_contact.user_id
#     mock_session.add.assert_called_once()
#     mock_session.commit.assert_called_once()
#     mock_session.refresh.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_remove_contact(contacts_repository, mock_session, mock_user):
#     # Arrange
#     contact_id = 1
#     mock_contact = Contact(id=contact_id, title="Test Contact")
#     mock_result = Mock()
#     mock_result.scalar_one_or_none.return_value = mock_contact
#     mock_session.execute.return_value = mock_result
#
#     # Act
#     result = await contacts_repository().remove_contact(contact_id, mock_user)
#
#     # Assert
#     assert result == mock_contact
#     mock_session.delete.assert_called_once_with(mock_contact)
#     mock_session.commit.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_update_contact(contacts_repository, mock_session, mock_user):
#     # Arrange
#     contact_id = 1
#     update_data = ContactUpdateSchema(title="Updated Contact")
#     mock_contact = Contact(id=contact_id, title="Old Title")
#     mock_result = Mock()
#     mock_result.scalar_one_or_none.return_value = mock_contact
#     mock_session.execute.return_value = mock_result
#     mock_session.refresh.return_value = mock_contact
#
#     # Act
#     result = await contacts_repository.update_contact(contact_id, update_data, mock_user)
#
#     # Assert
#     assert result.title == "Updated Contact"
#     mock_session.commit.assert_called_once()
#     mock_session.refresh.assert_called_once()
#


import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, Mock
import datetime

from src.entity.models import Contact, User
from src.repositories.contacts_repository import ContactRepository
from src.schemas.contact import ContactSchema, ContactUpdateSchema

@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture
def mock_user():
    return User(id=1, username="test_user")

@pytest.fixture
def contacts_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.mark.asyncio
async def test_get_contacts(contacts_repository, mock_session, mock_user):
    limit = 10
    offset = 0
    mock_contacts = [
        Contact(id=1, first_name="Test", last_name="Contact", email="test@example.com", phone="1234567890", birthday=datetime.date(1990, 1, 1), extra_info="Info"),
        Contact(id=2, first_name="Another", last_name="Contact", email="another@example.com", phone="0987654321", birthday=datetime.date(1991, 2, 2), extra_info="Info")
    ]
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_contacts
    mock_session.execute.return_value = mock_result

    result = await contacts_repository.get_contacts(limit, offset, mock_user)

    assert result == mock_contacts
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_contact_by_id(contacts_repository, mock_session, mock_user):
    contact_id = 1
    mock_contact = Contact(id=contact_id, first_name="Test", last_name="Contact", email="test@example.com", phone="1234567890", birthday=datetime.date(1990, 1, 1), extra_info="Info")
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_session.execute.return_value = mock_result

    result = await contacts_repository.get_contact_by_id(contact_id, mock_user)

    assert result == mock_contact
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_contact(contacts_repository, mock_session, mock_user):
    contact_data = ContactSchema(
        first_name="New",
        last_name="Contact",
        email="new@example.com",
        phone="1234567890",
        birthday=datetime.date(1990, 1, 1),
        extra_info="Test Description"
    )
    mock_contact = Contact(
        id=1,
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        email=contact_data.email,
        phone=contact_data.phone,
        birthday=contact_data.birthday,
        extra_info=contact_data.extra_info,
        user_id=mock_user.id
    )

    async def mock_refresh(contact):
        return mock_contact

    mock_session.refresh.side_effect = mock_refresh

    result = await contacts_repository.create_contact(contact_data, mock_user)

    assert result.first_name == mock_contact.first_name
    assert result.last_name == mock_contact.last_name
    assert result.email == mock_contact.email
    assert result.phone == mock_contact.phone
    assert result.birthday == mock_contact.birthday
    assert result.extra_info == mock_contact.extra_info
    assert result.user_id == mock_contact.user_id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_remove_contact(contacts_repository, mock_session, mock_user):
    contact_id = 1
    mock_contact = Contact(id=contact_id, first_name="Test", last_name="Contact", email="test@example.com", phone="1234567890", birthday=datetime.date(1990, 1, 1), extra_info="Info")
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_session.execute.return_value = mock_result

    result = await contacts_repository.remove_contact(contact_id, mock_user)

    assert result == mock_contact
    mock_session.delete.assert_called_once_with(mock_contact)
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_contact(contacts_repository, mock_session, mock_user):
    contact_id = 1
    update_data = ContactUpdateSchema(first_name="Updated Contact")
    mock_contact = Contact(id=contact_id, first_name="Old", last_name="Title", email="test@example.com", phone="1234567890", birthday=datetime.date(1990, 1, 1), extra_info="Info")
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_contact
    mock_session.execute.return_value = mock_result
    mock_session.refresh.return_value = mock_contact

    result = await contacts_repository.update_contact(contact_id, update_data, mock_user)

    assert result.first_name == "Updated Contact"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()