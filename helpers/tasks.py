import asyncio
from time import time

from interactions import IntervalTrigger, Task, EmbedField

from crypto.base import CoinSymbol
from helpers.embeds import send_tx_confirmed_embed
from helpers.shared import tx_queue, remove_transaction
from helpers.transaction import Transaction

# Use a semaphore to limit the number of simultaneous requests sent
semaphore = asyncio.Semaphore(5)


@Task.create(IntervalTrigger(seconds=10))
async def monitor_task():
    """
    Monitors transactions in the transaction queue. Runs every 10 seconds.
    """
    async with semaphore:
        tasks = [
            asyncio.ensure_future(monitor(tx))
            for tx in tx_queue
        ]
        await asyncio.gather(*tasks)


async def monitor(tx: Transaction):
    """
    Monitors a transaction.
    :param tx: The transaction to monitor
    """
    match tx.coin.symbol:
        case CoinSymbol.BTC:
            data = tx.coin.get_tx(tx.id).json()

            tx_block_height = data["block_height"]
            current_confirmations = tx.coin.get_current_confirmations(tx_block_height) if tx_block_height else 0

            # The transaction hasn't reached the required number of confirmations yet
            if current_confirmations < tx.required_confirmations:
                return

            formatted_confirmations = tx.coin.get_formatted_confirmations(current_confirmations)
            formatted_fee = tx.coin.get_formatted_fee(tx.fee)
            remove_transaction(tx)

            await send_tx_confirmed_embed(tx, [
                EmbedField(name="Transaction ID", value=f"`{tx.id}`", inline=False),
                EmbedField(name="Confirmations", value=formatted_confirmations, inline=True),
                EmbedField(name="Fee", value=formatted_fee, inline=True),
                EmbedField(name="Double-spent", value=f"{'Yes' if data['double_spend'] else 'No'}", inline=True),
                EmbedField(name="Block height", value=f"{tx_block_height:,}", inline=True),
                EmbedField(name="Confirmed at", value=f"<t:{int(time())}>", inline=True),
                EmbedField(name="Sent at", value=f"<t:{data['time']}>", inline=True)
            ])
        case CoinSymbol.LTC:
            data = tx.coin.get_tx(tx.id).json()

            current_confirmations = tx.coin.get_current_confirmations(data["status"]["block_height"]) \
                if data["status"]["confirmed"] \
                else 0

            # The transaction hasn't reached the required number of confirmations yet
            if current_confirmations < tx.required_confirmations:
                return

            tx_block_height = data["status"]["block_height"]

            formatted_confirmations = tx.coin.get_formatted_confirmations(current_confirmations)
            formatted_fee = tx.coin.get_formatted_fee(tx.fee)
            remove_transaction(tx)

            await send_tx_confirmed_embed(tx, [
                EmbedField(name="Transaction ID", value=f"`{tx.id}`", inline=False),
                EmbedField(name="Confirmations", value=formatted_confirmations, inline=True),
                EmbedField(name="Fee", value=formatted_fee, inline=True),
                EmbedField(name="Block height", value=f"{tx_block_height:,}", inline=True),
                EmbedField(name="Size", value=f"{data['size']:,} vB", inline=True),
                EmbedField(name="Weight", value=f"{data['weight']:,} WU", inline=True),
                EmbedField(name="Confirmed at", value=f"<t:{int(time())}>", inline=True)
            ])
        case CoinSymbol.ETH:
            data = tx.coin.get_tx(tx.id)

            current_confirmations = tx.coin.get_current_confirmations(
                data.blockNumber) if data.blockNumber is not None else 0

            # The transaction hasn't reached the required number of confirmations yet
            if current_confirmations < tx.required_confirmations:
                return

            # convert gas price from wei to ETH
            eth_gas_price = data.gasPrice / 1e18
            # tx fee (ETH) = gas price * gas used by tx
            fee = data.gas * eth_gas_price

            # convert tx value from wei to ETH
            eth_value = data.value / 1e18
            usd_amount = tx.coin.get_usd_rate() * eth_value

            formatted_confirmations = tx.coin.get_formatted_confirmations(current_confirmations)
            remove_transaction(tx)

            await send_tx_confirmed_embed(tx, [
                EmbedField(name="Transaction ID", value=f"`{tx.id}`", inline=False),
                EmbedField(name="Confirmations", value=formatted_confirmations, inline=True),
                EmbedField(name="Fee", value=tx.coin.get_formatted_fee(fee), inline=True),
                EmbedField(name="Value", value=f"${usd_amount:,.2f}", inline=True),
                EmbedField(name="Block number", value=f"{data.blockNumber:,}", inline=True),
                EmbedField(name="Nonce", value=f"{data.nonce:,}", inline=True),
                EmbedField(name="Confirmed at", value=f"<t:{int(time())}>", inline=True)
            ])
