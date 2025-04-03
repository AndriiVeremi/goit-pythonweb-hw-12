"""
Модуль, що містить моделі бази даних для додатку контактів.

Цей модуль визначає всі моделі SQLAlchemy, які використовуються в додатку,
включаючи користувачів, контакти, токени оновлення та токени скидання паролю.
"""

from datetime import datetime, date
from enum import Enum
from typing import Any

from sqlalchemy import (
    String,
    Date,
    ForeignKey,
    DateTime,
    func,
    Text,
    Boolean,
    Enum as SqlEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Базовий клас для всіх моделей SQLAlchemy.
    
    Цей клас використовується як базовий для всіх моделей в додатку.
    Він наслідується від DeclarativeBase SQLAlchemy і надає базову
    функціональність для ORM.

    Attributes:
        metadata: Об'єкт метаданих SQLAlchemy для керування схемою бази даних
        registry: Реєстр класів моделей
        
    Note:
        Всі моделі в додатку повинні наслідуватися від цього класу для
        забезпечення правильної роботи з базою даних.
    """
    pass


class Contact(Base):
    """
    Модель для зберігання контактів користувачів.

    Attributes:
        id (int): Унікальний ідентифікатор контакту
        first_name (str): Ім'я контакту
        last_name (str): Прізвище контакту
        email (str): Email адреса контакту
        phone (str): Номер телефону контакту
        birthday (date): Дата народження контакту
        extra_info (str): Додаткова інформація про контакт
        user_id (int): Ідентифікатор користувача, якому належить контакт
        user (User): Зв'язок з моделлю користувача
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    extra_info: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class UserRole(str, Enum):
    """
    Перелік можливих ролей користувача.

    Attributes:
        USER: Звичайний користувач
        MODERATOR: Модератор з розширеними правами
        ADMIN: Адміністратор з повними правами
    """
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(Base):
    """
    Модель користувача системи.

    Attributes:
        id (int): Унікальний ідентифікатор користувача
        username (str): Унікальне ім'я користувача
        email (str): Унікальна email адреса користувача
        hash_password (str): Хешований пароль користувача
        role (UserRole): Роль користувача в системі
        avatar (str): URL аватара користувача
        confirmed (bool): Статус підтвердження email
        refresh_tokens (list[RefreshToken]): Список токенів оновлення
        password_reset_tokens (list[PasswordResetToken]): Список токенів скидання паролю
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole), default=UserRole.USER, nullable=False
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user"
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user"
    )


class RefreshToken(Base):
    """
    Модель для зберігання токенів оновлення.

    Attributes:
        id (int): Унікальний ідентифікатор токену
        user_id (int): Ідентифікатор користувача
        token_hash (str): Хеш токену оновлення
        created_at (datetime): Час створення токену
        expired_at (datetime): Час закінчення дії токену
        revoked_at (datetime): Час відкликання токену
        ip_address (str): IP адреса, з якої було створено токен
        user_agent (str): User-Agent браузера
        user (User): Зв'язок з моделлю користувача
    """
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class PasswordResetToken(Base):
    """
    Модель для зберігання токенів скидання паролю.

    Attributes:
        id (int): Унікальний ідентифікатор токену
        user_id (int): Ідентифікатор користувача
        token (str): Унікальний токен для скидання паролю
        expires_at (datetime): Час закінчення дії токену
        used (bool): Прапорець використання токену
        created_at (datetime): Час створення токену
        user (User): Зв'язок з моделлю користувача
    """
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column()
    used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")
