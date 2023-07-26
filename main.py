import os
import re
from typing import Annotated

from interactions import (listen, slash_command, Activity, ActivityType, OptionType, SlashContext, SlashCommandChoice,
                          SlashCommandOption, Status, Embed, RoleColors, EmbedField, Timestamp)

from crypto import *
from crypto.base import CoinSymbol
from helpers.converters import LowerConverter
from helpers.shared import bot
from helpers.tasks import monitor_task

coins = {
    CoinSymbol.BTC: Bitcoin(),
    CoinSymbol.LTC: Litecoin(),
    CoinSymbol.ETH: Ethereum()
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
async def track_command(ctx: SlashContext, coin: CoinSymbol, txid: Annotated[str, LowerConverter],
                        confirmations=1):
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

    # If the user provided a link, attempt to extract the TXID from it
    if txid.startswith("http"):
        matches = re.findall(crypto.txid_pattern, txid)
        if matches:
            txid = matches[0]

    # Defer the response to avoid timing out
    await ctx.defer()
    await crypto.track(ctx, txid, confirmations)


@slash_command(name="prices", description="Displays the prices of top cryptocurrencies.")
async def prices_command(ctx: SlashContext):
    """
    Called when a user uses the /prices command.
    :param ctx: The application command interaction context.
    """
    await ctx.defer()

    embed = Embed(title=":coin: Cryptocurrency Prices", color=RoleColors.YELLOW, timestamp=Timestamp.now())
    embed.add_fields(*[
        EmbedField(
            name=f"{coin.name} ({coin.symbol.name})",
            value=f"{coin.emoji} ${coin.get_usd_rate():,.2f} USD",
            inline=True
        )
        for coin in coins.values()
    ])

    await ctx.send(embed=embed)


@slash_command(name="help", description="Displays information about the bot.")
async def help_command(ctx: SlashContext):
    """
    Called when a user uses the /help command.
    :param ctx: The application command interaction context.
    """
    embed = Embed(
        title=":coin: CryptoTracker Help",
        description="<:github:1133138264270831616> [This bot is open-source!](https://github.com/aelew/cryptotracker)",
        color=RoleColors.BLUE,
        timestamp=Timestamp.now()
    )
    embed.add_field(
        name=":tools: Commands",
        value="\n".join([
            f"`/{command.resolved_name}` • {command.description}"
            for command in bot.application_commands
        ])
    )

    await ctx.send(embed=embed)


# Start the Discord bot
bot.start(os.getenv("DISCORD_BOT_TOKEN"))
