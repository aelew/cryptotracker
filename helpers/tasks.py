from interactions import IntervalTrigger, Task
import asyncio

from helpers.monitor import check_transaction
from helpers.shared import transaction_queue
import helpers.btc as btc

# Limit Semaphore to prevent rate limiting
sem = asyncio.Semaphore(5)


@Task.create(IntervalTrigger(seconds=10))
async def monitor_task():
    global btc_usd_rate
    btc_usd_rate = await btc.get_usd_rate()

    async with sem:
        tasks = [
            asyncio.ensure_future(check_transaction(tx))
            for tx in transaction_queue
        ]
        await asyncio.gather(*tasks)
