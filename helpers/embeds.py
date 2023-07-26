from interactions import Embed, SlashContext, RoleColors, EmbedField

from helpers.shared import bot
from helpers.transaction import Transaction


async def send_invalid_tx_embed(ctx: SlashContext, status_code=404):
    """
    Sends an embed indicating an error with a transaction.
    :param ctx: The application command interaction context.
    :param status_code: The status code of the response.
    """
    embed = Embed(
        color=RoleColors.RED,
        title=":x: An error occurred",
        description=
        "The specified transaction ID is invalid."
        if status_code == 400 or status_code == 404
        else "The server returned an unexpected response."
    )
    await ctx.send(embed=embed)


async def send_tx_info_embed(ctx: SlashContext, tx: Transaction, current_confirmations: int, fields: list[EmbedField]):
    """
    Sends an embed containing information about a transaction.
    :param ctx: The application command interaction context.
    :param tx: The transaction to send the embed for.
    :param current_confirmations: The number of confirmations the transaction has reached.
    :param fields: The fields to add to the embed.
    """
    view_link = tx.coin.get_formatted_url(tx.id)

    # Check whether the transaction has already reached the required number of confirmations
    if current_confirmations >= tx.required_confirmations:
        description = f"{tx.coin.emoji} This transaction has already reached {tx.required_confirmations} " \
                      f"{'confirmation' if tx.required_confirmations == 1 else 'confirmations'} {view_link}."
    else:
        description = f"{tx.coin.emoji} You will be notified when this " \
                      f"transaction reaches {tx.required_confirmations} " \
                      f"{'confirmation' if tx.required_confirmations == 1 else 'confirmations'} {view_link}."

    embed = Embed(":information_source: Transaction information", description, RoleColors.BLUE)
    embed.add_fields(*fields)
    await ctx.send(embed=embed)


async def send_tx_confirmed_embed(tx: Transaction, fields: list[EmbedField]):
    """
    Sends an embed notifying the user that their transaction has confirmed.
    :param tx: The transaction to send the embed for.
    :param fields: The fields to add to the embed.
    """
    view_link = tx.coin.get_formatted_url(tx.id)

    embed = Embed(":white_check_mark: Transaction confirmed",
                  f"{tx.coin.emoji} Your transaction has reached {tx.required_confirmations} "
                  f"{'confirmation' if tx.required_confirmations == 1 else 'confirmations'} {view_link}.",
                  RoleColors.GREEN)
    embed.add_fields(*fields)
    channel = bot.get_channel(tx.channel_id)
    await channel.send(content=f"<@{tx.user_id}>", embed=embed)
