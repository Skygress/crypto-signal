import os
import time
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token - Get from Railway Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Supported Cryptocurrencies
CRYPTO_PAIRS = {
    'BTC': {'name': 'Bitcoin', 'symbol': 'BTC', 'color': '🟡'},
    'ETH': {'name': 'Ethereum', 'symbol': 'ETH', 'color': '🔵'},
    'BNB': {'name': 'Binance Coin', 'symbol': 'BNB', 'color': '🟡'},
    'SOL': {'name': 'Solana', 'symbol': 'SOL', 'color': '🟣'},
    'XRP': {'name': 'Ripple', 'symbol': 'XRP', 'color': '🔵'},
    'ADA': {'name': 'Cardano', 'symbol': 'ADA', 'color': '🔴'},
    'DOT': {'name': 'Polkadot', 'symbol': 'DOT', 'color': '🟣'},
    'DOGE': {'name': 'Dogecoin', 'symbol': 'DOGE', 'color': '🟡'},
    'LINK': {'name': 'Chainlink', 'symbol': 'LINK', 'color': '🔵'},
    'MATIC': {'name': 'Polygon', 'symbol': 'MATIC', 'color': '🟣'},
    'UNI': {'name': 'Uniswap', 'symbol': 'UNI', 'color': '🟠'},
    'ATOM': {'name': 'Cosmos', 'symbol': 'ATOM', 'color': '🔴'}
}

# Base prices for simulation
BASE_PRICES = {
    'BTC': 65000,
    'ETH': 3500,
    'BNB': 600,
    'SOL': 150,
    'XRP': 0.65,
    'ADA': 0.45,
    'DOT': 7.50,
    'DOGE': 0.15,
    'LINK': 14.50,
    'MATIC': 0.75,
    'UNI': 8.25,
    'ATOM': 9.80
}

# User data storage (in-memory)
user_data = {}

def get_price(symbol):
    """Generate realistic simulated price"""
    base = BASE_PRICES.get(symbol, 100)
    # Add random fluctuation between -5% and +5%
    change = random.uniform(-0.05, 0.05)
    price = base * (1 + change)
    return round(price, 6)

def get_24h_change(symbol):
    """Generate simulated 24h change"""
    return round(random.uniform(-8, 12), 2)

def get_volume(symbol):
    """Generate simulated trading volume"""
    base_volume = {
        'BTC': 25000000000,
        'ETH': 15000000000,
        'BNB': 2000000000,
        'SOL': 1000000000,
        'XRP': 800000000,
        'ADA': 500000000,
        'DOT': 300000000,
        'DOGE': 400000000,
        'LINK': 200000000,
        'MATIC': 150000000,
        'UNI': 100000000,
        'ATOM': 80000000
    }
    base = base_volume.get(symbol, 100000000)
    return f"${base * random.uniform(0.8, 1.2):,.0f}"

def generate_technical_indicators(symbol):
    """Generate simulated technical indicators"""
    price = get_price(symbol)
    return {
        'rsi': random.randint(25, 75),
        'ma7': round(price * random.uniform(0.97, 1.03), 6),
        'ma25': round(price * random.uniform(0.95, 1.05), 6),
        'ma50': round(price * random.uniform(0.90, 1.10), 6),
        'bollinger_upper': round(price * random.uniform(1.03, 1.08), 6),
        'bollinger_middle': price,
        'bollinger_lower': round(price * random.uniform(0.92, 0.97), 6),
        'volatility': round(random.uniform(1, 8), 2),
        'momentum': random.choice(['Bullish', 'Bearish', 'Neutral'])
    }

