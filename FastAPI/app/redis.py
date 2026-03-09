# Источники используемые при написании данного кода
# https://medium.com/@suganthi2496/building-a-rest-api-with-fastapi-and-redis-caching-278c4dc07d70

import redis
redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)