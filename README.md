# Contacts API

REST API додаток для керування контактами користувачів.

## Функціональність

- Створення, редагування та видалення контактів
- Пошук контактів за різними критеріями
- Відстеження днів народження
- Аутентифікація та авторизація користувачів
- Оновлення профілю користувача

## Технології

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication
- Sphinx Documentation
- Poetry (управління залежностями)

## Встановлення

1. Клонуйте репозиторій:

```bash
git clone https://github.com/your-username/goit-pythonweb-hw-12.git
cd goit-pythonweb-hw-12
```

2. Встановіть Poetry (якщо ще не встановлено):

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Встановіть залежності проекту:

```bash
poetry install
```

4. Активуйте віртуальне середовище:

```bash
poetry shell
```

5. Налаштуйте змінні середовища в файлі `.env`

6. Застосуйте міграції:

```bash
poetry run alembic upgrade head
```

## Запуск

```bash
poetry run uvicorn main:app --reload
```

Документація API буде доступна за адресою: http://localhost:8000/docs

## Документація

Для генерації документації:

```bash
cd docs
poetry install --with docs
poetry run make html
```

Документація буде доступна в директорії `docs/build/html`

## Тестування

```bash
poetry run pytest
```

## Розробка

Для додавання нових залежностей:

```bash
poetry add package_name
```

Для додавання залежностей розробки:

```bash
poetry add --group dev package_name
```

## Ліцензія

MIT License
