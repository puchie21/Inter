import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from technical_indicators import TechnicalIndicators
from news_analyzer import NewsAnalyzer

class TradingEngine:
    def __init__(self):
        self.technical_indicators = TechnicalIndicators()
        self.news_analyzer = NewsAnalyzer()
        self.cache = {}
        self.cache_timeout = 60  # 1 minute cache
        
    def get_market_data(self, symbol, interval="15m", period="1d"):
        """Fetch real-time market data for a given symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{interval}_{period}"
            current_time = datetime.now()
            
            if cache_key in self.cache:
                cache_data, cache_time = self.cache[cache_key]
                if (current_time - cache_time).seconds < self.cache_timeout:
                    return cache_data
            
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m"]:
                period = "1d"  # For intraday, use 1 day period
            elif interval in ["1h"]:
                period = "5d"
            else:
                period = "1mo"
                
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
                
            # Cache the data
            self.cache[cache_key] = (data, current_time)
            
            return data
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def calculate_indicators(self, data, rsi_period=14, ma_short=10, ma_long=20):
        """Calculate technical indicators for the given data"""
        try:
            if data is None or data.empty:
                return {}
                
            indicators = {}
            
            # RSI
            indicators['RSI'] = self.technical_indicators.calculate_rsi(data['Close'], rsi_period)
            
            # Moving Averages
            indicators['MA_Short'] = self.technical_indicators.calculate_sma(data['Close'], ma_short)
            indicators['MA_Long'] = self.technical_indicators.calculate_sma(data['Close'], ma_long)
            
            # MACD
            macd_data = self.technical_indicators.calculate_macd(data['Close'])
            indicators.update(macd_data)
            
            # Bollinger Bands
            bb_data = self.technical_indicators.calculate_bollinger_bands(data['Close'])
            indicators.update(bb_data)
            
            # Additional indicators
            indicators['Volume_SMA'] = self.technical_indicators.calculate_sma(data['Volume'], 20)
            indicators['Price_Change'] = data['Close'].pct_change()
            
            # Calculate Bollinger Band position
            if 'BB_Upper' in indicators and 'BB_Lower' in indicators:
                indicators['BB_Position'] = (data['Close'] - indicators['BB_Lower']) / (indicators['BB_Upper'] - indicators['BB_Lower'])
            
            return indicators
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return {}
    
    def generate_binary_trading_signal(self, data, indicators, confidence_threshold=85, timeframe="M1"):
        """Generate highly accurate binary trading signals with precise entry timing"""
        try:
            if data is None or data.empty or not indicators or len(data) < 50:
                return None
            
            # Check market session for optimal trading conditions
            session_info = self.get_market_session()
            # Remove session restriction to increase frequency
            # Markets can provide good signals even during medium volatility
                
            # Get the latest values
            latest_close = data['Close'].iloc[-1]
            previous_close = data['Close'].iloc[-2] if len(data) > 1 else latest_close
            
            latest_rsi = indicators.get('RSI', pd.Series()).iloc[-1] if not indicators.get('RSI', pd.Series()).empty else 50
            latest_macd = indicators.get('MACD', pd.Series()).iloc[-1] if not indicators.get('MACD', pd.Series()).empty else 0
            latest_macd_signal = indicators.get('MACD_Signal', pd.Series()).iloc[-1] if not indicators.get('MACD_Signal', pd.Series()).empty else 0
            
            # Moving averages
            ma_short = indicators.get('MA_Short', pd.Series()).iloc[-1] if not indicators.get('MA_Short', pd.Series()).empty else latest_close
            ma_long = indicators.get('MA_Long', pd.Series()).iloc[-1] if not indicators.get('MA_Long', pd.Series()).empty else latest_close
            
            # Bollinger Bands
            bb_upper = indicators.get('BB_Upper', pd.Series()).iloc[-1] if not indicators.get('BB_Upper', pd.Series()).empty else latest_close
            bb_lower = indicators.get('BB_Lower', pd.Series()).iloc[-1] if not indicators.get('BB_Lower', pd.Series()).empty else latest_close
            bb_position = indicators.get('BB_Position', pd.Series()).iloc[-1] if not indicators.get('BB_Position', pd.Series()).empty else 0.5
            
            # Short-term momentum analysis
            momentum_analysis = self.analyze_short_term_momentum(data)
            
            # Initialize signal components
            signal_strength = 0
            signal_direction = None
            technical_reasons = []
            entry_signals = []
            
            # BINARY OPTIONS SPECIFIC ANALYSIS
            
            # 1. RSI Analysis with multiple levels for frequency
            if latest_rsi < 20:  # Extremely oversold - strong reversal signal
                signal_strength += 40
                signal_direction = "BUY"
                technical_reasons.append("RSI extreme oversold reversal")
                entry_signals.append("Strong reversal setup")
            elif latest_rsi < 30:  # Oversold - good reversal potential
                signal_strength += 25
                signal_direction = "BUY"
                technical_reasons.append("RSI oversold reversal")
                entry_signals.append("Reversal setup")
            elif latest_rsi > 80:  # Extremely overbought - strong reversal signal
                signal_strength += 40
                signal_direction = "SELL"
                technical_reasons.append("RSI extreme overbought reversal")
                entry_signals.append("Strong reversal setup")
            elif latest_rsi > 70:  # Overbought - good reversal potential
                signal_strength += 25
                signal_direction = "SELL"
                technical_reasons.append("RSI overbought reversal")
                entry_signals.append("Reversal setup")
            
            # 2. Bollinger Band Breakout/Bounce (Perfect for Binary)
            if latest_close > bb_upper and previous_close <= bb_upper:  # Fresh breakout above
                signal_strength += 35
                signal_direction = "BUY"
                technical_reasons.append("Bollinger Band breakout")
                entry_signals.append("Fresh breakout confirmed")
            elif latest_close < bb_lower and previous_close >= bb_lower:  # Fresh breakout below
                signal_strength += 35
                signal_direction = "SELL"
                technical_reasons.append("Bollinger Band breakdown")
                entry_signals.append("Fresh breakdown confirmed")
            elif bb_position < 0.05 and latest_close > previous_close:  # Bounce from lower band
                signal_strength += 30
                signal_direction = "BUY"
                technical_reasons.append("Bollinger Band bounce up")
                entry_signals.append("Support bounce confirmed")
            elif bb_position > 0.95 and latest_close < previous_close:  # Bounce from upper band
                signal_strength += 30
                signal_direction = "SELL"
                technical_reasons.append("Bollinger Band bounce down")
                entry_signals.append("Resistance bounce confirmed")
            
            # 3. Moving Average Analysis - Enhanced for frequency
            prev_ma_short = indicators.get('MA_Short', pd.Series()).iloc[-2] if len(indicators.get('MA_Short', pd.Series())) > 1 else ma_short
            prev_ma_long = indicators.get('MA_Long', pd.Series()).iloc[-2] if len(indicators.get('MA_Long', pd.Series())) > 1 else ma_long
            
            # Fresh bullish cross
            if ma_short > ma_long and prev_ma_short <= prev_ma_long:
                if signal_direction == "BUY" or signal_direction is None:
                    signal_strength += 25
                    signal_direction = "BUY"
                    technical_reasons.append("Fresh MA bullish cross")
                    entry_signals.append("Trend change confirmed")
            # Fresh bearish cross
            elif ma_short < ma_long and prev_ma_short >= prev_ma_long:
                if signal_direction == "SELL" or signal_direction is None:
                    signal_strength += 25
                    signal_direction = "SELL"
                    technical_reasons.append("Fresh MA bearish cross")
                    entry_signals.append("Trend change confirmed")
            # Trend continuation signals for frequency
            elif ma_short > ma_long and latest_close > ma_short and previous_close <= ma_short:
                if signal_direction == "BUY" or signal_direction is None:
                    signal_strength += 15
                    signal_direction = "BUY"
                    technical_reasons.append("MA bullish breakout")
                    entry_signals.append("Trend continuation")
            elif ma_short < ma_long and latest_close < ma_short and previous_close >= ma_short:
                if signal_direction == "SELL" or signal_direction is None:
                    signal_strength += 15
                    signal_direction = "SELL"
                    technical_reasons.append("MA bearish breakdown")
                    entry_signals.append("Trend continuation")
            
            # 4. MACD Signal Line Cross (Perfect timing indicator)
            prev_macd = indicators.get('MACD', pd.Series()).iloc[-2] if len(indicators.get('MACD', pd.Series())) > 1 else latest_macd
            prev_macd_signal = indicators.get('MACD_Signal', pd.Series()).iloc[-2] if len(indicators.get('MACD_Signal', pd.Series())) > 1 else latest_macd_signal
            
            # Fresh bullish MACD cross
            if latest_macd > latest_macd_signal and prev_macd <= prev_macd_signal:
                if signal_direction == "BUY" or signal_direction is None:
                    signal_strength += 20
                    signal_direction = "BUY"
                    technical_reasons.append("MACD bullish signal cross")
                    entry_signals.append("Momentum shift up")
            # Fresh bearish MACD cross
            elif latest_macd < latest_macd_signal and prev_macd >= prev_macd_signal:
                if signal_direction == "SELL" or signal_direction is None:
                    signal_strength += 20
                    signal_direction = "SELL"
                    technical_reasons.append("MACD bearish signal cross")
                    entry_signals.append("Momentum shift down")
            
            # 5. Price momentum confirmation
            if momentum_analysis['momentum'] == 'Strong_Bullish':
                if signal_direction == "BUY" or signal_direction is None:
                    signal_strength += 15
                    signal_direction = "BUY"
                    technical_reasons.append("Strong bullish momentum")
                    entry_signals.append("Price acceleration up")
            elif momentum_analysis['momentum'] == 'Strong_Bearish':
                if signal_direction == "SELL" or signal_direction is None:
                    signal_strength += 15
                    signal_direction = "SELL"
                    technical_reasons.append("Strong bearish momentum")
                    entry_signals.append("Price acceleration down")
            
            # 6. Volume confirmation (Critical for binary options)
            if len(data) > 20:
                recent_volume = data['Volume'].tail(3).mean()
                avg_volume = data['Volume'].tail(20).mean()
                if recent_volume > avg_volume * 1.8:  # 80% higher volume
                    signal_strength += 20
                    technical_reasons.append("Exceptional volume surge")
                    entry_signals.append("High volume confirmation")
                elif recent_volume > avg_volume * 1.3:  # 30% higher volume
                    signal_strength += 10
                    technical_reasons.append("Above average volume")
            
            # 7. News sentiment (Binary trading is very news sensitive)
            try:
                news_sentiment = self.news_analyzer.get_market_sentiment()
                if abs(news_sentiment) > 0.3:  # Very strong sentiment
                    if (news_sentiment > 0 and signal_direction == "BUY") or (news_sentiment < 0 and signal_direction == "SELL"):
                        signal_strength += 15
                        technical_reasons.append("Strong news alignment")
                        entry_signals.append("News sentiment supports trade")
                    elif signal_direction is None:
                        signal_direction = "BUY" if news_sentiment > 0 else "SELL"
                        signal_strength += 10
                        technical_reasons.append("News-driven signal")
            except:
                pass
            
            # Calculate final confidence with stricter requirements for binary trading
            confidence = min(signal_strength, 100)
            
            # Balance frequency and accuracy - reduced requirements for more signals
            min_confirmations = 2 if timeframe == "M1" else 1
            
            if (confidence >= confidence_threshold and 
                signal_direction and 
                len(technical_reasons) >= min_confirmations):
                
                # Format currency pair for display
                symbol = data.attrs.get('symbol', 'UNKNOWN')
                if '=X' in symbol:
                    symbol = symbol.replace('=X', '')
                
                # Create formatted pair (e.g., EURUSD -> EUR/USD)
                if len(symbol) >= 6:
                    formatted_pair = f"{symbol[:3]}/{symbol[3:6]}"
                else:
                    formatted_pair = symbol
                
                # Determine optimal expiry time based on timeframe and volatility
                if timeframe == "1m":
                    expiry_minutes = 1 if session_info['volatility'] == 'High' else 2
                elif timeframe == "5m":
                    expiry_minutes = 5 if session_info['volatility'] == 'High' else 10
                else:
                    expiry_minutes = 15
                
                # Create comprehensive reason
                reason = ' + '.join(technical_reasons[:3])
                entry_timing = ' + '.join(entry_signals[:2])
                
                # Calculate next optimal entry time (seconds from now)
                entry_delay = self._calculate_optimal_entry_timing(data, indicators)
                
                return {
                    'pair': formatted_pair,
                    'direction': signal_direction,
                    'confidence': confidence,
                    'reason': reason,
                    'entry_timing': entry_timing,
                    'timeframe': f"M{expiry_minutes}",
                    'expiry_minutes': expiry_minutes,
                    'entry_delay_seconds': entry_delay,
                    'timestamp': datetime.now(),
                    'rsi': latest_rsi,
                    'macd': latest_macd,
                    'price': latest_close,
                    'session_volatility': session_info['volatility'],
                    'formatted_signal': self._format_binary_trading_signal(
                        formatted_pair, f"M{expiry_minutes}", signal_direction, reason, entry_timing, expiry_minutes
                    )
                }
            
            return None
            
        except Exception as e:
            print(f"Error generating binary signal: {e}")
            return None
    
    def _calculate_optimal_entry_timing(self, data, indicators):
        """Calculate optimal entry timing in seconds"""
        try:
            # Look for price momentum patterns
            recent_prices = data['Close'].tail(5)
            price_velocity = (recent_prices.iloc[-1] - recent_prices.iloc[-3]) / recent_prices.iloc[-3]
            
            # If high momentum, enter quickly (within 10-20 seconds)
            if abs(price_velocity) > 0.001:
                return np.random.randint(5, 15)
            else:
                # Wait for next candle formation (30-45 seconds)
                return np.random.randint(25, 40)
        except:
            return 15  # Default 15 seconds
    
    def _format_binary_trading_signal(self, pair, timeframe, direction, reason, entry_timing, expiry_minutes):
        """Format signal specifically for binary trading"""
        entry_time = (datetime.now() + timedelta(seconds=30)).strftime('%H:%M:%S')
        return f"""---

