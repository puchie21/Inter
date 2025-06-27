import requests
import json
from datetime import datetime, timedelta
import os
from textblob import TextBlob

class NewsAnalyzer:
    def __init__(self):
        # Use environment variables for API keys with fallbacks
        self.news_api_key = os.getenv("NEWS_API_KEY", "demo_key")
        self.base_url = "https://newsapi.org/v2"
        self.forex_keywords = [
            "forex", "currency", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD",
            "federal reserve", "ECB", "Bank of England", "interest rate", "inflation",
            "monetary policy", "central bank", "employment", "GDP", "trade"
        ]
    
    def get_forex_news(self, hours_back=24):
        """Get recent forex-related news"""
        try:
            if self.news_api_key == "demo_key":
                # Return sample news data when no API key is available
                return self._get_sample_news()
            
            from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            
            # Search for forex-related news
            params = {
                'q': 'forex OR currency OR "foreign exchange" OR "central bank"',
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.news_api_key
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Filter and format articles
                formatted_news = []
                for article in articles[:10]:  # Limit to 10 articles
                    if self._is_forex_relevant(article.get('title', '') + ' ' + article.get('description', '')):
                        formatted_news.append({
                            'title': article.get('title', 'No title'),
                            'description': article.get('description', 'No description'),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'time': self._format_time(article.get('publishedAt')),
                            'url': article.get('url', ''),
                            'sentiment': self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', ''))
                        })
                
                return formatted_news
            else:
                print(f"News API error: {response.status_code}")
                return self._get_sample_news()
                
        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._get_sample_news()
    
    def _get_sample_news(self):
        """Return sample news data when API is not available"""
        return [
            {
                'title': 'Federal Reserve Maintains Interest Rates',
                'description': 'The Fed holds rates steady amid inflation concerns',
                'source': 'Reuters',
                'time': '2 hours ago',
                'url': '#',
                'sentiment': 0.1
            },
            {
                'title': 'EUR/USD Reaches New Weekly High',
                'description': 'Euro strengthens against dollar following ECB comments',
                'source': 'Bloomberg',
                'time': '4 hours ago',
                'url': '#',
                'sentiment': 0.3
            },
            {
                'title': 'Bank of England Signals Rate Cut Possibility',
                'description': 'BoE Governor hints at potential monetary easing',
                'source': 'Financial Times',
                'time': '6 hours ago',
                'url': '#',
                'sentiment': -0.2
            }
        ]
    
    def _is_forex_relevant(self, text):
        """Check if the text is relevant to forex trading"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.forex_keywords)
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of the given text"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0  # Neutral sentiment if analysis fails
    
    def _format_time(self, timestamp_str):
        """Format timestamp to relative time"""
        try:
            if not timestamp_str:
                return "Unknown time"
                
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timestamp.tzinfo)
            diff = now - timestamp
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
                
        except Exception as e:
            return "Unknown time"
    
    def get_market_sentiment(self):
        """Get overall market sentiment from recent news"""
        try:
            news = self.get_forex_news(hours_back=6)  # Last 6 hours
            
            if not news:
                return 0.0
            
            sentiments = [article['sentiment'] for article in news if 'sentiment' in article]
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                return avg_sentiment
            
            return 0.0
            
        except Exception as e:
            print(f"Error calculating market sentiment: {e}")
            return 0.0
    
    def get_high_impact_events(self):
        """Get high-impact economic events (simplified)"""
        try:
            # In a real implementation, you'd connect to an economic calendar API
            # For now, return sample high-impact events
            events = [
                {
                    'time': '15:30',
                    'event': 'US Non-Farm Payrolls',
                    'impact': 'High',
                    'previous': '150K',
                    'forecast': '180K',
                    'currency': 'USD'
                },
                {
                    'time': '13:30',
                    'event': 'ECB Interest Rate Decision',
                    'impact': 'High',
                    'previous': '4.50%',
                    'forecast': '4.25%',
                    'currency': 'EUR'
                }
            ]
            
            return events
            
        except Exception as e:
            print(f"Error fetching economic events: {e}")
            return []
    
    def analyze_news_impact(self, currency_pair):
        """Analyze potential news impact on specific currency pair"""
        try:
            news = self.get_forex_news(hours_back=2)  # Very recent news
            
            # Extract currencies from pair (e.g., "EURUSD=X" -> ["EUR", "USD"])
            base_currency = currency_pair[:3]
            quote_currency = currency_pair[3:6] if len(currency_pair) >= 6 else currency_pair[4:7]
            
            relevant_news = []
            for article in news:
                text = (article.get('title', '') + ' ' + article.get('description', '')).upper()
                if base_currency in text or quote_currency in text:
                    relevant_news.append(article)
            
            if relevant_news:
                avg_sentiment = sum(article['sentiment'] for article in relevant_news) / len(relevant_news)
                return {
                    'impact_level': 'High' if abs(avg_sentiment) > 0.3 else 'Medium' if abs(avg_sentiment) > 0.1 else 'Low',
                    'sentiment': avg_sentiment,
                    'relevant_articles': len(relevant_news)
                }
            
            return {
                'impact_level': 'Low',
                'sentiment': 0.0,
                'relevant_articles': 0
            }
            
        except Exception as e:
            print(f"Error analyzing news impact: {e}")
            return {
                'impact_level': 'Unknown',
                'sentiment': 0.0,
                'relevant_articles': 0
            }
