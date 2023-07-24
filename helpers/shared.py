from helpers.transaction import Transaction
from interactions import Client, Intents
from dotenv import load_dotenv
from collections import deque

load_dotenv()

# This is here to prevent circular imports
bot = Client(intents=Intents.DEFAULT)

transaction_queue: deque[Transaction] = deque()
btc_usd_rate = 0
