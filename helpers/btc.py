import httpx


async def get_latest_block_height():
    async with httpx.AsyncClient(http2=True) as client:
        r = await client.get("https://mempool.space/api/v1/blocks/tip/height")
        if not r.is_success:
            raise Exception("Failed to retrieve latest block height")
        return int(r.text)


async def get_raw_tx(txid: str):
    async with httpx.AsyncClient(http2=True) as client:
        return await client.get("https://blockchain.info/rawtx/" + txid)


async def get_usd_rate():
    async with httpx.AsyncClient(http2=True) as client:
        r = await client.get(
            "https://api.blockchain.com/v3/exchange/tickers/BTC-USD")
        if not r.is_success:
            raise Exception("Failed to retrieve BTC-USD rate")
        return r.json()["last_trade_price"]