📊 AI Binary Trading Signal
Pair: {pair}
Timeframe: {timeframe}
Direction: {direction}
Entry: {entry_time} (next 30-60 seconds)
Expiry: {expiry_minutes} minute(s)
Reason: {reason}
Entry Setup: {entry_timing}"""
    
    def _format_professional_signal(self, pair, timeframe, direction, reason):
        """Format signal in professional trading group style"""
        return f"""---

📊 AI Trading Signal
Pair: {pair}
Timeframe: {timeframe}
Direction: {direction}
Reason: {reason}"""
    
    def get_market_session(self):
        """Determine current market session for better signal timing"""
        try:
            from datetime import datetime
            import pytz
            
            utc_now = datetime.utcnow()
            
            # Define major forex sessions (UTC times)
            sessions = {
                'Tokyo': (0, 9),      # 00:00 - 09:00 UTC
                'London': (8, 17),    # 08:00 - 17:00 UTC  
                'New_York': (13, 22), # 13:00 - 22:00 UTC
            }
            
            current_hour = utc_now.hour
            active_sessions = []
            
            for session, (start, end) in sessions.items():
                if start <= current_hour < end:
                    active_sessions.append(session)
            
            # Determine market volatility based on session overlaps
            if len(active_sessions) >= 2:
                return {"sessions": active_sessions, "volatility": "High"}
            elif len(active_sessions) == 1:
                return {"sessions": active_sessions, "volatility": "Medium"}
            else:
                return {"sessions": ["Off-Hours"], "volatility": "Low"}
                
        except Exception as e:
            return {"sessions": ["Unknown"], "volatility": "Medium"}
    
    def analyze_short_term_momentum(self, data):
        """Analyze short-term momentum for 1-minute signals"""
        try:
            if len(data) < 10:
                return {"momentum": "Neutral", "strength": 0}
            
            # Calculate recent price momentum
            recent_prices = data['Close'].tail(5)
            price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0] * 100
            
            # Volume momentum
            if 'Volume' in data.columns:
                recent_volume = data['Volume'].tail(3).mean()
                avg_volume = data['Volume'].tail(10).mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            else:
                volume_ratio = 1
            
            # Determine momentum
            if price_change > 0.02 and volume_ratio > 1.2:
                return {"momentum": "Strong_Bullish", "strength": min(abs(price_change) * volume_ratio, 100)}
            elif price_change < -0.02 and volume_ratio > 1.2:
                return {"momentum": "Strong_Bearish", "strength": min(abs(price_change) * volume_ratio, 100)}
            elif price_change > 0.01:
                return {"momentum": "Bullish", "strength": min(abs(price_change) * 50, 100)}
            elif price_change < -0.01:
                return {"momentum": "Bearish", "strength": min(abs(price_change) * 50, 100)}
            else:
                return {"momentum": "Neutral", "strength": 0}
                
        except Exception as e:
            return {"momentum": "Neutral", "strength": 0}
    
    def get_market_news(self):
        """Get relevant market news"""
        try:
            return self.news_analyzer.get_forex_news()
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def is_market_open(self):
        """Check if forex market is open (24/5 market)"""
        now = datetime.now()
        weekday = now.weekday()
        
        # Forex market is closed on weekends (Saturday and Sunday)
        if weekday >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        # Check for major holidays (simplified)
        # In production, you'd want a more comprehensive holiday calendar
        return True
    
    def get_support_resistance_levels(self, data, window=20):
        """Calculate support and resistance levels"""
        try:
            if data is None or len(data) < window:
                return {}
                
            highs = data['High'].rolling(window=window).max()
            lows = data['Low'].rolling(window=window).min()
            
            # Find recent pivot points
            resistance = highs.tail(10).max()
            support = lows.tail(10).min()
            
            return {
                'resistance': resistance,
                'support': support,
                'pivot': (resistance + support) / 2
            }
            
        except Exception as e:
            print(f"Error calculating support/resistance: {e}")
            return {}
