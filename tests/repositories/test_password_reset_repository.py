import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, Mock

from src.entity.models import PasswordResetToken
from src.repositories.password_reset_repository import PasswordResetRepository


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session


@pytest.fixture
def password_reset_repository(mock_session):
    return PasswordResetRepository(mock_session)


@pytest.mark.asyncio
async def test_save_token(password_reset_repository, mock_session):
    # Arrange
    user_id = 1
    expires_at = datetime.now() + timedelta(hours=1)

    # Act
    token = await password_reset_repository.save_token(user_id, expires_at)

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_token(password_reset_repository, mock_session):
    # Arrange
    test_token = "test_token"
    mock_reset_token = PasswordResetToken(
        token=test_token,
        user_id=1,
        expires_at=datetime.now() + timedelta(hours=1),
        used=False,
    )
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_reset_token
    mock_session.execute.return_value = mock_result

    # Act
    result = await password_reset_repository.get_token(test_token)

    # Assert
    assert result == mock_reset_token
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_mark_token_as_used(password_reset_repository, mock_session):
    # Arrange
    test_token = "test_token"
    mock_reset_token = PasswordResetToken(
        token=test_token,
        user_id=1,
        expires_at=datetime.now() + timedelta(hours=1),
        used=False,
    )
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_reset_token
    mock_session.execute.return_value = mock_result

    # Act
    await password_reset_repository.mark_token_as_used(test_token)

    # Assert
    assert mock_reset_token.used is True
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_expired_tokens(password_reset_repository, mock_session):
    # Act
    await password_reset_repository.delete_expired_tokens()

    # Assert
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
