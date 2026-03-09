# Источники используемые при написании данного кода
# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
# https://github.com/hse-ai/applied_python/tree/main/fastapi-booking

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Реализовыаем retry логику подключения к БД. Делаем эту логику, т.к. FastAPI может запуститься быстрее чем PostgreSQL
for attempt in range(5):
    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        connection.close()
        print("Successful connection to DB")
        break
    except Exception as e:
        print("DB is not ready")
        time.sleep(3)
else:
    raise Exception("Cannot connect to DB")

Session = sessionmaker(bind=engine, autocommit=False)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()