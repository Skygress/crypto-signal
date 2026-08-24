# Telegram Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather

# Supported Cryptocurrencies (symbol, name, pair)
CRYPTO_PAIRS = {
    'BTC': {'name': 'Bitcoin', 'symbol': 'BTC', 'pair': 'BTCUSDT'},
    'ETH': {'name': 'Ethereum', 'symbol': 'ETH', 'pair': 'ETHUSDT'},
    'BNB': {'name': 'Binance Coin', 'symbol': 'BNB', 'pair': 'BNBUSDT'},
    'SOL': {'name': 'Solana', 'symbol': 'SOL', 'pair': 'SOLUSDT'},
    'XRP': {'name': 'Ripple', 'symbol': 'XRP', 'pair': 'XRPUSDT'},
    'ADA': {'name': 'Cardano', 'symbol': 'ADA', 'pair': 'ADAUSDT'},
    'DOT': {'name': 'Polkadot', 'symbol': 'DOT', 'pair': 'DOTUSDT'},
    'DOGE': {'name': 'Dogecoin', 'symbol': 'DOGE', 'pair': 'DOGEUSDT'}
}

# Timeframes
TIMEFRAMES = {
    '1m': {'label': '1 Minute', 'seconds': 60},
    '5m': {'label': '5 Minutes', 'seconds': 300},
    '15m': {'label': '15 Minutes', 'seconds': 900},
    '1h': {'label': '1 Hour', 'seconds': 3600},
    '4h': {'label': '4 Hours', 'seconds': 14400},
    '1d': {'label': '1 Day', 'seconds': 86400}
}

# Admin IDs (for bot management)
ADMIN_IDS = []  # Add your Telegram user IDs

# Channel/Group where bot will post signals (optional)
PUBLIC_CHANNEL = ""  # @yourchannel

# Bot Settings
SIGNAL_INTERVAL = 300  # Check for signals every 5 minutes
MAX_HISTORY = 100  # Max price history to keep

# Website sources for scraping (no API needed)
TICKER_SOURCES = [
    'https://www.binance.com/en/trade/',
    'https://www.coingecko.com/en/coins/',
    'https://coinmarketcap.com/currencies/'
]
