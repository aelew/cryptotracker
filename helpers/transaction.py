from interactions import Snowflake

from crypto.base import Coin


class Transaction:

    def __init__(
            self,
            coin: Coin,
            id: str,
            user_id: Snowflake,
            channel_id: Snowflake,
            fee: int,
            required_confirmations: int
    ):
        """
        Represents a cryptocurrency transaction.
        :param id: The transaction ID.
        :param coin: The cryptocurrency coin used in the transaction.
        :param user_id: The ID of the user who started the transaction.
        :param channel_id: The ID of the channel the transaction was started in.
        :param fee: The fee of the transaction.
        :param required_confirmations: The number of confirmations to notify after.
        """
        self.coin = coin
        self.id = id
        self.user_id = user_id
        self.channel_id = channel_id
        self.fee = fee
        self.required_confirmations = required_confirmations
