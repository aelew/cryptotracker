import os
import re

from interactions import (listen, slash_command, Activity, ActivityType, OptionType, SlashContext, SlashCommandChoice,
                          SlashCommandOption, Status)

from crypto import *
from crypto.base import CoinSymbol
from helpers.shared import bot
from helpers.tasks import monitor_task

coins = {
    CoinSymbol.BTC: Bitcoin(),
    CoinSymbol.LTC: Litecoin(),
    CoinSymbol.ETH: Ethereum()
}

rates: dict[CoinSymbol, float] = {
    CoinSymbol.BTC: 0,
    CoinSymbol.LTC: 0,
    CoinSymbol.ETH: 0
}


@listen()
async def on_ready():
    """
    Called when the bot is ready to start receiving events.
    """
    print(f"Established connection with gateway! Logged in as {bot.user}.")
    activity = Activity(type=ActivityType.WATCHING, name="your transactions")
    await bot.change_presence(Status.IDLE, activity)
    monitor_task.start()


@slash_command(
    name="track",
    description="Starts tracking a crypto transaction.",
    options=[
        SlashCommandOption(
            type=OptionType.STRING,
            required=True,
            name="coin",
            description="The cryptocurrency coin used.",
            choices=[
                SlashCommandChoice(name=f"{coin.name} ({coin.symbol.name})", value=coin.symbol)
                for coin in coins.values()
            ]
        ),
        SlashCommandOption(
            type=OptionType.STRING,
            required=True,
            name="txid",
            description="The ID of the transaction you want to track."
        ),
        SlashCommandOption(
            type=OptionType.INTEGER,
            required=False,
            name="confirmations",
            description="The number of confirmations to notify you after.",
            min_value=1
        )
    ]
)
async def track_command(ctx: SlashContext, coin: CoinSymbol, txid: str, confirmations: int = 1):
    """
    Called when a user uses the /track command.
    :param ctx: The application command interaction context.
    :param coin: The symbol of the cryptocurrency coin used.
    :param txid: The ID of the transaction to track.
    :param confirmations: The number of confirmations to notify after.
    """
    crypto = coins.get(coin)
    if confirmations > crypto.max_confirmations:
        return await ctx.send(f"The maximum number of confirmations for "
                              f"**{crypto.name}** is **{crypto.max_confirmations}**.")

    txid = txid.lower()

    # If the user provided a link, attempt to extract the TXID from it
    if txid.startswith("http"):
        matches = re.findall(crypto.txid_pattern, txid)
        if matches:
            txid = matches[0]

    # Defer the response to avoid timing out
    await ctx.defer()
    await crypto.track(ctx, txid, confirmations)


# Start the Discord bot
bot.start(os.getenv("DISCORD_BOT_TOKEN"))
