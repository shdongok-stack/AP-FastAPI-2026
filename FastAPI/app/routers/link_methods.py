# Источники используемые при написании данного кода
# https://github.com/hse-ai/applied_python/tree/main/fastapi-booking
# https://fastapi.tiangolo.com/tutorial/sql-databases/#update-a-hero-with-heroupdate
# https://stackoverflow.com/questions/6028231/http-status-code-for-an-expired-link
# https://fastapi.tiangolo.com/advanced/custom-response/#jsonresponse

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Link
from ..schemas import LinkCreate, LinkResponse, LinkStats
from ..shorter import generate_shortlink
from ..redis import redis_client


# Создаем router
router = APIRouter(
    prefix="/links",
    tags=["links"]
)

# Эндпоинт создания короткой ссылки
@router.post("/shorten", response_model=LinkResponse)
def create_short_link(link:LinkCreate, db: Session = Depends(get_db)):
    if link.short_name is not None: # Проверка - указал ли пользователь кастомный alias
        alias_checker = db.query(Link).filter(Link.short_name == link.short_name).first() # Проверяем есть ли уже такой alias в БД

        if alias_checker is not None: # Если alias уже существует, то сообщаем об ошибку
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "description": "Alias уже существует"
                }
            )
        
        short_name = link.short_name # Если alias доступен, то записываем его
    else:
        short_name = generate_shortlink() # Если юзер не указал alias, то генерируем случайное название

    new_link = Link( # Создаем объект модели Link
        original_url=str(link.original_url), # Преобразуем HttpUrl в строку
        short_name=short_name, # Короткое название ссылки
        expiration_date=link.expiration_date # Дата истекания срока жизни ссылки
    )

    db.add(new_link) # Добавляем объект в сессию
    db.commit() # Сохраняем изменение в БД
    db.refresh(new_link) # Обновляем объект из БД

    return new_link

# Эндпоинт поиска короткой ссылки по оригинальному URL
@router.get("/search", response_model=list[LinkResponse])
def search_link(original_url: str, db: Session = Depends(get_db)):

    # Ищем все ссылки с данным оригинальным URL
    links = db.query(Link).filter(Link.original_url == original_url).all()

    return links

# Эндпоинт отображения истекших ссылок (дополнительная функция)
@router.get("/expired", response_model=list[LinkStats])
def get_expired_links(db: Session = Depends(get_db)):

    # Поиск ссылок, у которых истек срок
    exp_links = db.query(Link).filter(Link.expiration_date < datetime.utcnow()).all()

    return exp_links # Получаем список ссылок с истекшим сроком

# Эндпоинт перехода по короткой ссылке
@router.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    
    url_cached = redis_client.get(short_code) # Проверка есть ли короткая ссылка в кэше

    if url_cached is not None:
        return RedirectResponse(url=url_cached, status_code=307) # Если ссылка в кэше есть - проводим редирект

    link = db.query(Link).filter(Link.short_name == short_code).first() # Запрос к БД
    if link is None: # Если ссылка не найдена, то сообщаем об ошибку
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "description": "Короткая ссылка не найдена"
            }
        )
   
    # Проверяем срок жизни короткой ссылки (если есть)
    if link.expiration_date is not None and link.expiration_date < datetime.utcnow():
        raise HTTPException(
            status_code=410,
            detail={
                "status": "error",
                "description": "Истек срок работы короткой ссылки"
            }
        )
   
    link.last_used = datetime.utcnow() # Обновление даты последнего перехода по ссылке
    link.click_count += 1 # Увеличиваем счетчик перехода по ссылке
    db.commit() # Сохраняем изменения в БД
    
    redis_client.set(short_code, link.original_url) # Сохранение ссылки в redis (если ее там нет)

    return RedirectResponse(url=link.original_url, status_code=307) # Редирект юзера по оригинальной ссылке

# Эндпоинт получения статистики по ссылке
@router.get("/{short_code}/stats", response_model=LinkStats)
def get_link_stats(short_code: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_name == short_code).first() # Ищем ссылку в БД
    if link is None: # Если ссылка не найдена, то сообщаем об ошибку
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "description": "Короткая ссылка не найдена"
            }
        )
    return link # Возврат статистики по ссылке

# Эндпоинт удаления короткой ссылки
@router.delete("/{short_code}")
def delete_link(short_code: str, db: Session = Depends(get_db)):
   
    link = db.query(Link).filter(Link.short_name == short_code).first() # Ищем ссылку в БД
    if link is None: # Если ссылка не найдена, то сообщаем об ошибку
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "description": "Короткая ссылка не найдена"
            }
        )
   
    db.delete(link) # Удаляем ссылку
    db.commit() # Сохраняем изменение в БД
    redis_client.delete(short_code) # Удаление кэша
   
    return {
    "status": "success",
    "description": "Ссылка успешно удалена"
}

# Эндпоинт обновления короткой ссылки
@router.put("/{short_code}", response_model=LinkResponse)
def update_link(short_code: str, link_data: LinkCreate, db: Session = Depends(get_db)):
    
    link = db.query(Link).filter(Link.short_name == short_code).first() # Ищем ссылку в БД
    if link is None: # Если ссылка не найдена, то сообщаем об ошибку
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "description": "Короткая ссылка не найдена"
            }
        )

    link.original_url = str(link_data.original_url) # Обновляем оригинальную ссылку

    db.commit() # Сохраняем изменение в БД
    db.refresh(link) # Обновляем объект из БД
    redis_client.delete(short_code) # Удаление кэша

    return link