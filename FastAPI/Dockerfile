# Источники используемые при написании данного кода
# https://github.com/hse-ai/applied_python/tree/main/fastapi-booking
# https://itandcats.ru/fastapi-deployment-examples

FROM python:3.9 

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Запуск Uvicorn -> FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]