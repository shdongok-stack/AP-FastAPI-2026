# Источники используемые при написании данного кода
# https://github.com/hse-ai/applied_python/tree/main/fastapi-booking
# https://colab.research.google.com/drive/1Ac4e-Xaby3iNnYHQ-lHzhW3aN8Ww3v88?usp=sharing#scrollTo=LsLzH6wYEu2V

from sqlalchemy.sql import func
from sqlalchemy import Column, String, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Link(Base):
    """
    Таблица для хранения информации о сокращенных ссылках
    """
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True) # Идентификатор ссылки
    original_url = Column(String, nullable=False) # Оригинальная ссылка
    short_name = Column(String, unique=True, index=True) # Короткое название ссылки
    creation_date = Column(TIMESTAMP, default=func.now()) # Дата создания ссылки
    expiration_date = Column(TIMESTAMP, nullable=True) # Дата, когда ссылка перестает работать
    click_count = Column(Integer, default=0) # Кол-во переходов по ссылке
    last_used = Column(TIMESTAMP, nullable=True) # Дата последнего перехода по ссылке
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Ключ для связи с таблицей юзеров
    user = relationship("User", back_populates="links") # Установка связи с таблицей users

class User(Base):
    """
    Таблица для хранения информации пользователях, которые использовали сервис сокращения ссылок.
    """
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # Идентификатор пользователя
    email = Column(String, unique=True, nullable=False) # Почта пользователя
    hashed_password = Column(String, nullable=False) # Захэщированный пароль пользователя
    registered_at = Column(TIMESTAMP, default=func.now()) # Дата регистрации пользователя
    links = relationship("Link", back_populates="user") # Установка связи с таблицей links