"""
Подключение к БД и базовые ORM-объекты.

Вынесено в отдельный модуль, чтобы `app.py` и `models.py` могли его
импортировать без циклической зависимости.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Use PostgreSQL on Replit
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL, future=True)
else:
    # Fallback to SQLite for local development
    DB_PATH = BASE_DIR / "data.db"
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
Base = declarative_base()
