import asyncio
import httpx

async def fetch_from_example(api_url: str, params: dict | None = None):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(api_url, params=params)
        resp.raise_for_status()
        return resp.json()


async def gather_price_sources():
    # Placeholder: concurrently fetch from multiple sources
    apis = [
        "https://api.coindesk.com/v1/bpi/currentprice/BTC.json",
    ]
    tasks = [fetch_from_example(url) for url in apis]
    return await asyncio.gather(*tasks)
