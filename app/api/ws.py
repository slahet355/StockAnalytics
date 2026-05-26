import asyncio
import json
import random
from fastapi import WebSocket

clients = set()


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
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


async def background_publisher():
    # Simple demo publisher that sends random price updates every second
    from ..models import PricePoint
    from ..db import async_session
    while True:
        msg = {
            "type": "price_update",
            "symbol": "BTC-USD",
            "price": round(20000 + random.random() * 1000, 2)
        }
        await broadcast(msg)
        # try to persist to DB (best-effort)
        try:
            async with async_session() as session:
                price = PricePoint(symbol=msg["symbol"], price=msg["price"], source="demo")
                session.add(price)
                await session.commit()
        except Exception:
            pass
        await asyncio.sleep(1)
