import pandas as pd
import numpy as np

class TechnicalIndicators:
    def __init__(self):
        pass
    
    def calculate_sma(self, data, period):
        """Calculate Simple Moving Average"""
        try:
            return data.rolling(window=period).mean()
        except Exception as e:
            print(f"Error calculating SMA: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        try:
            return data.ewm(span=period).mean()
        except Exception as e:
            print(f"Error calculating EMA: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_rsi(self, data, period=14):
        """Calculate Relative Strength Index"""
        try:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            print(f"Error calculating RSI: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            exp1 = data.ewm(span=fast).mean()
            exp2 = data.ewm(span=slow).mean()
            
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=signal).mean()
            macd_hist = macd - macd_signal
            
            return {
                'MACD': macd,
                'MACD_Signal': macd_signal,
                'MACD_Hist': macd_hist
            }
        except Exception as e:
            print(f"Error calculating MACD: {e}")
            return {
                'MACD': pd.Series(index=data.index, dtype=float),
                'MACD_Signal': pd.Series(index=data.index, dtype=float),
                'MACD_Hist': pd.Series(index=data.index, dtype=float)
            }
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        try:
            sma = self.calculate_sma(data, period)
            rolling_std = data.rolling(window=period).std()
            
            upper_band = sma + (rolling_std * std_dev)
            lower_band = sma - (rolling_std * std_dev)
            
            return {
                'BB_Upper': upper_band,
                'BB_Middle': sma,
                'BB_Lower': lower_band
            }
        except Exception as e:
            print(f"Error calculating Bollinger Bands: {e}")
            return {
                'BB_Upper': pd.Series(index=data.index, dtype=float),
                'BB_Middle': pd.Series(index=data.index, dtype=float),
                'BB_Lower': pd.Series(index=data.index, dtype=float)
            }
    
    def calculate_stochastic(self, high, low, close, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return {
                'Stoch_K': k_percent,
                'Stoch_D': d_percent
            }
        except Exception as e:
            print(f"Error calculating Stochastic: {e}")
            return {
                'Stoch_K': pd.Series(index=close.index, dtype=float),
                'Stoch_D': pd.Series(index=close.index, dtype=float)
            }
    
    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            return pd.Series(index=close.index, dtype=float)
    
    def calculate_williams_r(self, high, low, close, period=14):
        """Calculate Williams %R"""
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            
            return williams_r
        except Exception as e:
            print(f"Error calculating Williams %R: {e}")
            return pd.Series(index=close.index, dtype=float)
    
    def calculate_cci(self, high, low, close, period=20):
        """Calculate Commodity Channel Index"""
        try:
            typical_price = (high + low + close) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mad = typical_price.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            
            cci = (typical_price - sma_tp) / (0.015 * mad)
            
            return cci
        except Exception as e:
            print(f"Error calculating CCI: {e}")
            return pd.Series(index=close.index, dtype=float)
    
    def detect_patterns(self, data):
        """Detect basic chart patterns"""
        try:
            patterns = {}
            
            if len(data) < 20:
                return patterns
            
            # Simple pattern detection
            recent_highs = data['High'].tail(5)
            recent_lows = data['Low'].tail(5)
            
            # Uptrend detection
            if recent_lows.is_monotonic_increasing:
                patterns['uptrend'] = True
            
            # Downtrend detection
            if recent_highs.is_monotonic_decreasing:
                patterns['downtrend'] = True
            
            # Support/Resistance levels
            resistance_level = data['High'].tail(20).max()
            support_level = data['Low'].tail(20).min()
            
            patterns['resistance'] = resistance_level
            patterns['support'] = support_level
            
            return patterns
            
        except Exception as e:
            print(f"Error detecting patterns: {e}")
            return {}
    
    def calculate_momentum(self, data, period=10):
        """Calculate Price Momentum"""
        try:
            momentum = data / data.shift(period) - 1
            return momentum * 100
        except Exception as e:
            print(f"Error calculating momentum: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_roc(self, data, period=12):
        """Calculate Rate of Change"""
        try:
            roc = ((data - data.shift(period)) / data.shift(period)) * 100
            return roc
        except Exception as e:
            print(f"Error calculating ROC: {e}")
            return pd.Series(index=data.index, dtype=float)