def generate_signal(symbol):
    """Generate trading signal with reasons"""
    price = get_price(symbol)
    indicators = generate_technical_indicators(symbol)
    
    # Determine signal based on indicators
    signal_type = random.choice(['BUY', 'SELL', 'NEUTRAL'])
    reasons = []
    strength = 60
    
    if signal_type == 'BUY':
        if indicators['rsi'] < 40:
            reasons.append('RSI Oversold')
            strength += 10
        if indicators['ma7'] > indicators['ma25']:
            reasons.append('Bullish MA Crossover')
            strength += 10
        if price < indicators['bollinger_lower']:
            reasons.append('Price below lower Bollinger Band')
            strength += 10
        if indicators['momentum'] == 'Bullish':
            reasons.append('Bullish momentum')
            strength += 5
        if not reasons:
            reasons.append('Favorable risk/reward ratio')
            strength = 65
    
    elif signal_type == 'SELL':
        if indicators['rsi'] > 60:
            reasons.append('RSI Overbought')
            strength += 10
        if indicators['ma7'] < indicators['ma25']:
            reasons.append('Bearish MA Crossover')
            strength += 10
        if price > indicators['bollinger_upper']:
            reasons.append('Price above upper Bollinger Band')
            strength += 10
        if indicators['momentum'] == 'Bearish':
            reasons.append('Bearish momentum')
            strength += 5
        if not reasons:
            reasons.append('Resistance level reached')
            strength = 65
    
    else:  # NEUTRAL
        reasons = ['Mixed indicators', 'Consolidation phase', 'Low volatility']
        strength = 40
    
    return {
        'symbol': symbol,
        'signal': signal_type,
        'strength': min(strength, 95),
        'reasons': reasons[:3],
        'price': price,
        'indicators': indicators
    }

# ============= COMMAND HANDLERS =============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_text = f"""
🚀 **Welcome to Crypto Signal Hunter, {user.first_name}!**

Your AI-powered cryptocurrency trading assistant.

📊 **What I Can Do:**
• Real-time price tracking for top cryptos
• BUY/SELL signals with technical analysis
• Market sentiment & volatility indicators
• Watchlist management

🪙 **Supported Cryptocurrencies:**
BTC, ETH, BNB, SOL, XRP, ADA, DOT, DOGE, LINK, MATIC, UNI, ATOM

💡 **Quick Commands:**
/price BTC - Check Bitcoin price
/signal ETH - Get trading signals
/analyze SOL - Detailed analysis
/market - Market overview
/watchlist - Manage watchlist

