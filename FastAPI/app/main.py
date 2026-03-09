from fastapi import FastAPI
from .database import engine
from . import models
from .routers import link_methods

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

# Создаем объект FastAPI
app = FastAPI()

# Подключаем router со всеми endpoint-ами
app.include_router(link_methods.router)
