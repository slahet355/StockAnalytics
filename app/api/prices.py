from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..models import PricePoint
from ..db import get_session
from ..services.fetcher import gather_price_sources

router = APIRouter()


@router.post("/prices", response_model=PricePoint)
async def create_price(price: PricePoint, session: AsyncSession = Depends(get_session)):
    session.add(price)
    await session.commit()
    await session.refresh(price)
    return price


@router.get("/prices", response_model=List[PricePoint])
async def list_prices(limit: int = 100, session: AsyncSession = Depends(get_session)):
    stmt = select(PricePoint).limit(limit)
    result = await session.exec(stmt)
    return result.all()


@router.get("/fetch", response_model=List[Dict[str, Any]])
async def fetch_prices():
    """Manually trigger fetching from all configured sources."""
    results = await gather_price_sources()
    return results
