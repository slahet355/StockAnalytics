import os
import json
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CHANNEL = "stockanalytics:feed"
LATEST_KEY = "stockanalytics:latest"
RECENT_KEY = "stockanalytics:recent"

redis = None


async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        await redis.ping()
    except Exception:
        pass


async def save_latest_feed(message: dict):
    if redis is None:
        return
    body = json.dumps(message)
    await redis.set(LATEST_KEY, body)
    await redis.lpush(RECENT_KEY, body)
    await redis.ltrim(RECENT_KEY, 0, 99)


async def get_latest_feed() -> dict | None:
    if redis is None:
        return None
    raw = await redis.get(LATEST_KEY)
    return json.loads(raw) if raw else None


async def get_recent_feeds(limit: int = 20) -> list[dict]:
    if redis is None:
        return []
    raw_items = await redis.lrange(RECENT_KEY, 0, limit - 1)
    return [json.loads(item) for item in raw_items]


async def publish_feed(message: dict):
    if redis is None:
        return
    await save_latest_feed(message)
    await redis.publish(REDIS_CHANNEL, json.dumps(message))
