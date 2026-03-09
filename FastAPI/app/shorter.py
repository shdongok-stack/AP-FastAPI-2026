# Источники используемые при написании данного кода
# https://docs.python.org/3/library/secrets.html
# https://labex.io/ru/tutorials/python-create-a-url-shortener-with-python-flask-445790

import string
import secrets

def generate_shortlink(length: int = 6):
    all_str = string.ascii_letters + string.digits # Собираем все буквы и числа в 1 переменную
    return ''.join(secrets.choice(all_str) for _ in range(length)) # Генерируем случайный набор 6 символов