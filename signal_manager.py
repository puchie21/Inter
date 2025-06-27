from datetime import datetime, timedelta
import json
import os

class SignalManager:
    def __init__(self):
        self.signals_file = "signal_history.json"
        self.max_signals_per_hour = 3
        self.signals = self._load_signals()
    
    def _load_signals(self):
        """Load signal history from file"""
        try:
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime objects
                    for signal in data:
                        signal['timestamp'] = datetime.fromisoformat(signal['timestamp'])
                    return data
            return []
        except Exception as e:
            print(f"Error loading signals: {e}")
            return []
    
    def _save_signals(self):
        """Save signal history to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data = []
            for signal in self.signals:
                signal_copy = signal.copy()
                signal_copy['timestamp'] = signal['timestamp'].isoformat()
                data.append(signal_copy)
            
            with open(self.signals_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving signals: {e}")
    
    def add_signal(self, signal):
        """Add a new trading signal"""
        try:
            # Check rate limiting
            if not self._can_add_signal():
                print("Rate limit exceeded: Maximum 3 signals per hour")
                return False
            
            # Add signal to history
            self.signals.insert(0, signal)  # Insert at beginning for newest first
            
            # Keep only last 100 signals
            self.signals = self.signals[:100]
            
            # Save to file
            self._save_signals()
            
            print(f"Signal added: {signal['direction']} {signal['pair']} at {signal['confidence']:.1f}% confidence")
            return True
            
        except Exception as e:
            print(f"Error adding signal: {e}")
            return False
    
    def _can_add_signal(self):
        """Check if we can add a new signal (rate limiting)"""
        try:
            current_time = datetime.now()
            one_hour_ago = current_time - timedelta(hours=1)
            
            # Count signals in the last hour
            recent_signals = [
                signal for signal in self.signals
                if signal['timestamp'] > one_hour_ago
            ]
            
            return len(recent_signals) < self.max_signals_per_hour
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return True  # Allow signal if check fails
    
    def get_recent_signals(self, count=10):
        """Get recent trading signals"""
        try:
            return self.signals[:count]
        except Exception as e:
            print(f"Error getting recent signals: {e}")
            return []
    
    def get_signals_by_pair(self, pair, count=20):
        """Get signals for a specific currency pair"""
        try:
            pair_signals = [
                signal for signal in self.signals
                if signal.get('pair', '').upper() == pair.upper()
            ]
            return pair_signals[:count]
        except Exception as e:
            print(f"Error getting signals by pair: {e}")
            return []
    
    def get_signals_today(self):
        """Get signals from today"""
        try:
            today = datetime.now().date()
            today_signals = [
                signal for signal in self.signals
                if signal['timestamp'].date() == today
            ]
            return today_signals
        except Exception as e:
            print(f"Error getting today's signals: {e}")
            return []
    
    def get_performance_stats(self):
        """Calculate performance statistics"""
        try:
            total_signals = len(self.signals)
            today_signals = len(self.get_signals_today())
            
            if total_signals == 0:
                return {
                    'total_signals': 0,
                    'signals_today': 0,
                    'success_rate': 0.0,
                    'avg_confidence': 0.0,
                    'buy_signals': 0,
                    'sell_signals': 0
                }
            
            # Calculate success rate (simplified - in reality you'd track actual outcomes)
            high_confidence_signals = [
                signal for signal in self.signals
                if signal.get('confidence', 0) >= 80
            ]
            success_rate = (len(high_confidence_signals) / total_signals) * 100
            
            # Calculate average confidence
            confidences = [signal.get('confidence', 0) for signal in self.signals]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count buy/sell signals
            buy_signals = len([s for s in self.signals if s.get('direction') == 'BUY'])
            sell_signals = len([s for s in self.signals if s.get('direction') == 'SELL'])
            
            return {
                'total_signals': total_signals,
                'signals_today': today_signals,
                'success_rate': success_rate,
                'avg_confidence': avg_confidence,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals
            }
            
        except Exception as e:
            print(f"Error calculating performance stats: {e}")
            return {
                'total_signals': 0,
                'signals_today': 0,
                'success_rate': 0.0,
                'avg_confidence': 0.0,
                'buy_signals': 0,
                'sell_signals': 0
            }
    
    def cleanup_old_signals(self, days=7):
        """Remove signals older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            self.signals = [
                signal for signal in self.signals
                if signal['timestamp'] > cutoff_date
            ]
            self._save_signals()
            print(f"Cleaned up signals older than {days} days")
        except Exception as e:
            print(f"Error cleaning up old signals: {e}")
    
    def get_signal_statistics(self):
        """Get detailed signal statistics"""
        try:
            if not self.signals:
                return {}
            
            # Group by currency pairs
            pair_stats = {}
            for signal in self.signals:
                pair = signal.get('pair', 'Unknown')
                if pair not in pair_stats:
                    pair_stats[pair] = {
                        'count': 0,
                        'buy_count': 0,
                        'sell_count': 0,
                        'avg_confidence': 0
                    }
                
                pair_stats[pair]['count'] += 1
                if signal.get('direction') == 'BUY':
                    pair_stats[pair]['buy_count'] += 1
                else:
                    pair_stats[pair]['sell_count'] += 1
                pair_stats[pair]['avg_confidence'] += signal.get('confidence', 0)
            
            # Calculate averages
            for pair in pair_stats:
                if pair_stats[pair]['count'] > 0:
                    pair_stats[pair]['avg_confidence'] /= pair_stats[pair]['count']
            
            # Hourly distribution
            hourly_dist = {}
            for signal in self.signals:
                hour = signal['timestamp'].hour
                hourly_dist[hour] = hourly_dist.get(hour, 0) + 1
            
            return {
                'pair_statistics': pair_stats,
                'hourly_distribution': hourly_dist,
                'total_signals': len(self.signals)
            }
            
        except Exception as e:
            print(f"Error getting signal statistics: {e}")
            return {}
    
    def export_signals(self, format='json'):
        """Export signals to different formats"""
        try:
            if format == 'json':
                return json.dumps([
                    {
                        **signal,
                        'timestamp': signal['timestamp'].isoformat()
                    }
                    for signal in self.signals
                ], indent=2)
            elif format == 'csv':
                import pandas as pd
                df = pd.DataFrame(self.signals)
                return df.to_csv(index=False)
            else:
                return "Unsupported format"
        except Exception as e:
            print(f"Error exporting signals: {e}")
            return None
