import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import TypedDict

import httpx
from cachetools import cached, TTLCache
from interactions import SlashContext

FeeDenomination = TypedDict("FeeDenomination", {"name": str, "decimal_digits": int, "conversion_rate": float})


class CoinSymbol(str, Enum):
    BTC = "BTC"
    LTC = "LTC"
    ETH = "ETH"


class Coin(ABC):

    def __init__(
            self,
            name: str,
            symbol: CoinSymbol,
            max_confirmations: int,
            txid_pattern: str,
            emoji: str,
            explorer_url: str,
            fee_denomination: FeeDenomination,
    ):
        self.name = name
        self.symbol = symbol
        self.max_confirmations = max_confirmations
        self.txid_pattern = re.compile(txid_pattern)
        self.emoji = emoji
        self.explorer_url = explorer_url
        self.fee_denomination = fee_denomination

    @abstractmethod
    def get_latest_block_height(self):
        """
        Retrieves the latest block height of the cryptocurrency.
        :return: The latest block height of the cryptocurrency.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_tx(self, txid: str):
        """
        Retrieves the transaction with the given transaction ID.
        :param txid: The transaction ID.
        :return: The transaction response.
        """
        raise NotImplementedError()

    @abstractmethod
    async def track(self, ctx: SlashContext, txid: str, required_confirmations: int):
        """
        Tracks the transaction with the given transaction ID.
        :param ctx: The application command interaction context.
        :param txid: The ID of the transaction to track.
        :param required_confirmations: The number of confirmations to notify after.
        """
        raise NotImplementedError()

    def get_current_confirmations(self, tx_block_height: int):
        """
        Calculates the number of confirmations using the latest block height and the block height of the transaction.
        :param tx_block_height: The block height of the transaction.
        :return: The number of confirmations the transaction has reached.
        """
        return max(0, self.get_latest_block_height() - tx_block_height + 1)

    @cached(cache=TTLCache(maxsize=50, ttl=5))
    def get_usd_rate(self) -> float:
        """
        Retrieves the current USD price of the cryptocurrency.
        :return: The last trade price of the cryptocurrency in USD.
        """
        ticker_symbol = self.symbol.name + "-USD"
        r = httpx.get(f"https://api.blockchain.com/v3/exchange/tickers/{ticker_symbol}")
        if not r.is_success:
            raise Exception(f"Failed to retrieve current {ticker_symbol} price")
        return r.json()["last_trade_price"]

    def get_explorer_url(self, txid: str):
        """
        Retrieves the URL of the transaction on a blockchain explorer.
        :param txid: The transaction ID.
        :return: The URL of the transaction on a blockchain explorer.
        """
        return self.explorer_url.format(id=txid)

    def get_formatted_url(self, txid: str):
        return f"[[view]]({self.get_explorer_url(txid)})"

    def get_formatted_confirmations(self, current_confirmations: int):
        """
        Formats the current number of confirmations for display.
        :param current_confirmations: The current number of confirmations.
        :return: The formatted number of confirmations.
        """
        return f"{current_confirmations:,}" \
            if current_confirmations > self.max_confirmations \
            else f"{current_confirmations}/{self.max_confirmations}"

    def get_formatted_fee(self, tx_fee: int):
        """
        Formats the transaction fee for display.
        :param tx_fee: The transaction fee.
        :return: The formatted transaction fee.
        """
        tx_fee_display = f"{tx_fee:,.15f}".rstrip('0').rstrip('.')
        usd_fee = self.get_usd_rate() * (tx_fee / self.fee_denomination["conversion_rate"])
        return f"{tx_fee_display} {self.fee_denomination['name']} " \
               f"(${usd_fee:,.{self.fee_denomination['decimal_digits']}f})"
