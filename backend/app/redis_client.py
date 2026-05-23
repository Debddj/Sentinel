"""Redis connection and pub/sub helpers."""
import aioredis
from app.config import settings

redis = None

async def get_redis():
    """Get or create Redis connection."""
    global redis
    if not redis:
        redis = await aioredis.from_url(settings.REDIS_URL)
    return redis

async def close_redis():
    """Close Redis connection."""
    global redis
    if redis:
        await redis.close()
        redis = None
