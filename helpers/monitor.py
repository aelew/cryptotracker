from interactions import Embed, EmbedField, RoleColors
from time import time

from helpers.shared import bot, btc_usd_rate, transaction_queue
from helpers.transaction import Transaction
from helpers.enums import Crypto
import helpers.btc as btc


async def check_transaction(tx: Transaction):
    global btc_usd_rate
    match tx.crypto:
        case Crypto.BTC.name:
            latest_block_height = await btc.get_latest_block_height()
            r = await btc.get_raw_tx(tx.id)

            # Calculate the number of confirmations using the latest block height and the block height of the transaction
            data = r.json()
            tx_block_height = data["block_height"]

            if tx_block_height:
                calc_conf = latest_block_height - tx_block_height + 1
                current_confirmations = max(0, min(calc_conf, 6))
            else:
                current_confirmations = 0

            # Whether the transaction has already reached the specified number of confirmations
            completed = current_confirmations >= tx.required_confirmations
            if not completed:
                return

            fee_in_usd = await btc.get_usd_rate() * (tx.fee / 1e8)

            # Create an embed to respond with
            embed = Embed(title=":warning:  Transaction confirmed",
                          color=RoleColors.GREEN)
            embed.add_fields(
                EmbedField(name="Transaction ID",
                           value=f"`{tx.id}`",
                           inline=False),
                EmbedField(name="Confirmations",
                           value=f"{current_confirmations}/6",
                           inline=True),
                EmbedField(name="Fee",
                           value=f"{tx.fee:,} sat (${fee_in_usd:,.2f})",
                           inline=True),
                EmbedField(name="Double-spent",
                           value=f"{'Yes' if data['double_spend'] else 'No'}",
                           inline=True),
                EmbedField(name="Block height",
                           value=f"{tx_block_height:,}",
                           inline=True),
                EmbedField(name="Confirmed at",
                           value=f"<t:{int(time())}>",
                           inline=True),
                EmbedField(name="Sent at",
                           value=f"<t:{data['time']}>",
                           inline=True),
            )

            print(
                f"Transaction confirmed (type: {tx.crypto} | txid: {tx.id} | confirmations: {current_confirmations})"
            )
            transaction_queue.remove(tx)

            channel = bot.get_channel(tx.channel_id)
            await channel.send(content=f"<@{tx.user_id}>", embed=embed)
        case _:
            print(f"Removing {tx.id} (unsupported cryptocurrency)")
