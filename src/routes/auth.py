import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    Request,
    BackgroundTasks,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.services.auth import AuthService, oauth2_scheme
from src.schemas.token import TokenResponse, RefreshTokenRequest
from src.schemas.user import (
    UserResponse,
    UserCreate,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
)
from src.services.email import send_email, send_password_reset_email
from src.services.user import UserService
from src.services.password_reset import PasswordResetService
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("uvicorn.error")


def get_auth_service(db: AsyncSession = Depends(get_db)):
    """
    Отримання сервісу аутентифікації.

    Args:
        db (AsyncSession): Сесія бази даних

    Returns:
        AuthService: Екземпляр сервісу аутентифікації
    """
    return AuthService(db)


def get_user_service(db: AsyncSession = Depends(get_db)):
    """
    Отримання сервісу користувача.

    Args:
        db (AsyncSession): Сесія бази даних

    Returns:
        UserService: Екземпляр сервісу користувача
    """
    return UserService(db)


def get_password_reset_service(db: AsyncSession = Depends(get_db)):
    """
    Отримання сервісу скидання пароля.

    Args:
        db (AsyncSession): Сесія бази даних

    Returns:
        PasswordResetService: Екземпляр сервісу скидання пароля
    """
    return PasswordResetService(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Реєстрація нового користувача.

    Args:
        user_data (UserCreate): Дані нового користувача
        background_tasks (BackgroundTasks): Фонові завдання FastAPI
        request (Request): Об'єкт запиту
        auth_service (AuthService): Сервіс аутентифікації

    Returns:
        UserResponse: Дані створеного користувача
    """
    user = await auth_service.register_user(user_data)
    background_tasks.add_task(
        send_email, user_data.email, user_data.username, str(request.base_url)
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Аутентифікація користувача.

    Args:
        form_data (OAuth2PasswordRequestForm): Дані форми входу
        request (Request): Об'єкт запиту
        auth_service (AuthService): Сервіс аутентифікації

    Returns:
        TokenResponse: Токени доступу та оновлення

    Raises:
        HTTPException: При невірних облікових даних
    """
    user = await auth_service.authenticate(form_data.username, form_data.password)
    access_token = auth_service.create_access_token(user.username)
    refresh_token = await auth_service.create_refresh_token(
        user.id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    return TokenResponse(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: RefreshTokenRequest,
    request: Request = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Оновлення токену доступу.

    Args:
        refresh_token (RefreshTokenRequest): Токен оновлення
        request (Request): Об'єкт запиту
        auth_service (AuthService): Сервіс аутентифікації

    Returns:
        TokenResponse: Нові токени доступу та оновлення

    Raises:
        HTTPException: При невалідному токені оновлення
    """
    user = await auth_service.validate_refresh_token(refresh_token.refresh_token)

    new_access_token = auth_service.create_access_token(user.username)
    new_refresh_token = await auth_service.create_refresh_token(
        user.id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )

    await auth_service.revoke_refresh_token(refresh_token.refresh_token)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: RefreshTokenRequest,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Вихід користувача з системи.

    Args:
        refresh_token (RefreshTokenRequest): Токен оновлення для відкликання
        token (str): Токен доступу для відкликання
        auth_service (AuthService): Сервіс аутентифікації

    Returns:
        None: Успішний вихід
    """
    await auth_service.revoke_access_token(token)
    await auth_service.revoke_refresh_token(refresh_token.refresh_token)
    return None


@router.post("/password-reset-request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    password_reset_service: PasswordResetService = Depends(get_password_reset_service),
):
    """
    Запит на скидання пароля.

    Args:
        request (PasswordResetRequest): Запит з email користувача
        password_reset_service (PasswordResetService): Сервіс скидання пароля

    Returns:
        PasswordResetResponse: Повідомлення про відправку інструкцій
    """
    await password_reset_service.request_password_reset(request.email)
    return PasswordResetResponse(
        message="Якщо користувач з такою електронною поштою існує, інструкції щодо скидання пароля будуть відправлені"
    )


@router.post("/password-reset-confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    password_reset_service: PasswordResetService = Depends(get_password_reset_service),
):
    """
    Підтвердження скидання пароля.

    Args:
        request (PasswordResetConfirm): Дані для скидання пароля
        password_reset_service (PasswordResetService): Сервіс скидання пароля

    Returns:
        PasswordResetResponse: Повідомлення про успішну зміну пароля

    Raises:
        HTTPException: При невалідному токені або помилці зміни пароля
    """
    await password_reset_service.confirm_password_reset(request.token, request.new_password)
    return PasswordResetResponse(message="Пароль успішно змінено")
