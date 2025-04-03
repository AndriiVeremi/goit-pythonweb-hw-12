import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, Mock
from sqlalchemy import Column, Integer, String

from src.entity.models import Base
from src.repositories.base import BaseRepository


class TestModel(Base):
    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def base_repository(mock_session):
    return BaseRepository(mock_session, TestModel)


@pytest.mark.asyncio
async def test_get_all(base_repository, mock_session):
    # Arrange
    mock_models = [TestModel(), TestModel()]
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_models
    mock_session.execute.return_value = mock_result

    # Act
    result = await base_repository.get_all()

    # Assert
    assert result == mock_models
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_found(base_repository, mock_session):
    # Arrange
    test_id = 1
    mock_model = TestModel()
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_model
    mock_session.execute.return_value = mock_result

    # Act
    result = await base_repository.get_by_id(test_id)

    # Assert
    assert result == mock_model
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(base_repository, mock_session):
    # Arrange
    test_id = 999
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Act
    result = await base_repository.get_by_id(test_id)

    # Assert
    assert result is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create(base_repository, mock_session):
    # Arrange
    test_model = TestModel()

    # Act
    result = await base_repository.create(test_model)

    # Assert
    assert result == test_model
    mock_session.add.assert_called_once_with(test_model)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(test_model)


@pytest.mark.asyncio
async def test_update(base_repository, mock_session):
    # Arrange
    test_model = TestModel()

    # Act
    result = await base_repository.update(test_model)

    # Assert
    assert result == test_model
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(test_model)


@pytest.mark.asyncio
async def test_delete(base_repository, mock_session):
    # Arrange
    test_model = TestModel()

    # Act
    await base_repository.delete(test_model)

    # Assert
    mock_session.delete.assert_called_once_with(test_model)
    mock_session.commit.assert_called_once()
