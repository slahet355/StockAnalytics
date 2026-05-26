from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import asyncio
from .api import ws as ws_module
from . import db, cache
from .api import prices as prices_module

app = FastAPI(title="StockAnalytics")

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(prices_module.router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup_event():
    # Initialize DB and Redis then start background tasks
    await db.init_db()
    await cache.init_redis()
    asyncio.create_task(ws_module.redis_subscriber())
    asyncio.create_task(ws_module.background_publisher())


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await ws_module.websocket_endpoint(websocket)
