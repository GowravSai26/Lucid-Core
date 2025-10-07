import redis
from Backend.app.config import settings

def get_redis_connection():
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
