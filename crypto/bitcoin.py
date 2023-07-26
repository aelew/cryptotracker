import httpx
from interactions import SlashContext, EmbedField

from helpers.embeds import send_invalid_tx_embed, send_tx_info_embed
from helpers.shared import queue_transaction
from helpers.transaction import Transaction
from .base import Coin, CoinSymbol, FeeDenomination


class Bitcoin(Coin):
    def __init__(self):
        super(Bitcoin, self).__init__(
            name="Bitcoin",
            symbol=CoinSymbol.BTC,
            max_confirmations=6,
            txid_pattern=r"[0-9a-f]{64}$",
            emoji="<:btc:1133213003655942145>",
            explorer_url="https://mempool.space/tx/{id}",
            fee_denomination=FeeDenomination(name="sat", decimal_digits=2, conversion_rate=1e8)
        )

    def get_latest_block_height(self):
        r = httpx.get("https://mempool.space/api/v1/blocks/tip/height")
        if not r.is_success:
            raise Exception("Failed to retrieve latest BTC block height")
        return int(r.text)

    def get_tx(self, txid: str):
        return httpx.get("https://blockchain.info/rawtx/" + txid)

    async def track(self, ctx: SlashContext, txid: str, required_confirmations: int):
        response = self.get_tx(txid)
        if not response.is_success:
            return await send_invalid_tx_embed(ctx, response.status_code)

        data = response.json()
        txid = data["hash"]

        tx_block_height = data["block_height"]
        current_confirmations = self.get_current_confirmations(tx_block_height) if tx_block_height else 0
        formatted_confirmations = self.get_formatted_confirmations(current_confirmations)

        tx = Transaction(self, txid, ctx.user.id, ctx.channel_id, data["fee"], required_confirmations)

        # Queue the transaction if it hasn't already reached the required number of confirmations
        if current_confirmations < required_confirmations:
            queue_transaction(tx)

        await send_tx_info_embed(ctx, tx, current_confirmations, [
            EmbedField(name="Transaction ID", value=f"`{txid}`", inline=False),
            EmbedField(name="Confirmations", value=formatted_confirmations, inline=True),
            EmbedField(name="Fee", value=self.get_formatted_fee(data['fee']), inline=True),
            EmbedField(name="Double-spent", value=f"{'Yes' if data['double_spend'] else 'No'}", inline=True)
        ])
