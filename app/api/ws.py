import asyncio
import json
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
    """Publisher that fetches from real APIs and broadcasts updates."""
    from ..models import PricePoint
    from ..db import async_session
    from ..services.fetcher import gather_price_sources
    
    while True:
        try:
            # Fetch from multiple real sources concurrently
            results = await gather_price_sources()
            
            for msg in results:
                await broadcast(msg)
                
                # Persist price updates to DB (not sentiment)
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
        
        # Fetch every 10 seconds to respect API rate limits
        await asyncio.sleep(10)
