import httpx


def get_latest_block_height():
    r = httpx.get("https://mempool.space/api/v1/blocks/tip/height")
    if not r.is_success:
        raise Exception("Failed to retrieve latest block height")
    return int(r.text)


def get_raw_tx(txid: str):
    return httpx.get("https://blockchain.info/rawtx/" + txid)


def get_usd_rate():
    r = httpx.get("https://api.blockchain.com/v3/exchange/tickers/BTC-USD")
    if not r.is_success:
        raise Exception("Failed to retrieve BTC-USD rate")
    return r.json()["last_trade_price"]
