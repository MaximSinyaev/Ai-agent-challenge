from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
import os
from pathlib import Path

# Путь к файлу базы данных
DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATABASE_DIR / "agents.db"

# URL для подключения к SQLite
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# Создаем async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # True для отладки SQL запросов
    future=True
)

# Создаем session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Dependency для получения сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована")


async def close_db():
    """Закрытие соединения с базой данных"""
    await engine.dispose()
    print("Соединение с базой данных закрыто")