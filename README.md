# CryptoTracker

![Discord server invite](https://img.shields.io/discord/1132807338961686538?logo=discord&logoColor=white&label=community&color=%235865F2&cacheSeconds=300&link=https%3A%2F%2Fdiscord.gg%2FdCNthcSrkS)
![Discord bot invite](https://img.shields.io/badge/bot-click_to_invite-brightgreen?logo=discord&logoColor=white&link=https%3A%2F%2Fdiscord.com%2Fapi%2Foauth2%2Fauthorize%3Fclient_id%3D1132724830135922688%26permissions%3D277025508352%26scope%3Dbot%2520applications.commands)
![GitHub stars](https://img.shields.io/github/stars/aelew/cryptotracker)

🤖 A Discord bot that notifies users when their cryptocurrency transaction has confirmed.

## Features

- Pings you when a transaction reaches a specified number of confirmations
- Support for Bitcoin (BTC), Ethereum (ETH), and Litecoin (LTC)
- Usage of Discord interactions (application commands)
- Easy setup and installation

![Example](./images/example.png)

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
  To run this project, you will need to set the required environment variables.
  These can be found in the `.env.example` file.
```

Start the bot

```bash
  py main.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
