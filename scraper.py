import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache = {}
        self.last_fetch = {}

    def get_price_binance(self, pair):
        """Scrape price from Binance using their public ticker page"""
        try:
            url = f"https://www.binance.com/en/trade/{pair}"
            response = self.session.get(url, timeout=10)
            
            # Use regex to find price data from page source
            price_pattern = r'"p":"([0-9.]+)"'
            match = re.search(price_pattern, response.text)
            
            if match:
                price = float(match.group(1))
                return {
                    'price': price,
                    'source': 'Binance',
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Binance scrape error: {e}")
            return None

    def get_price_coingecko(self, coin_id):
        """Scrape price from CoinGecko"""
        try:
            url = f"https://www.coingecko.com/en/coins/{coin_id}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find price element
            price_element = soup.find('span', {'data-target': 'price.price'})
            if price_element:
                price_text = price_element.text.strip()
                price = float(price_text.replace('$', '').replace(',', ''))
                return {
                    'price': price,
                    'source': 'CoinGecko',
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"CoinGecko scrape error: {e}")
            return None

    def get_price_coinmarketcap(self, coin_name):
        """Scrape price from CoinMarketCap"""
        try:
            url = f"https://coinmarketcap.com/currencies/{coin_name}/"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find price element
            price_element = soup.find('div', {'class': 'priceValue'})
            if price_element:
                price_text = price_element.text.strip()
                price = float(price_text.replace('$', '').replace(',', ''))
                return {
                    'price': price,
                    'source': 'CoinMarketCap',
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"CoinMarketCap scrape error: {e}")
            return None

    def get_market_data(self, symbol, coin_name, pair):
        """Aggregate price data from multiple sources"""
        # Map symbol to coin identifiers for different sites
        coin_map = {
            'BTC': {'coingecko': 'bitcoin', 'cmc': 'bitcoin'},
            'ETH': {'coingecko': 'ethereum', 'cmc': 'ethereum'},
            'BNB': {'coingecko': 'binancecoin', 'cmc': 'bnb'},
            'SOL': {'coingecko': 'solana', 'cmc': 'solana'},
            'XRP': {'coingecko': 'ripple', 'cmc': 'xrp'},
            'ADA': {'coingecko': 'cardano', 'cmc': 'cardano'},
            'DOT': {'coingecko': 'polkadot', 'cmc': 'polkadot'},
            'DOGE': {'coingecko': 'dogecoin', 'cmc': 'dogecoin'}
        }

        coin_info = coin_map.get(symbol, {})
        price_data = []
        
        # Try all sources
        if coin_info.get('coingecko'):
            data = self.get_price_coingecko(coin_info['coingecko'])
            if data:
                price_data.append(data)
        
        if coin_info.get('cmc'):
            data = self.get_price_coinmarketcap(coin_info['cmc'])
            if data:
                price_data.append(data)
        
        # Try Binance as fallback
        data = self.get_price_binance(pair)
        if data:
            price_data.append(data)
        
        if not price_data:
            return None
        
        # Average prices from all sources
        avg_price = sum(d['price'] for d in price_data) / len(price_data)
        
        return {
            'symbol': symbol,
            'name': coin_name,
            'price': round(avg_price, 6),
            'sources': len(price_data),
            'timestamp': datetime.now().isoformat(),
            'raw_data': price_data
        }

    def get_historical_prices(self, symbol, timeframe='1h', limit=50):
        """
        Simulate historical price data using moving averages
        Since we're scraping real-time, we'll use random walk with drift
        """
        # Get current price first
        current_data = self.get_market_data(symbol, symbol, f"{symbol}USDT")
        if not current_data:
            return None
        
        current_price = current_data['price']
        historical = []
        
        # Generate simulated historical data
        import random
        price = current_price
        
        for i in range(limit, 0, -1):
            # Add random movement with slight upward drift
            change = random.uniform(-0.02, 0.025)  # -2% to +2.5%
            price = price / (1 + change)
            
            # Ensure price doesn't go to 0
            price = max(price, 0.01)
            
            historical.append({
                'timestamp': datetime.now().timestamp() - (i * 60),
                'price': round(price, 6)
            })
        
        # Add current price
        historical.append({
            'timestamp': datetime.now().timestamp(),
            'price': current_price
        })
        
        return historical
