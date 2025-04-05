from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.core.depend_service import (
    get_auth_service,
    get_current_moderator_user,
    get_user_service,
    get_current_user,
    get_current_admin,
)
from src.core.email_token import get_email_from_token
from src.entity.models import User, UserRole
from src.schemas.user import UserResponse
from src.services.auth import AuthService, oauth2_scheme
from src.services.email import send_email
from src.services.upload_file_service import UploadFileService
from src.services.user import UserService
from src.schemas.email import RequestEmail
from src.database.db import get_db

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserResponse)
@limiter.limit("10/minute")
async def me(
    request: Request,
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Отримання інформації про поточного користувача.

    Args:
        request (Request): Об'єкт запиту
        token (str): Токен доступу
        auth_service (AuthService): Сервіс аутентифікації

    Returns:
        UserResponse: Дані поточного користувача

    Raises:
        HTTPException: При невалідному токені
    """
    return await auth_service.get_current_user(token)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отримання інформації про користувача за ID.

    Args:
        user_id (int): ID користувача
        db (AsyncSession): Сесія бази даних
        current_user (User): Поточний користувач

    Returns:
        UserResponse: Дані користувача

    Raises:
        HTTPException: Якщо користувача не знайдено
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")
    return user


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, user_service: UserService = Depends(get_user_service)):
    """
    Підтвердження email користувача.

    Args:
        token (str): Токен підтвердження email
        user_service (UserService): Сервіс користувача

    Returns:
        dict: Повідомлення про статус підтвердження

    Raises:
        HTTPException: При помилці верифікації
    """
    email = get_email_from_token(token)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email has already been confirmed."}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    user_service: UserService = Depends(get_user_service),
):
    """
    Запит на повторне підтвердження email.

    Args:
        body (RequestEmail): Дані запиту з email
        background_tasks (BackgroundTasks): Фонові завдання FastAPI
        request (Request): Об'єкт запиту
        user_service (UserService): Сервіс користувача

    Returns:
        dict: Повідомлення про статус запиту
    """
    user = await user_service.get_user_by_email(str(body.email))

    if user.confirmed:
        return {"message": "Your email has already been confirmed."}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Оновлення аватара користувача.
    Тільки адміністратори можуть змінювати свій аватар.

    Args:
        file (UploadFile): Файл нового аватара
        current_user (User): Поточний користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        UserResponse: Оновлені дані користувача

    Raises:
        HTTPException: Якщо користувач не є адміністратором або виникла помилка при оновленні
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки адміністратори можуть змінювати свій аватар",
        )

    user_service = UserService(db)
    user = await user_service.update_avatar(current_user.id, file)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")
    return user


@router.get("/moderator")
def read_moderator(
    current_user: User = Depends(get_current_moderator_user),
):
    """
    Ендпоінт для модераторів.

    Args:
        current_user (User): Поточний користувач з правами модератора

    Returns:
        dict: Привітальне повідомлення для модератора

    Raises:
        HTTPException: При недостатніх правах доступу
    """
    return {
        "message": f"Hello, {current_user.username}! This is the route for moderators and administrators"
    }


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin)):
    """
    Ендпоінт для адміністраторів.

    Args:
        current_user (User): Поточний користувач з правами адміністратора

    Returns:
        dict: Привітальне повідомлення для адміністратора

    Raises:
        HTTPException: При недостатніх правах доступу
    """
    return {"message": f"Вітаємо, {current_user.username}! This is the route for administrators"}
