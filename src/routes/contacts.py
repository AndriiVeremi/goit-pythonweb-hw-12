import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.depend_service import get_current_user
from src.database.db import get_db
from src.entity.models import User
from src.services.contacts import ContactService
from src.schemas.contact import (
    ContactResponse,
    ContactSchema,
    ContactUpdateSchema,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = logging.getLogger("uvicorn.error")


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(10, ge=10, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Отримання списку контактів з пагінацією.

    Args:
        limit (int): Кількість контактів на сторінку (від 10 до 100)
        offset (int): Зміщення від початку списку
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        list[ContactResponse]: Список контактів
    """
    cont_service = ContactService(db)
    contacts = await cont_service.get_contacts(limit, offset, user)
    logger.info(f"Fetched {len(contacts)} contacts")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Отримання контакту за його ідентифікатором.

    Args:
        contact_id (int): Ідентифікатор контакту
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        ContactResponse: Дані контакту

    Raises:
        HTTPException: Якщо контакт не знайдено
    """
    cont_service = ContactService(db)
    contact = await cont_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")
    return contact


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: ContactSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Створення нового контакту.

    Args:
        body (ContactSchema): Дані нового контакту
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        ContactResponse: Створений контакт

    Raises:
        HTTPException: При помилці створення контакту
    """
    logger.info(f"Creating new contact: {body}")
    try:
        cont_service = ContactService(db)
        return await cont_service.create_contact(body, user)
    except Exception as e:
        logger.error(f"Помилка створення контакту: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdateSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Оновлення існуючого контакту.

    Args:
        contact_id (int): Ідентифікатор контакту
        body (ContactUpdateSchema): Дані для оновлення
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        ContactResponse: Оновлений контакт

    Raises:
        HTTPException: Якщо контакт не знайдено
    """
    cont_service = ContactService(db)
    contact = await cont_service.update_contact(contact_id, body, user)
    if contact is None:
        logger.warning(f"Контакт з ID {contact_id} не знайдено для оновлення")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")
    logger.info(f"Контакт з ID {contact_id} успішно оновлено")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Видалення контакту.

    Args:
        contact_id (int): Ідентифікатор контакту для видалення
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        None: Контакт успішно видалено
    """
    cont_service = ContactService(db)
    await cont_service.remove_contact(contact_id, user)
    logger.info(f"Контакт з ID {contact_id} успішно видалено")
    return None


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Пошук контактів за різними критеріями.

    Args:
        first_name (Optional[str]): Ім'я для пошуку
        last_name (Optional[str]): Прізвище для пошуку
        email (Optional[str]): Email для пошуку
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        list[ContactResponse]: Список знайдених контактів

    Raises:
        HTTPException: Якщо контакти не знайдено
    """
    cont_service = ContactService(db)
    contacts = await cont_service.search_contacts(first_name, last_name, email, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакти не знайдено")
    logger.info(f"Знайдено {len(contacts)} контактів")
    return contacts


@router.get("/birthdays/", response_model=list[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(default=7, ge=1),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Отримання списку контактів з найближчими днями народження.

    Args:
        days (int): Кількість днів для перевірки (за замовчуванням 7)
        user (User): Поточний аутентифікований користувач
        db (AsyncSession): Сесія бази даних

    Returns:
        list[ContactResponse]: Список контактів з найближчими днями народження
    """
    cont_service = ContactService(db)
    contacts = await cont_service.get_upcoming_birthdays(days, user)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакти з найближчими днями народження не знайдено",
        )
    return contacts
