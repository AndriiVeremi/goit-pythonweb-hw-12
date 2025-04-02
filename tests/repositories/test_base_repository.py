import pytest
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Base
from src.repositories.base import BaseRepository


# Тестова модель
class TestModel(Base):
    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)


@pytest.fixture
def test_data() -> dict:
    return {"name": "Test Item", "description": "Test Description"}


@pytest.fixture
async def test_model(test_data: dict, session: AsyncSession) -> TestModel:
    model = TestModel(**test_data)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


@pytest.fixture
async def base_repository(
    session: AsyncSession,
) -> AsyncGenerator[BaseRepository, None]:
    yield BaseRepository(session, TestModel)


@pytest.mark.asyncio
async def test_get_by_id(base_repository: BaseRepository, test_model: TestModel):
    result = await base_repository.get_by_id(test_model.id)
    assert result is not None
    assert result.id == test_model.id
    assert result.name == test_model.name
    assert result.description == test_model.description


@pytest.mark.asyncio
async def test_get_all(base_repository: BaseRepository, test_model: TestModel):
    results = await base_repository.get_all()
    assert len(results) == 1
    assert results[0].id == test_model.id


@pytest.mark.asyncio
async def test_create(base_repository: BaseRepository, test_data: dict):
    model = TestModel(**test_data)
    result = await base_repository.create(model)
    assert result is not None
    assert result.name == test_data["name"]
    assert result.description == test_data["description"]


@pytest.mark.asyncio
async def test_update(base_repository: BaseRepository, test_model: TestModel):
    test_model.name = "Updated Name"
    result = await base_repository.update(test_model)
    assert result is not None
    assert result.name == "Updated Name"
    assert result.description == test_model.description  # Не змінилося


@pytest.mark.asyncio
async def test_delete(base_repository: BaseRepository, test_model: TestModel):
    await base_repository.delete(test_model)

    # Перевіряємо, що об'єкт дійсно видалений
    deleted = await base_repository.get_by_id(test_model.id)
    assert deleted is None
