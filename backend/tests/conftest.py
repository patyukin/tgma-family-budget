import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Создаем тестовую in-memory SQLite базу данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Создаем фабрику тестовых сессий
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def setup_test_db():
    # Создаем все таблицы в тестовой БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Закрываем соединение с БД
    await engine.dispose()


@pytest.fixture
async def test_db(setup_test_db):
    # Создаем новую сессию для каждого теста
    async with TestSessionLocal() as session:
        yield session
        # Откатываем изменения после каждого теста
        await session.rollback()


@pytest.fixture
def test_client(monkeypatch):
    # Переопределяем функцию получения БД для тестов
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
            await session.rollback()

    # Заменяем оригинальную функцию на тестовую
    app.dependency_overrides[get_db] = override_get_db
    
    # Создаем тестовый клиент
    with TestClient(app) as client:
        yield client
    
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Создаем цикл событий для pytest-asyncio"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
