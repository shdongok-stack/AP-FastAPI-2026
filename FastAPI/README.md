# Инструкция по запуску тестов

1. Устанавливаем зависимости через
- pip install -r requirements.txt

2. Запускаем тесты
- python3 -m pytest tests

3. Проверяем покрытие
- python3 -m coverage report (отображение покрытия внутри терминала)
- python3 -m coverage html (формирование html кода покрытия для открытия в браузере)
  - open htmlcov/index.html (открыть отчет в браузере)
