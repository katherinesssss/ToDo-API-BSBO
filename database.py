from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

# Читаем переменные окружения из файла .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Переменная DATABASE_URL не найдена. "
        "Создайте файл .env в корне проекта (см. .env.example)."
    )

# Асинхронный движок: подключение к PostgreSQL (Supabase)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,            # Показывать SQL в консоли (удобно для обучения)
    future=True,          # Использовать новый API SQLAlchemy 2.0
    pool_pre_ping=True,   # Проверять, живо ли соединение
    # Отключаем кеш подготовленных выражений: Supabase использует PgBouncer,
    # который может переключать одно соединение между разными транзакциями
    connect_args={"statement_cache_size": 0},
)

# Фабрика сессий для работы с БД
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не сбрасывать объекты после commit
    autoflush=False,         # Не сохранять автоматически при каждом изменении
    autocommit=False,        # Не коммитить автоматически
)

# Базовый класс для всех моделей (Task, User и т.д.)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Создаёт и возвращает сессию БД для одного запроса.

    Пример:
        @router.get("/tasks")
        async def get_tasks(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Task))
            return result.scalars().all()
    """
    async with async_session_maker() as session:
        try:
            yield session  # Отдаём сессию в endpoint
        finally:
            await session.close()  # Закрываем сессию после использования


async def init_db():
    """Создаёт все таблицы в БД (если их нет).

    Создаёт таблицы для всех моделей, унаследованных от Base.
    НЕ ИСПОЛЬЗУЙТЕ В ПРОДАКШЕНЕ: там используются миграции (Alembic).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("База данных инициализирована!")


async def drop_db():
    """Удаляет все таблицы из БД.

    ОПАСНО! Удаляет ВСЕ данные! Используйте только для тестирования.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("Все таблицы удалены!")