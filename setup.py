from setuptools import setup, find_packages

setup(
    name="goit-pythonweb-hw-12",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "asyncpg",
        "pydantic-settings",
        "redis",
        "passlib[bcrypt]",
        "jwt",
        "anyio",
        "pyjwt",
        "itsdangerous",
        "apscheduler",
        "slowapi",
        "fastapi-mail",
        "libgravatar",
        "cloudinary",
    ],
)
