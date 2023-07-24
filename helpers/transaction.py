from helpers.enums import Crypto


class Transaction:

    def __init__(self, id: str, crypto: Crypto, user_id: str, channel_id: str,
                 fee: int, required_confirmations: int):
        self.id = id
        self.crypto = crypto
        self.user_id = user_id
        self.channel_id = channel_id
        self.fee = fee
        self.required_confirmations = required_confirmations
