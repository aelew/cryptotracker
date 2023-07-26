import os

from eth_typing import HexStr
from interactions import SlashContext, EmbedField
from web3 import Web3
from web3.exceptions import TransactionNotFound
from web3.types import TxData

from helpers.embeds import send_invalid_tx_embed, send_tx_info_embed
from helpers.shared import queue_transaction
from helpers.transaction import Transaction
from .base import Coin, CoinSymbol, FeeDenomination


class Ethereum(Coin):
    def __init__(self):
        super(Ethereum, self).__init__(
            name="Ethereum",
            symbol=CoinSymbol.ETH,
            max_confirmations=50,
            txid_pattern=r"^0x([a-f0-9]{64})$",
            emoji="<:eth:1133213001529434122>",
            explorer_url="https://etherscan.io/tx/{id}",
            fee_denomination=FeeDenomination(name="ETH", decimal_digits=2, conversion_rate=1)
        )
        self.eth = Web3(Web3.HTTPProvider(os.getenv("QUICKNODE_HTTP_PROVIDER"))).eth

    def get_latest_block_height(self):
        return self.eth.block_number

    def get_tx(self, txid: str) -> TxData:
        try:
            return self.eth.get_transaction(HexStr(txid))
        except (ValueError, TransactionNotFound):
            return None

    async def track(self, ctx: SlashContext, txid: str, required_confirmations: int):
        data = self.get_tx(txid)
        if not data:
            return await send_invalid_tx_embed(ctx)

        txid = data.hash.hex()

        # convert gas price from wei to ETH
        eth_gas_price = data.gasPrice / 1e18
        # tx fee (ETH) = gas price * gas used by tx
        fee = data.gas * eth_gas_price

        # convert tx value from wei to ETH
        eth_value = data.value / 1e18
        usd_amount = self.get_usd_rate() * eth_value

        current_confirmations = self.get_current_confirmations(data.blockNumber) if data.blockNumber is not None else 0
        formatted_confirmations = self.get_formatted_confirmations(current_confirmations)

        tx = Transaction(self, txid, ctx.user.id, ctx.channel_id, data.gasPrice, required_confirmations)

        # Queue the transaction if it hasn't already reached the required number of confirmations
        if current_confirmations < required_confirmations:
            queue_transaction(tx)

        await send_tx_info_embed(ctx, tx, current_confirmations, [
            EmbedField(name="Transaction ID", value=f"`{txid}`", inline=False),
            EmbedField(name="Confirmations", value=formatted_confirmations, inline=True),
            EmbedField(name="Fee", value=self.get_formatted_fee(fee), inline=True),
            EmbedField(name="Value", value=f"${usd_amount:,.2f}", inline=True)
        ])