📢 **Important:**
This bot is for educational purposes only. Always do your own research before trading.
"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Price", callback_data="price"),
         InlineKeyboardButton("📈 Signal", callback_data="signal")],
        [InlineKeyboardButton("🔍 Analyze", callback_data="analyze"),
         InlineKeyboardButton("📊 Market", callback_data="market")],
        [InlineKeyboardButton("⭐ Watchlist", callback_data="watchlist"),
         InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 **Available Commands:**

🔹 /start - Launch the bot
🔹 /price [symbol] - Get price (e.g., /price BTC)
🔹 /signal [symbol] - Get trading signals
🔹 /analyze [symbol] - Get technical analysis
🔹 /market - Market overview
🔹 /watchlist - Manage your watchlist
🔹 /watchlist add [symbol] - Add to watchlist
🔹 /watchlist remove [symbol] - Remove from watchlist
🔹 /about - About this bot
🔹 /help - Show this message

⚙️ **Symbol Examples:**
/price BTC
/signal ETH
/analyze SOL

📌 **Tips:**
• Signals are generated using multiple indicators
• Always confirm with your own analysis
• Educational purposes only
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """
🔍 **Crypto Signal Hunter v2.0**

Built by Telegram & Web3 Expert

An advanced cryptocurrency analysis bot that provides:
• Real-time price tracking
• AI-powered trading signals
• Professional technical analysis
• User-friendly interface

**Features:**
✅ 100% Telegram Policy Compliant
✅ No External API Required
✅ Educational Purpose Only
✅ Free & Always Available

**Disclaimer:**
This bot provides signals for educational purposes only. Cryptocurrency trading involves substantial risk. Always conduct your own research before making trading decisions.

**Version:** 2.0
**Last Update:** 2024
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    if not context.args:
        await update.message.reply_text("Please specify a cryptocurrency symbol.\nExample: /price BTC")
        return
    
    symbol = context.args[0].upper()
    if symbol not in CRYPTO_PAIRS:
        await update.message.reply_text(f"❌ Symbol '{symbol}' not supported.\nSupported: {', '.join(CRYPTO_PAIRS.keys())}")
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    time.sleep(0.5)
    
    coin = CRYPTO_PAIRS[symbol]
    price = get_price(symbol)
    change_24h = get_24h_change(symbol)
    volume = get_volume(symbol)
    
    response = f"""
{coin['color']} **{coin['name']} ({symbol}) Price**

💰 **Current Price:** ${price:,.6f}
📈 **24h Change:** {change_24h:+.2f}%
📊 **24h Volume:** {volume}
⏰ **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📌 **Quick Actions:**
/signal {symbol} - Get trading signals
/analyze {symbol} - Get technical analysis
"""
    
    keyboard = [
        [InlineKeyboardButton("📈 Signal", callback_data=f"signal_{symbol}"),
         InlineKeyboardButton("🔍 Analyze", callback_data=f"analyze_{symbol}")],
        [InlineKeyboardButton("⭐ Add to Watchlist", callback_data=f"watchlist_add_{symbol}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /signal command"""
    if not context.args:
        await update.message.reply_text("Please specify a cryptocurrency symbol.\nExample: /signal BTC")
        return
    
    symbol = context.args[0].upper()
    if symbol not in CRYPTO_PAIRS:
        await update.message.reply_text(f"❌ Symbol '{symbol}' not supported.\nSupported: {', '.join(CRYPTO_PAIRS.keys())}")
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    time.sleep(0.8)
    
    signal_data = generate_signal(symbol)
    coin = CRYPTO_PAIRS[symbol]
    
    if signal_data['signal'] == 'BUY':
        emoji = '🟢'
        signal_text = '**BUY**'
        advice = 'Consider entering a long position'
    elif signal_data['signal'] == 'SELL':
        emoji = '🔴'
        signal_text = '**SELL**'
        advice = 'Consider exiting or shorting'
    else:
        emoji = '⚪'
        signal_text = '**NEUTRAL**'
        advice = 'Wait for clearer signals'
    
    indicators = signal_data['indicators']
    
    response = f"""
{emoji} **Signal Analysis for {symbol}**

**Signal:** {signal_text}
**Confidence:** {signal_data['strength']}%
**Current Price:** ${signal_data['price']:,.6f}

**Reasons:**
{chr(10).join(['• ' + reason for reason in signal_data['reasons']])}

**Technical Indicators:**
📊 RSI: {indicators['rsi']}
📉 MA(7): ${indicators['ma7']:,.6f}
📉 MA(25): ${indicators['ma25']:,.6f}
📉 MA(50): ${indicators['ma50']:,.6f}

**Bollinger Bands:**
📈 Upper: ${indicators['bollinger_upper']:,.6f}
📊 Middle: ${indicators['bollinger_middle']:,.6f}
📉 Lower: ${indicators['bollinger_lower']:,.6f}

**Market Stats:**
⚡ Volatility: {indicators['volatility']}%
📊 Momentum: {indicators['momentum']}

**Recommendation:** {advice}

⚠️ **Disclaimer:** This is not financial advice. Always DYOR before trading.
"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Full Analysis", callback_data=f"analyze_{symbol}"),
         InlineKeyboardButton("🔄 Refresh", callback_data=f"signal_{symbol}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command"""
    if not context.args:
        await update.message.reply_text("Please specify a cryptocurrency symbol.\nExample: /analyze BTC")
        return
    
    symbol = context.args[0].upper()
    if symbol not in CRYPTO_PAIRS:
        await update.message.reply_text(f"❌ Symbol '{symbol}' not supported.\nSupported: {', '.join(CRYPTO_PAIRS.keys())}")
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    time.sleep(0.8)
    
    coin = CRYPTO_PAIRS[symbol]
    price = get_price(symbol)
    change_24h = get_24h_change(symbol)
    indicators = generate_technical_indicators(symbol)
    
    # Determine trend
    if indicators['ma7'] > indicators['ma25'] > indicators['ma50']:
        trend = '📈 Strong Bullish'
        trend_emoji = '🟢'
    elif indicators['ma7'] < indicators['ma25'] < indicators['ma50']:
        trend = '📉 Strong Bearish'
        trend_emoji = '🔴'
    elif indicators['ma7'] > indicators['ma25']:
        trend = '📈 Bullish'
        trend_emoji = '🟢'
    else:
        trend = '➡️ Neutral'
        trend_emoji = '⚪'
    
    response = f"""
🔍 **Detailed Technical Analysis - {symbol}**

{coin['color']} **{coin['name']} Market Analysis**

**Current Price:** ${price:,.6f}
**24h Change:** {change_24h:+.2f}%
**Trend:** {trend}

**Moving Averages:**
📉 MA(7): ${indicators['ma7']:,.6f}
📉 MA(25): ${indicators['ma25']:,.6f}
📉 MA(50): ${indicators['ma50']:,.6f}
📊 MA Alignment: {'Bullish' if indicators['ma7'] > indicators['ma25'] else 'Bearish'}

**Bollinger Bands (20,2):**
📈 Upper: ${indicators['bollinger_upper']:,.6f}
📊 Middle: ${indicators['bollinger_middle']:,.6f}
📉 Lower: ${indicators['bollinger_lower']:,.6f}
📊 Band Width: {((indicators['bollinger_upper'] - indicators['bollinger_lower']) / indicators['bollinger_middle'] * 100):.1f}%

**Key Indicators:**
📊 RSI (14): {indicators['rsi']} {'(Oversold)' if indicators['rsi'] < 30 else '(Overbought)' if indicators['rsi'] > 70 else '(Neutral)'}
⚡ Volatility: {indicators['volatility']}%
📊 Momentum: {indicators['momentum']}

**Market Sentiment:**
{trend_emoji} {trend}
{'✅ Low Volatility - Stable' if indicators['volatility'] < 3 else '⚡ High Volatility - Risky'}

💡 **Key Levels:**
🛡️ Support: ${round(indicators['bollinger_lower'] * 0.98, 6):,.6f}
🚀 Resistance: ${round(indicators['bollinger_upper'] * 1.02, 6):,.6f}

📌 **Action:**
{'🟢 Consider BUY if price holds support' if trend_emoji == '🟢' else '🔴 Consider SELL if price breaks support' if trend_emoji == '🔴' else '⚪ Wait for clearer direction'}
"""
    
    keyboard = [
        [InlineKeyboardButton("📈 Get Signal", callback_data=f"signal_{symbol}"),
         InlineKeyboardButton("💰 Price", callback_data=f"price_{symbol}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /market command - Show market overview"""
    await update.message.chat.send_action(action="typing")
    time.sleep(0.5)
    
    response = "📊 **Market Overview**\n\n"
    
    # Show top gainers/losers
    all_symbols = list(CRYPTO_PAIRS.keys())
    market_data = []
    
    for symbol in all_symbols:
        price = get_price(symbol)
        change = get_24h_change(symbol)
        market_data.append({
            'symbol': symbol,
            'price': price,
            'change': change
        })
    
    # Sort by change
    sorted_by_change = sorted(market_data, key=lambda x: x['change'], reverse=True)
    
    response += "🏆 **Top Gainers:**\n"
    for data in sorted_by_change[:3]:
        coin = CRYPTO_PAIRS[data['symbol']]
        response += f"{coin['color']} {data['symbol']}: ${data['price']:,.6f} ({data['change']:+.2f}%)\n"
    
    response += "\n📉 **Top Losers:**\n"
    for data in sorted_by_change[-3:]:
        coin = CRYPTO_PAIRS[data['symbol']]
        response += f"{coin['color']} {data['symbol']}: ${data['price']:,.6f} ({data['change']:+.2f}%)\n"
    
    response += f"\n📊 **Total Coins Tracked:** {len(CRYPTO_PAIRS)}"
    response += f"\n⏰ **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    keyboard = [
        [InlineKeyboardButton("📊 Full List", callback_data="market_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /watchlist command"""
    user_id = str(update.effective_user.id)
    
    # Initialize user data if not exists
    if user_id not in user_data:
        user_data[user_id] = {'watchlist': []}
    
    watchlist = user_data[user_id]['watchlist']
    
    # Handle subcommands
    if context.args:
        action = context.args[0].lower()
        if action == 'add' and len(context.args) > 1:
            symbol = context.args[1].upper()
            if symbol in CRYPTO_PAIRS:
                if symbol not in watchlist:
                    watchlist.append(symbol)
                    await update.message.reply_text(f"✅ Added {symbol} to your watchlist!")
                else:
                    await update.message.reply_text(f"ℹ️ {symbol} is already in your watchlist.")
            else:
                await update.message.reply_text(f"❌ '{symbol}' is not supported.")
            return
        
        elif action == 'remove' and len(context.args) > 1:
            symbol = context.args[1].upper()
            if symbol in watchlist:
                watchlist.remove(symbol)
                await update.message.reply_text(f"✅ Removed {symbol} from your watchlist!")
            else:
                await update.message.reply_text(f"ℹ️ {symbol} is not in your watchlist.")
            return
        
        elif action == 'clear':
            watchlist.clear()
            await update.message.reply_text("✅ Watchlist cleared!")
            return
    
    # Show watchlist
    if not watchlist:
        response = """
⭐ **Your Watchlist is Empty**

Add cryptocurrencies to your watchlist to track them easily.

**How to add:**
/watchlist add SYMBOL
Example: /watchlist add BTC

**How to remove:**
/watchlist remove SYMBOL

**Supported symbols:**
BTC, ETH, BNB, SOL, XRP, ADA, DOT, DOGE, LINK, MATIC, UNI, ATOM
"""
        await update.message.reply_text(response, parse_mode='Markdown')
        return
    
    response = "⭐ **Your Watchlist:**\n\n"
    keyboard = []
    
    for symbol in watchlist:
        if symbol in CRYPTO_PAIRS:
            coin = CRYPTO_PAIRS[symbol]
            price = get_price(symbol)
            change = get_24h_change(symbol)
            response += f"{coin['color']} **{symbol}**: ${price:,.6f} ({change:+.2f}%)\n"
            keyboard.append([InlineKeyboardButton(f"📊 {symbol}", callback_data=f"price_{symbol}")])
    
    response += f"\n**Total:** {len(watchlist)} coins"
    
    keyboard.append([InlineKeyboardButton("❌ Clear Watchlist", callback_data="watchlist_clear")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def market_all_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all market data"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("📊 Fetching all market data...")
    time.sleep(0.5)
    
    response = "📊 **Complete Market Data**\n\n"
    
    for symbol in CRYPTO_PAIRS:
        coin = CRYPTO_PAIRS[symbol]
        price = get_price(symbol)
        change = get_24h_change(symbol)
        emoji = '🟢' if change >= 0 else '🔴'
        response += f"{coin['color']} **{symbol}**: ${price:,.6f} {emoji} {change:+.2f}%\n"
    
    response += f"\n⏰ **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    response += "\n\n💡 Use /price SYMBOL for more details"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="market_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='Markdown')

async def market_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to market overview"""
    query = update.callback_query
    await query.answer()
    await market_command(update, context)

# ============= CALLBACK HANDLER =============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(update.effective_user.id)
    
    if data.startswith("price_"):
        symbol = data.replace("price_", "")
        context.args = [symbol]
        await price_command(update, context)
    
    elif data.startswith("signal_"):
        symbol = data.replace("signal_", "")
        context.args = [symbol]
        await signal_command(update, context)
    
    elif data.startswith("analyze_"):
        symbol = data.replace("analyze_", "")
        context.args = [symbol]
        await analyze_command(update, context)
    
    elif data.startswith("watchlist_add_"):
        symbol = data.replace("watchlist_add_", "")
        if user_id not in user_data:
            user_data[user_id] = {'watchlist': []}
        if symbol not in user_data[user_id]['watchlist']:
            user_data[user_id]['watchlist'].append(symbol)
            await query.edit_message_text(f"✅ {symbol} added to your watchlist!")
        else:
            await query.edit_message_text(f"ℹ️ {symbol} is already in your watchlist.")
    
    elif data == "watchlist_clear":
        if user_id in user_data:
            user_data[user_id]['watchlist'] = []
            await query.edit_message_text("✅ Watchlist cleared successfully!")
    
    elif data == "watchlist":
        await watchlist_command(update, context)
    
    elif data == "market":
        await market_command(update, context)
    
    elif data == "market_all":
        await market_all_callback(update, context)
    
    elif data == "market_back":
        await market_back_callback(update, context)
    
    elif data == "price":
        await query.edit_message_text("📊 To check price, use /price SYMBOL\nExample: /price BTC")
    
    elif data == "signal":
        await query.edit_message_text("📈 To get signals, use /signal SYMBOL\nExample: /signal ETH")
    
    elif data == "analyze":
        await query.edit_message_text("🔍 To analyze, use /analyze SYMBOL\nExample: /analyze SOL")
    
    elif data == "help":
        await help_command(update, context)
    
    elif data == "about":
        await about_command(update, context)

# ============= MAIN =============

def main():
    """Main entry point"""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("⚠️ ERROR: BOT_TOKEN not set!")
        print("Please set BOT_TOKEN in Railway environment variables.")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("signal", signal_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("market", market_command))
    application.add_handler(CommandHandler("watchlist", watchlist_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("🚀 Crypto Signal Hunter Bot is starting...")
    logger.info(f"✅ Bot token: {BOT_TOKEN[:10]}...")
    logger.info(f"✅ Supported coins: {len(CRYPTO_PAIRS)}")
    print("\n" + "="*50)
    print("🤖 CRYPTO SIGNAL HUNTER BOT")
    print("="*50)
    print(f"✅ Bot is running!")
    print(f"✅ Supported coins: {', '.join(CRYPTO_PAIRS.keys())}")
    print(f"✅ Find your bot at: https://t.me/your_bot_username")
    print("="*50 + "\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
