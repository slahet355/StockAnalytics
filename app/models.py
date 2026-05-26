from sqlmodel import SQLModel, Field
from typing import Optional


class PricePoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    price: float
    source: Optional[str] = None
