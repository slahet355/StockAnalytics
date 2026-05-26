import asyncio
import json
import uuid
from fastapi import WebSocket

from .. import cache

clients = set()
ORIGIN_ID = str(uuid.uuid4())


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    latest = await cache.get_latest_feed()
    if latest is not None:
        await websocket.send_text(json.dumps(latest))

    clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # echo for now
            await websocket.send_text(f"echo: {data}")
    except Exception:
        pass
    finally:
        clients.discard(websocket)


async def broadcast(message: dict):
    text = json.dumps(message)
    to_remove = []
    for ws in clients:
        try:
            await ws.send_text(text)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        clients.discard(ws)


async def redis_subscriber():
    if cache.redis is None:
        return

    pubsub = cache.redis.pubsub()
    await pubsub.subscribe(cache.REDIS_CHANNEL)
    try:
        async for message in pubsub.listen():
            if message is None:
                continue
            if message.get("type") != "message":
                continue
            try:
                payload = json.loads(message["data"])
            except Exception:
                continue
            await broadcast(payload)
    except Exception as e:
        print(f"Redis subscriber error: {e}")
    finally:
        await pubsub.close()


async def background_publisher():
    """Publisher that fetches from real APIs, caches updates, and publishes them."""
    from ..models import PricePoint
    from ..db import async_session
    from ..services.fetcher import gather_price_sources
    
    while True:
        try:
            results = await gather_price_sources()
            for msg in results:
                msg["origin"] = ORIGIN_ID
                try:
                    await cache.publish_feed(msg)
                except Exception as e:
                    print(f"Redis publish error: {e}")
                    await broadcast(msg)

                if msg.get("type") == "price_update":
                    try:
                        async with async_session() as session:
                            price = PricePoint(
                                symbol=msg["symbol"],
                                price=msg["price"],
                                source=msg.get("source", "unknown")
                            )
                            session.add(price)
                            await session.commit()
                    except Exception as e:
                        print(f"DB persist error: {e}")
        except Exception as e:
            print(f"Publisher error: {e}")
        await asyncio.sleep(10)
