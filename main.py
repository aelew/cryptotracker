from interactions import listen, slash_command, Activity, ActivityType, Embed, EmbedField, OptionType, RoleColors, SlashContext, SlashCommandChoice, SlashCommandOption, Status
import os, re

from helpers.shared import bot, transaction_queue
from helpers.transaction import Transaction
from helpers.constants import TXID_PATTERN
from helpers.tasks import monitor_task
from helpers.enums import Crypto
import helpers.btc as btc


@listen()
async def on_ready():
    print(f"Established connection with gateway! Logged in as {bot.user}.")
    activity = Activity(type=ActivityType.WATCHING, name="your transactions")
    await bot.change_presence(Status.IDLE, activity)
    monitor_task.start()


@slash_command(
    name="track",
    description="Starts tracking a crypto transaction.",
    options=[
        SlashCommandOption(name="crypto",
                           description="The type of cryptocurrency used.",
                           type=OptionType.STRING,
                           required=True,
                           choices=[
                               SlashCommandChoice(name="Bitcoin (BTC)",
                                                  value="BTC"),
                               SlashCommandChoice(name="Ethereum (ETH)",
                                                  value="ETH"),
                               SlashCommandChoice(name="Litecoin (LTC)",
                                                  value="LTC")
                           ]),
        SlashCommandOption(name="txid",
                           description="The transaction ID to track.",
                           type=OptionType.STRING,
                           required=True),
        SlashCommandOption(
            name="confirmations",
            description="The number of confirmations to notify you after.",
            type=OptionType.INTEGER,
            required=False,
            min_value=0)
    ])
async def track_command(ctx: SlashContext,
                        crypto: Crypto,
                        txid: str,
                        confirmations: int = 1):
    await ctx.defer()

    if crypto == Crypto.BTC.name:
        if confirmations > 6:
            return await ctx.send("The maximum number of confirmations is 6.")

        txid = txid.lower()

        # If the user provided a link, attempt to extract the TXID from it
        if txid.startswith("http"):
            matches = re.findall(TXID_PATTERN, txid)
            if matches:
                txid = matches[0]

    match crypto:
        case Crypto.BTC.name:
            latest_block_height = btc.get_latest_block_height()
            r = btc.get_raw_tx(txid)
            if not r.is_success:
                description = "The specified transaction ID is invalid." if r.status_code == 404 else "The server returned an unexpected response."
                embed = Embed(title=":x:  An error occurred",
                              description=description,
                              color=RoleColors.RED)
                return await ctx.send(embed=embed)

            data = r.json()
            txid = data["hash"]

            # Fee in USD
            fee_in_usd = btc.get_usd_rate() * (data["fee"] / 1e8)

            tx_block_height = data["block_height"]
            if tx_block_height:
                # Calculate the number of confirmations using the latest block height and the block height of the transaction
                calc_conf = latest_block_height - tx_block_height + 1
                current_confirmations = max(0, min(calc_conf, 6))
            else:
                current_confirmations = 0

            # Whether the transaction has already reached the specified number of confirmations
            completed = current_confirmations >= confirmations

            # Create an embed to respond with
            embed = Embed(
                title=":information_source:  Transaction information",
                color=RoleColors.BLUE)
            embed.add_fields(
                EmbedField(name="Transaction ID",
                           value=f"`{txid}`",
                           inline=False),
                EmbedField(name="Confirmations",
                           value=f"{current_confirmations}/6",
                           inline=True),
                EmbedField(name="Fee",
                           value=f"{data['fee']:,} sat (${fee_in_usd:,.2f})",
                           inline=True),
                EmbedField(name="Double-spent",
                           value=f"{'Yes' if data['double_spend'] else 'No'}",
                           inline=True))

            # Check whether the transaction has already reached the specified number of confirmations
            if completed:
                embed.description = f"This transaction has already reached {confirmations} {'confirmation' if confirmations == 1 else 'confirmations'} [[view]](https://mempool.space/tx/{txid})."
            else:
                transaction = Transaction(id=txid,
                                          crypto=crypto,
                                          user_id=ctx.user.id,
                                          channel_id=ctx.channel_id,
                                          fee=data["fee"],
                                          required_confirmations=confirmations)
                transaction_queue.append(transaction)
                print(f"Transaction added (type: {crypto} | txid: {txid})")
                embed.description = f"You will be notified when this transaction reaches {confirmations} {'confirmation' if confirmations == 1 else 'confirmations'} [[view]](https://mempool.space/tx/{txid})."

            await ctx.send(embed=embed)
        case _:
            await ctx.send("This cryptocurrency has not been implemented yet!")


bot.start(os.getenv("DISCORD_BOT_TOKEN"))
