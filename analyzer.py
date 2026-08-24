import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self):
        self.signals = []

    def calculate_moving_average(self, prices, period):
        """Calculate simple moving average"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None
        
        sma = self.calculate_moving_average(prices, period)
        if sma is None:
            return None
        
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }

    def calculate_macd(self, prices):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < 26:
            return None
        
        ema12 = self.calculate_ema(prices, 12)
        ema26 = self.calculate_ema(prices, 26)
        
        if ema12 is None or ema26 is None:
            return None
        
        macd_line = ema12 - ema26
        signal_line = self.calculate_ema([macd_line], 9)
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': macd_line - signal_line
        }

    def calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        # Simple MA for first value
        sma = sum(prices[:period]) / period
        multiplier = 2 / (period + 1)
        
        ema = sma
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema

    def calculate_support_resistance(self, prices, window=5):
        """Find support and resistance levels"""
        if len(prices) < window * 2:
            return None
        
        highs = []
        lows = []
        
        for i in range(window, len(prices) - window):
            # Check if this is a local high
            if prices[i] > max(prices[i-window:i] + prices[i+1:i+window+1]):
                highs.append(prices[i])
            # Check if this is a local low
            if prices[i] < min(prices[i-window:i] + prices[i+1:i+window+1]):
                lows.append(prices[i])
        
        if not highs or not lows:
            return None
        
        resistance = sum(highs) / len(highs)
        support = sum(lows) / len(lows)
        
        return {
            'support': support,
            'resistance': resistance
        }

    def generate_signal(self, symbol, price_data):
        """Generate trading signal based on technical analysis"""
        prices = [d['price'] for d in price_data]
        current_price = prices[-1]
        
        signals = []
        
        # 1. Moving Average Crossover
        ma_short = self.calculate_moving_average(prices, 9)
        ma_long = self.calculate_moving_average(prices, 21)
        
        if ma_short and ma_long:
            if ma_short > ma_long and prices[-2] <= ma_long:
                signals.append({
                    'type': 'BUY',
                    'strength': 0.7,
                    'reason': 'MA Crossover (9 > 21)'
                })
            elif ma_short < ma_long and prices[-2] >= ma_long:
                signals.append({
                    'type': 'SELL',
                    'strength': 0.7,
                    'reason': 'MA Crossover (9 < 21)'
                })
        
        # 2. RSI
        rsi = self.calculate_rsi(prices)
        if rsi:
            if rsi < 30:
                signals.append({
                    'type': 'BUY',
                    'strength': 0.8,
                    'reason': f'RSI Oversold ({round(rsi, 1)})'
                })
            elif rsi > 70:
                signals.append({
                    'type': 'SELL',
                    'strength': 0.8,
                    'reason': f'RSI Overbought ({round(rsi, 1)})'
                })
        
        # 3. Bollinger Bands
        bb = self.calculate_bollinger_bands(prices)
        if bb:
            if current_price < bb['lower']:
                signals.append({
                    'type': 'BUY',
                    'strength': 0.6,
                    'reason': 'Price below lower Bollinger Band'
                })
            elif current_price > bb['upper']:
                signals.append({
                    'type': 'SELL',
                    'strength': 0.6,
                    'reason': 'Price above upper Bollinger Band'
                })
        
        # 4. Support/Resistance
        sr = self.calculate_support_resistance(prices)
        if sr:
            if current_price < sr['support']:
                signals.append({
                    'type': 'BUY',
                    'strength': 0.75,
                    'reason': 'Price near support level'
                })
            elif current_price > sr['resistance']:
                signals.append({
                    'type': 'SELL',
                    'strength': 0.75,
                    'reason': 'Price near resistance level'
                })
        
        # Determine overall signal
        if not signals:
            return {
                'symbol': symbol,
                'signal': 'NEUTRAL',
                'strength': 0,
                'reasons': ['No clear signal'],
                'price': current_price,
                'rsi': rsi,
                'ma_short': ma_short,
                'ma_long': ma_long
            }
        
        # Weight signals
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        buy_strength = sum(s['strength'] for s in buy_signals)
        sell_strength = sum(s['strength'] for s in sell_signals)
        
        if buy_strength > sell_strength:
            signal_type = 'BUY'
            strength = min(buy_strength / (buy_strength + sell_strength), 1)
        elif sell_strength > buy_strength:
            signal_type = 'SELL'
            strength = min(sell_strength / (buy_strength + sell_strength), 1)
        else:
            signal_type = 'NEUTRAL'
            strength = 0
        
        return {
            'symbol': symbol,
            'signal': signal_type,
            'strength': round(strength * 100),
            'reasons': [s['reason'] for s in signals],
            'price': current_price,
            'rsi': rsi,
            'ma_short': ma_short,
            'ma_long': ma_long,
            'signals_count': len(signals)
        }

    def get_market_summary(self, symbol, price_data):
        """Get comprehensive market summary"""
        prices = [d['price'] for d in price_data]
        current_price = prices[-1]
        
        # Calculate indicators
        rsi = self.calculate_rsi(prices)
        ma7 = self.calculate_moving_average(prices, 7)
        ma25 = self.calculate_moving_average(prices, 25)
        bb = self.calculate_bollinger_bands(prices)
        
        # Price change
        price_change = prices[-1] - prices[0]
        price_change_percent = (price_change / prices[0]) * 100
        
        # Volatility (based on standard deviation)
        volatility = np.std(prices[-20:]) if len(prices) >= 20 else 0
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'price_change': round(price_change, 6),
            'price_change_percent': round(price_change_percent, 2),
            'rsi': round(rsi, 1) if rsi else None,
            'ma7': round(ma7, 6) if ma7 else None,
            'ma25': round(ma25, 6) if ma25 else None,
            'bollinger_upper': round(bb['upper'], 6) if bb else None,
            'bollinger_middle': round(bb['middle'], 6) if bb else None,
            'bollinger_lower': round(bb['lower'], 6) if bb else None,
            'volatility': round(volatility, 6),
            'data_points': len(prices)
        }
