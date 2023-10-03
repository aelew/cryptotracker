# CryptoTracker

[![Discord bot invite](https://img.shields.io/badge/bot-click_to_invite-brightgreen?logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=1132724830135922688&permissions=277025508352&scope=bot%20applications.commands)
![GitHub stars](https://img.shields.io/github/stars/aelew/cryptotracker)

🤖 A Discord bot that notifies users when their cryptocurrency transactions have confirmed.

## Features

- Pings you when a transaction reaches a specified number of confirmations
- Support for Bitcoin (BTC), Ethereum (ETH), and Litecoin (LTC)
- Usage of Discord interactions (application commands)
- Easy setup and installation

![Example](./images/example.png)

## Contributions

The development of CryptoTracker is an ongoing process, and everyone is welcome to contribute. Feel free to share your
ideas, report issues, and help make CryptoTracker even better!

## Run Locally

Clone the project

```bash
git clone https://github.com/aelew/cryptotracker.git
```

Go to the project directory

```bash
cd cryptotracker
```

Install dependencies

```bash
pip install -r requirements.txt
```

Set environment variables

```
To run this project, you need to set the required environment variables.
Copy `.env.example` into a new file called `.env` and fill in the values.
```

Start the bot

```bash
py main.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
