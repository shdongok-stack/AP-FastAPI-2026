# Тестируем создание ссылки
def test_create_link(api_client): 
    response = api_client.post("/links/shorten", json={"original_url": "https://example.com"}) # Отправка запроса
    assert response.status_code == 200 # Проверка успешности обработки запроса

# Тестируем создание ссылки с alias
def test_create_link_alias(api_client):
    response = api_client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "short_name": "hsetop"
    }) # Создаем ссылку с alias
    assert response.status_code == 200 # Проверка успешности обработки запроса

# Тестируем создание ссылки с alias - ошибка одинаковых alias
def test_existed_alias(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://example.com", 
        "short_name": "check"
    }) # Создаем ссылку с alias

    response = api_client.post("/links/shorten", json={
        "original_url": "https://example.com", 
        "short_name": "check"
    }) # Создание ссылки с тем же alias
    assert response.status_code == 400 # Проверка получения ошибки - alias должен быть уникален

# Тестируем поиск по оригинальной ссылке
def test_search_links(api_client):
    api_client.post("/links/shorten", json={"original_url": "https://example.com"}) # Создаем коротку ссылку

    response = api_client.get("/links/search", params={"original_url": "https://example.com"}) # Поиск по оригинальной ссылке
    assert response.status_code == 200 # Проверка успешности обработки запроса

# Тестируем запрос ссылок с истекшим сроком действия
def test_expired_links(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://expired.com",
        "expiration_date": "2020-01-01T00:00:00"
    }) # Создаем ссылку с истекшим сроком действия

    response = api_client.get("/links/expired") # Запрос списка просроченных ссылок
    assert response.status_code == 200 # Проверка успешности обработки запроса

# Тестируем поиск ссылки, которой нет в БД
def test_search_not_existed(api_client):
    response = api_client.get("/links/search", params={"original_url": "https://notexisted.com"}) # Поиск несуществующей ссылки

    assert response.status_code == 200 # Успешный запрос
    assert response.json() == [] # Никаких данных об этой ссылки нет

# Тест редиректа
def test_redirect_db(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "short_name": "redirection"
    }) # Создаем тестовую ссылку для проверки редиректа

    response = api_client.get("/links/redirection", follow_redirects=False) # Переход по короткой ссылке. Без авто-редиректа для проверки статус кода
    assert response.status_code == 307 # Проверка редиректа

# Тест редиректа по несуществующей ссылке
def test_redirect_not_existed(api_client):
    response = api_client.get("/links/notexisted") # Редирект по несуществующей короткой ссылке
    assert response.status_code == 404 # Проверка наличия ошибки

# Тест редиректа по просроченной ссылке
def test_redirect_expired(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://expired.com",
        "short_name": "expired_1",
        "expiration_date": "2020-01-01T00:00:00"
    }) # Создаем ссылку с истекшим сроком действия

    response = api_client.get("/links/expired_1") # Редирект по несуществующей короткой ссылке, у которой истек срок
    assert response.status_code == 410 # Проверка наличия ошибки

# Тест счетчика переходов и даты последнего перехода 
def test_clicks_last_used(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "short_name": "clickuse"
    }) # Создаем тестовую ссылку

    api_client.get("/links/clickuse", follow_redirects=False) # Делаем переход по короткой ссылке

    stats = api_client.get("/links/clickuse/stats") # Запрос статистики по короткой ссылке
    assert stats.status_code == 200 # Ожидаем успешность запроса
    assert stats.json()["click_count"] >= 1 # Проверка увеличения счетччика переходов
    assert stats.json()["last_used"] is not None # Проверка даты последнего перехода (не пусто)

# Тест запроса статистики по несуществующей ссылке
def test_stats_not_existed(api_client):
    response = api_client.get("/links/notexisted_1/stats") # Запрос статистики по несуществующей ссылке
    assert response.status_code == 404 # Проверка наличия ошибки

# Тест удаления ссылки
def test_delete(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "short_name": "delete"
    }) # Создаение тестовой ссылки

    response = api_client.delete("/links/delete") # Удаление ссылки
    assert response.status_code == 200 # Проверка успешности удаления

# Тест удаления несуществующей ссылки
def test_delete_not_existed(api_client):
    response = api_client.delete("/links/notexisted2") # Удаление несуществующей ссылки
    assert response.status_code == 404 # Проверка наличия ошибки

# Тест обновления ссылки
def test_update(api_client):
    api_client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "short_name": "update"
    }) # Создание тестовой ссылки

    response = api_client.put("/links/update", json={"original_url": "https://example1.com"}) # Обновление ссылки
    assert response.status_code == 200 # Проверки успешности обновления

# Тест обновления несущесвтующей ссылки
def test_update_not_existed(api_client):
    response = api_client.put("/links/notexisted3", json={"original_url": "https://example2.com"}) # Обновляем несуществующую ссылку
    assert response.status_code == 404 # Проверяем наличие ошибки