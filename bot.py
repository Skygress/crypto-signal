import os
import time
import threading
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue
import json

from config import BOT_TOKEN, CRYPTO_PAIRS, TIMEFRAMES, ADMIN_IDS, SIGNAL_INTERVAL
from scraper import CryptoScraper
from analyzer import TechnicalAnalyzer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize scraper and analyzer
scraper = CryptoScraper()
analyzer = TechnicalAnalyzer()

# Store price history in memory
price_history = {}
user_preferences = {}
active_signals = {}

# Bot Commands
BOT_COMMANDS = {
    'start': 'Start the bot and view main menu',
    'price': 'Get current price for a cryptocurrency',
    'signal': 'Get trading signals for a crypto',
    'analyze': 'Get detailed technical analysis',
    'watchlist': 'Manage your watchlist',
    'alerts': 'Set price alerts',
    'help': 'Show all available commands',
    'about': 'About Crypto Signal Hunter'
}

class CryptoSignalBot:
    def __init__(self):
        self.scraper = CryptoScraper()
        self.analyzer = TechnicalAnalyzer()
        self.price_history = {}
        self.user_data = {}
        self.running = True

    def start_bot(self):
        """Start the Telegram bot"""
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("about", self.about_command))
        application.add_handler(CommandHandler("price", self.price_command))
        application.add_handler(CommandHandler("signal", self.signal_command))
        application.add_handler(CommandHandler("analyze", self.analyze_command))
        application.add_handler(CommandHandler("watchlist", self.watchlist_command))
        application.add_handler(CommandHandler("alerts", self.alerts_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Add job queue for automatic signals
        job_queue = application.job_queue
        job_queue.run_repeating(self.auto_signal_check, interval=SIGNAL_INTERVAL, first=10)
        
        # Start bot
        logger.info("Starting bot...")
        application.run_polling()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = f"""
🚀 Welcome to Crypto Signal Hunter, {user.first_name}!

Your AI-powered cryptocurrency trading assistant. Get real-time signals, technical analysis, and market insights.

📊 **What I Can Do:**
• Real-time price tracking for top cryptos
• BUY/SELL signals based on technical analysis
• Technical indicators (RSI, MA, Bollinger Bands)
• Price alerts and watchlist management
• Market summaries and volatility analysis

🪙 **Supported Cryptocurrencies:**
{', '.join(CRYPTO_PAIRS.keys())}

💡 **Get Started:**
Use /help to see all available commands
Use /price BTC to check Bitcoin price
Use /signal ETH to get trading signals

📢 **Important:**
This bot is for educational purposes only. Always do your own research before trading.
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 Price", callback_data="price"),
             InlineKeyboardButton("📈 Signal", callback_data="signal")],
            [InlineKeyboardButton("🔍 Analyze", callback_data="analyze"),
             InlineKeyboardButton("⭐ Watchlist", callback_data="watchlist")],
            [InlineKeyboardButton("💬 Help", callback_data="help"),
             InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 **Available Commands:**

🔹 /start - Start the bot
🔹 /price [symbol] - Get current price (e.g., /price BTC)
🔹 /signal [symbol] - Get trading signals with analysis
🔹 /analyze [symbol] - Get detailed technical analysis
🔹 /watchlist - Manage your watchlist
🔹 /alerts - Set price alerts
🔹 /about - About Crypto Signal Hunter
🔹 /help - Show this help message

⚙️ **Symbol Examples:**
/price BTC
/signal ETH
/analyze SOL

📊 **Technical Indicators Used:**
• Moving Averages (7 & 25 period)
• RSI (Relative Strength Index)
• Bollinger Bands
• Support & Resistance Levels
• MACD (Coming soon)

📌 **Quick Tips:**
• The bot analyzes data from multiple sources
• Signals are generated using multiple indicators
• Always confirm signals with your own analysis
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
        about_text = """
🔍 **Crypto Signal Hunter v2.0**

Built by Telegram & Web3 Expert

An advanced cryptocurrency analysis bot that provides:
• Real-time price tracking without APIs
• AI-powered trading signals
• Professional technical analysis
• User-friendly interface

**Features:**
✅ 100% Telegram Policy Compliant
✅ No External API Required
✅ Real-time Web Scraping
✅ Multiple Data Sources
✅ Educational Purpose Only

**Disclaimer:**
This bot provides signals for educational purposes only. Cryptocurrency trading involves substantial risk. Always conduct your own research before making trading decisions.

📱 **Contact:**
For support or feedback, contact the developer.

**Version:** 2.0
**Last Update:** 2024
"""
        await update.message.reply_text(about_text, parse_mode='Markdown')

    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        # Get price data
        coin = CRYPTO_PAIRS[symbol]
        price_data = self.scraper.get_market_data(symbol, coin['name'], coin['pair'])
        
        if not price_data:
            await update.message.reply_text(f"❌ Could not fetch price for {symbol}. Please try again later.")
            return
        
        # Get historical data for trends
        hist_data = self.scraper.get_historical_prices(symbol, '1h', 24)
        
        if hist_data:
            prices = [d['price'] for d in hist_data]
            change = ((prices[-1] - prices[0]) / prices[0]) * 100
        else:
            change = 0
        
        # Format response
        response = f"""
📊 **{coin['name']} ({symbol}) Price**

💰 **Current Price:** ${price_data['price']:,.6f}
📈 **24h Change:** {change:+.2f}%
🔄 **Data Sources:** {price_data['sources']}
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

    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        # Get historical data
        hist_data = self.scraper.get_historical_prices(symbol, '1h', 50)
        
        if not hist_data or len(hist_data) < 20:
            await update.message.reply_text(f"❌ Not enough data to generate signal for {symbol}. Please try again later.")
            return
        
        # Generate signal
        signal = self.analyzer.generate_signal(symbol, hist_data)
        summary = self.analyzer.get_market_summary(symbol, hist_data)
        
        # Format signal response
        if signal['signal'] == 'BUY':
            emoji = '🟢'
            signal_text = '**BUY**'
            advice = 'Consider entering a long position'
        elif signal['signal'] == 'SELL':
            emoji = '🔴'
            signal_text = '**SELL**'
            advice = 'Consider exiting or shorting'
        else:
            emoji = '⚪'
            signal_text = '**NEUTRAL**'
            advice = 'Wait for clearer signals'
        
        response = f"""
{emoji} **Signal Analysis for {symbol}**

**Signal:** {signal_text}
**Confidence:** {signal['strength']}%
**Current Price:** ${signal['price']:,.6f}

**Reasons:**
{chr(10).join(['• ' + reason for reason in signal['reasons']])}

**Technical Indicators:**
📊 RSI: {signal.get('rsi', 'N/A')}
📉 MA(7): ${signal.get('ma_short', 0):,.6f}
📉 MA(25): ${signal.get('ma_long', 0):,.6f}

**Recommendation:** {advice}

⚠️ **Disclaimer:** This is not financial advice. Always DYOR before trading.
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 Full Analysis", callback_data=f"analyze_{symbol}"),
             InlineKeyboardButton("🔄 Refresh", callback_data=f"signal_{symbol}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        # Get data
        hist_data = self.scraper.get_historical_prices(symbol, '1h', 50)
        
        if not hist_data:
            await update.message.reply_text(f"❌ Could not fetch data for {symbol}. Please try again later.")
            return
        
        # Get summary
        summary = self.analyzer.get_market_summary(symbol, hist_data)
        
        response = f"""
🔍 **Detailed Technical Analysis - {symbol}**

**Current Price:** ${summary['current_price']:,.6f}
**24h Change:** {summary['price_change_percent']:+.2f}%

**Moving Averages:**
📉 MA(7): ${summary['ma7']:,.6f}
📉 MA(25): ${summary['ma25']:,.6f}
📉 MA Trend: {'Bullish' if summary['ma7'] > summary['ma25'] else 'Bearish'}

**Bollinger Bands:**
📈 Upper: ${summary['bollinger_upper']:,.6f}
📊 Middle: ${summary['bollinger_middle']:,.6f}
📉 Lower: ${summary['bollinger_lower']:,.6f}

**Market Statistics:**
📊 RSI: {summary['rsi']}
📊 Volatility: {summary['volatility']*100:.2f}%
📊 Data Points: {summary['data_points']}

**Market Sentiment:**
{'📈 Bullish' if summary['rsi'] and summary['rsi'] > 50 else '📉 Bearish'}
{'⚡ High Volatility' if summary['volatility'] > summary['current_price'] * 0.02 else '✅ Low Volatility'}

💡 **Tips:**
• RSI < 30 = Oversold (Potential Buy)
• RSI > 70 = Overbought (Potential Sell)
• Price near lower band = Oversold
• Price near upper band = Overbought
"""
        
        keyboard = [
            [InlineKeyboardButton("📈 Get Signal", callback_data=f"signal_{symbol}"),
             InlineKeyboardButton("💰 Price", callback_data=f"price_{symbol}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

    async def watchlist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /watchlist command"""
        user_id = update.effective_user.id
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {'watchlist': []}
        
        watchlist = self.user_data[user_id]['watchlist']
        
        if not watchlist:
            response = """
⭐ **Your Watchlist is Empty**

Add cryptocurrencies to your watchlist to track them easily.

**How to add:**
Use /watchlist add SYMBOL
Example: /watchlist add BTC

Or use the "Add to Watchlist" button when checking prices.
"""
            await update.message.reply_text(response, parse_mode='Markdown')
            return
        
        # Format watchlist
        response = "⭐ **Your Watchlist:**\n\n"
        keyboard = []
        
        for symbol in watchlist:
            if symbol in CRYPTO_PAIRS:
                coin = CRYPTO_PAIRS[symbol]
                price_data = self.scraper.get_market_data(symbol, coin['name'], coin['pair'])
                
                if price_data:
                    response += f"• **{symbol}** - ${price_data['price']:,.6f}\n"
                    keyboard.append([InlineKeyboardButton(f"📊 {symbol}", callback_data=f"price_{symbol}")])
                else:
                    response += f"• **{symbol}** - Data unavailable\n"
        
        response += f"\nTotal: {len(watchlist)} coins"
        
        keyboard.append([InlineKeyboardButton("❌ Clear Watchlist", callback_data="watchlist_clear")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        user_id = update.effective_user.id
        
        alert_text = """
🔔 **Price Alerts**

Set price alerts for your favorite cryptocurrencies.

**How to set alerts:**
/alerts set SYMBOL PRICE
Example: /alerts set BTC 50000

**How to manage:**
/alerts list - View your active alerts
/alerts remove SYMBOL - Remove alert for a symbol

**Alert Types:**
• Price reaches target (BUY/SELL trigger)
• 5% price movement
• RSI oversold/overbought

⚠️ **Note:** Alerts are checked every 5 minutes.
"""
        await update.message.reply_text(alert_text, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Handle different callback types
        if data.startswith("price_"):
            symbol = data.replace("price_", "")
            context.args = [symbol]
            await self.price_command(update, context)
        
        elif data.startswith("signal_"):
            symbol = data.replace("signal_", "")
            context.args = [symbol]
            await self.signal_command(update, context)
        
        elif data.startswith("analyze_"):
            symbol = data.replace("analyze_", "")
            context.args = [symbol]
            await self.analyze_command(update, context)
        
        elif data.startswith("watchlist_add_"):
            symbol = data.replace("watchlist_add_", "")
            user_id = update.effective_user.id
            
            if user_id not in self.user_data:
                self.user_data[user_id] = {'watchlist': []}
            
            if symbol not in self.user_data[user_id]['watchlist']:
                self.user_data[user_id]['watchlist'].append(symbol)
                await query.edit_message_text(f"✅ {symbol} added to your watchlist!")
            else:
                await query.edit_message_text(f"ℹ️ {symbol} is already in your watchlist.")
        
        elif data == "watchlist_clear":
            user_id = update.effective_user.id
            if user_id in self.user_data:
                self.user_data[user_id]['watchlist'] = []
                await query.edit_message_text("✅ Watchlist cleared successfully!")
        
        elif data == "price":
            await query.edit_message_text("📊 To check price, use /price SYMBOL\nExample: /price BTC")
        
        elif data == "signal":
            await query.edit_message_text("📈 To get signals, use /signal SYMBOL\nExample: /signal ETH")
        
        elif data == "analyze":
            await query.edit_message_text("🔍 To analyze, use /analyze SYMBOL\nExample: /analyze SOL")
        
        elif data == "watchlist":
            await self.watchlist_command(update, context)
        
        elif data == "help":
            await self.help_command(update, context)
        
        elif data == "about":
            await self.about_command(update, context)

    async def auto_signal_check(self, context: ContextTypes.DEFAULT_TYPE):
        """Automatically check for signals and notify users"""
        logger.info("Running automatic signal check...")
        
        for symbol in CRYPTO_PAIRS:
            try:
                hist_data = self.scraper.get_historical_prices(symbol, '1h', 50)
                
                if hist_data and len(hist_data) >= 20:
                    signal = self.analyzer.generate_signal(symbol, hist_data)
                    
                    # Check if signal is strong
                    if signal['strength'] > 70:
                        # Store signal to notify users later
                        active_signals[symbol] = {
                            'signal': signal,
                            'timestamp': datetime.now().isoformat()
                        }
                        logger.info(f"Strong signal detected for {symbol}: {signal['signal']} ({signal['strength']}%)")
                        
                        # Notify admin (if configured)
                        for admin_id in ADMIN_IDS:
                            try:
                                await context.bot.send_message(
                                    chat_id=admin_id,
                                    text=f"🚨 **Strong Signal Alert**\n\n"
                                         f"Symbol: {symbol}\n"
                                         f"Signal: {signal['signal']}\n"
                                         f"Strength: {signal['strength']}%\n"
                                         f"Price: ${signal['price']:,.6f}"
                                )
                            except:
                                pass
            except Exception as e:
                logger.error(f"Error in auto signal check for {symbol}: {e}")

def main():
    """Main entry point"""
    bot = CryptoSignalBot()
    bot.start_bot()

if __name__ == "__main__":
    main()
