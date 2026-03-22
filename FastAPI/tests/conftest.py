# Источники используемые для написания кода:
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html
# https://docs.python.org/3/library/sys.html#sys.modules
# https://fastapi.tiangolo.com/tutorial/testing/
# https://sky.pro/wiki/media/ispolzovanie-conftest-py-v-pytest/
# https://dev.to/akarshan/mocking-redis-in-pythons-unittest-ha2
# https://docs.pytest.org/en/stable/how-to/monkeypatch.html

# Создаем инфраструктуру для проведения тестов

import sys
import types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient

# Поднимаем тестовую БД (SQLite)
engine = create_engine(
    "sqlite:///./test_api.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаем тестовый модуль БД
mock_db = types.ModuleType("app.database")
mock_db.engine = engine
mock_db.get_db = get_db
mock_db.Session = SessionLocal

# Подмена на тестовую БД (при вызове модуля app.database)
sys.modules["app.database"] = mock_db

# Импорт приложения и модуля управления БД
from app.main import app
from app.models import Base

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Подключаем TestCLient для имитации запросов к API
@pytest.fixture()
def api_client():
    return TestClient(app)

# Производим очистку БД перед тестами
@pytest.fixture(autouse=True)
def reuse_db():
    Base.metadata.drop_all(bind=engine) # Удаляем все таблицы
    Base.metadata.create_all(bind=engine) # Создаем их заново 

# Создаем тестовый Redis
class MockRedis:
    def __init__(self):
        self.storage = {} # Имитация хранилища кэша

    def get(self, key):
        return self.storage.get(key) # Имитация метода get

    def set(self, key, value):
        self.storage[key] = value # Имитация метода set

    def delete(self, key):
        self.storage.pop(key, None) # Имитация метода delete

# Подмена на тестовый Redis
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock_redis = MockRedis()
    monkeypatch.setattr("app.routers.link_methods.redis_client", mock_redis)