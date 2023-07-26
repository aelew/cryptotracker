import httpx
from interactions import SlashContext, EmbedField

from helpers.embeds import send_invalid_tx_embed, send_tx_info_embed
from helpers.shared import queue_transaction
from helpers.transaction import Transaction
from .base import Coin, CoinSymbol, FeeDenomination


class Litecoin(Coin):
    def __init__(self):
        super(Litecoin, self).__init__(
            name="Litecoin",
            symbol=CoinSymbol.LTC,
            max_confirmations=24,
            txid_pattern=r"[0-9a-f]{64}$",
            emoji="<:btc:1133213000304697495>",
            explorer_url="https://blockchair.com/litecoin/transaction/{id}",
            fee_denomination=FeeDenomination(name="lit", decimal_digits=7, conversion_rate=1e8)
        )

    def get_latest_block_height(self):
        r = httpx.get("https://litecoinspace.org/api/v1/blocks/tip/height")
        if not r.is_success:
            raise Exception("Failed to retrieve latest LTC block height")
        return int(r.text)

    def get_tx(self, txid: str):
        return httpx.get("https://litecoinspace.org/api/tx/" + txid)

    async def track(self, ctx: SlashContext, txid: str, required_confirmations: int):
        response = self.get_tx(txid)
        if not response.is_success:
            return await send_invalid_tx_embed(ctx, response.status_code)

        data = response.json()
        txid = data["txid"]

        current_confirmations = self.get_current_confirmations(data["status"]["block_height"]) \
            if data["status"]["confirmed"] \
            else 0
        formatted_confirmations = self.get_formatted_confirmations(current_confirmations)

        tx = Transaction(self, txid, ctx.user.id, ctx.channel_id, data["fee"], required_confirmations)

        # Queue the transaction if it hasn't already reached the required number of confirmations
        if current_confirmations < required_confirmations:
            queue_transaction(tx)

        await send_tx_info_embed(ctx, tx, current_confirmations, [
            EmbedField(name="Transaction ID", value=f"`{txid}`", inline=False),
            EmbedField(name="Confirmations", value=formatted_confirmations, inline=True),
            EmbedField(name="Fee", value=self.get_formatted_fee(data['fee']), inline=True),
            EmbedField(name="Size", value=f"{data['size']:,} vB", inline=True)
        ])
