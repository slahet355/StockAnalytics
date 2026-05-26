import asyncio
import httpx
import os
from typing import Optional, Dict, Any, List

COINDESK_API = "https://api.coindesk.com/v1/bpi/currentprice"
ALPHA_VANTAGE_API = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo")
REDDIT_API = "https://www.reddit.com/r/cryptocurrency/new.json"


async def fetch_coindesk_price(symbol: str = "BTC") -> Optional[Dict[str, Any]]:
    """Fetch Bitcoin/crypto price from CoinDesk."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{COINDESK_API}/{symbol}.json")
            resp.raise_for_status()
            data = resp.json()
            return {
                "type": "price_update",
                "symbol": f"{symbol}-USD",
                "price": data.get("bpi", {}).get("USD", {}).get("rate_float"),
                "source": "coindesk",
            }
    except Exception as e:
        print(f"CoinDesk fetch error: {e}")
        return None


async def fetch_alpha_vantage_price(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock price from Alpha Vantage (demo key has limits)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                ALPHA_VANTAGE_API,
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": ALPHA_VANTAGE_KEY,
                }
            )
            resp.raise_for_status()
            data = resp.json()
            quote = data.get("Global Quote", {})
            price = quote.get("05. price")
            if price:
                return {
                    "type": "price_update",
                    "symbol": symbol,
                    "price": float(price),
                    "source": "alpha_vantage",
                }
    except Exception as e:
        print(f"Alpha Vantage fetch error: {e}")
    return None


async def fetch_reddit_sentiment() -> Optional[Dict[str, Any]]:
    """Fetch recent sentiment from r/cryptocurrency."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                REDDIT_API,
                headers={"User-Agent": "StockAnalytics/1.0"}
            )
            resp.raise_for_status()
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            # Simple: count upvotes on recent posts as sentiment proxy
            total_score = sum(p.get("data", {}).get("score", 0) for p in posts[:10])
            avg_sentiment = total_score / len(posts[:10]) if posts else 0
            return {
                "type": "sentiment_update",
                "source": "reddit_crypto",
                "sentiment_score": avg_sentiment,
            }
    except Exception as e:
        print(f"Reddit fetch error: {e}")
    return None


async def gather_price_sources(symbols: List[str] = None) -> List[Dict[str, Any]]:
    """Concurrently fetch from multiple price and sentiment sources."""
    if symbols is None:
        symbols = ["BTC", "ETH"]
    
    tasks = []
    
    # Fetch crypto prices from CoinDesk
    for symbol in symbols:
        tasks.append(fetch_coindesk_price(symbol))
    
    # Fetch stock prices (if we have API key and symbol)
    if ALPHA_VANTAGE_KEY != "demo":
        tasks.append(fetch_alpha_vantage_price("AAPL"))
    
    # Fetch sentiment
    tasks.append(fetch_reddit_sentiment())
    
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
