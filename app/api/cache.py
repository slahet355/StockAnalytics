from fastapi import APIRouter
from typing import List

from .. import cache

router = APIRouter()


@router.get("/cache/latest")
async def latest_feed():
    """Return the latest cached live feed message."""
    result = await cache.get_latest_feed()
    return result or {}


@router.get("/cache/recent", response_model=List[dict])
async def recent_feeds(limit: int = 20):
    """Return recent cached live feed messages."""
    return await cache.get_recent_feeds(limit)
