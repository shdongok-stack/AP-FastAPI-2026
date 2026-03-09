# Источники используемые при написании данного кода
# https://github.com/hse-ai/applied_python/tree/main/fastapi-booking
# https://docs.pydantic.dev/1.10/usage/model_config/

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, EmailStr

class LinkCreate(BaseModel):
    """
    Схема создания короткой ссылки
    """
    original_url: HttpUrl # Оригинальная ссылка
    expiration_date: Optional[datetime] = None # Дата, когда ссылка перестает работать
    short_name: Optional[str] = None # Собственный (кастомный) alias 

class LinkResponse(BaseModel):
    """
    Схема ответа при создании ссылки
    """

    original_url: HttpUrl # Оригинальная ссылка
    short_name: str # Короткая ссылка
    creation_date: datetime # Дата создания ссылки

    class Config:
        # Чтение данных из SQLAlchemy моделей
        orm_mode = True

class LinkStats(BaseModel):
    """
    Схема отображения статистики ссылки
    """
    original_url: HttpUrl # Оригинальная ссылка
    creation_date: datetime # Дата создания ссылки
    click_count: int # Кол-во переходов по ссылке
    last_used: Optional[datetime] = None # Дата последнего перехода

    class Config:
        # Чтение данных из SQLAlchemy моделей
        orm_mode = True