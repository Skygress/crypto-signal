# Crypto Signal Hunter 🚀

A Telegram bot that provides real-time cryptocurrency price tracking, technical analysis, and trading signals.

## Features

✅ **Price Tracking** - Check prices for top cryptocurrencies
✅ **Trading Signals** - BUY/SELL signals with confidence levels
✅ **Technical Analysis** - RSI, Moving Averages, Bollinger Bands
✅ **Watchlist** - Track your favorite cryptocurrencies
✅ **100% Telegram Compliant** - No API usage

## Supported Cryptocurrencies

- BTC (Bitcoin)
- ETH (Ethereum)
- BNB (Binance Coin)
- SOL (Solana)
- XRP (Ripple)
- ADA (Cardano)
- DOT (Polkadot)
- DOGE (Dogecoin)

## Deployment on Railway

### Step 1: Create Telegram Bot
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Name it **CryptoSignalHunter**
4. Copy the token

### Step 2: Deploy on Railway
1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Add environment variable:
   - Key: `BOT_TOKEN`
   - Value: Your bot token from @BotFather
5. Click "Deploy"

### Step 3: Test Your Bot
1. Open your bot on Telegram
2. Send `/start`
3. Test commands

## Commands

- `/start` - Start the bot
- `/price [symbol]` - Get current price
- `/signal [symbol]` - Get trading signals
- `/analyze [symbol]` - Get technical analysis
- `/watchlist` - Manage watchlist
- `/help` - Show help
- `/about` - About the bot

## Disclaimer

⚠️ This bot is for educational purposes only. Cryptocurrency trading involves substantial risk. Always do your own research before making trading decisions.

## License

MIT License
