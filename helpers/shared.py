from collections import deque

from dotenv import load_dotenv
from interactions import Client, Intents

from helpers.transaction import Transaction

load_dotenv()

bot = Client(intents=Intents.DEFAULT)
tx_queue: deque[Transaction] = deque()


def queue_transaction(tx: Transaction):
    """
    Adds a transaction to the queue.
    :param tx: The transaction to add.
    """
    tx_queue.append(tx)
    print(f"[+] TX (type: {tx.coin.symbol.name} | hash: {tx.id})")


def remove_transaction(tx: Transaction):
    """
    Removes a transaction from the queue.
    :param tx: The transaction to remove.
    """
    tx_queue.remove(tx)
    print(f"[-] TX (type: {tx.coin.symbol.name} | hash: {tx.id} | conf: {tx.required_confirmations})")
