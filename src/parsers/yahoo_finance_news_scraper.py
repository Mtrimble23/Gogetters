#!/usr/bin/env python3
"""
Yahoo Finance News Scraper for NEAT Trading System
Scrapes financial news for AAPL, AMZN, GOOGL, NVDA, META, TSLA
3-day rolling sentiment window for optimal trading signals
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
import re

# Optional imports for enhanced functionality
try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import numpy as np
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    print("Warning: Some dependencies missing. Using basic functionality.")

try:
    from .sentiment_analyzer import SentimentAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("Warning: Sentiment analyzer not available.")

try:
    from .gemini_summarizer import GeminiSummarizer
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Gemini summarizer not available.")

class YahooFinanceNewsScraper:
    """Scrape financial news from Yahoo Finance for major tech stocks"""

    def __init__(self, cache_dir: str = "./news_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Target stocks
        self.stocks = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']

        # Setup sentiment analyzer
        if SENTIMENT_AVAILABLE:
            self.sentiment_analyzer = SentimentAnalyzer()
        else:
            self.sentiment_analyzer = None

        # Setup Gemini summarizer
        if GEMINI_AVAILABLE:
            self.gemini_summarizer = GeminiSummarizer()
        else:
            self.gemini_summarizer = None

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        self.request_delay = 2  # seconds between requests

        # Headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def get_stock_news(self, symbol: str, max_headlines: int = 10, date_filter: str = None) -> List[Dict]:
        """Get recent news headlines for a specific stock"""

        try:
            import yfinance as yf

            self.logger.info(f"Fetching real news for {symbol}")

            # Get the stock ticker
            stock = yf.Ticker(symbol)

            # Get news from yfinance
            news = stock.news

            headlines = []

            if news and len(news) > 0:
                # Company name mapping for better filtering
                company_names = {
                    'AAPL': ['Apple', 'iPhone', 'iPad', 'Mac', 'iOS'],
                    'TSLA': ['Tesla', 'Elon Musk', 'Model', 'Cybertruck', 'Supercharger'],
                    'NVDA': ['NVIDIA', 'GeForce', 'RTX', 'AI chip', 'data center'],
                    'META': ['Meta', 'Facebook', 'Instagram', 'WhatsApp', 'VR', 'metaverse'],
                    'GOOGL': ['Google', 'Alphabet', 'YouTube', 'Chrome', 'Android', 'Search'],
                    'AMZN': ['Amazon', 'AWS', 'Prime', 'Bezos', 'e-commerce']
                }

                keywords = [symbol] + company_names.get(symbol, [symbol])

                for i, article in enumerate(news):
                    if len(headlines) >= max_headlines:
                        break

                    # Extract headline from nested content structure
                    content = article.get('content', {})
                    headline = content.get('title', 'No title available')

                    # Filter headlines to only include relevant ones
                    is_relevant = any(keyword.lower() in headline.lower() for keyword in keywords)

                    if not is_relevant:
                        continue

                    # Get publish time from content.pubDate
                    pub_date = content.get('pubDate')
                    if pub_date:
                        # Parse ISO format timestamp
                        try:
                            article_datetime = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                            timestamp = article_datetime.isoformat()
                        except:
                            timestamp = pub_date
                            article_datetime = datetime.now()
                    else:
                        # Fallback to current time minus hours
                        article_datetime = datetime.now() - timedelta(hours=len(headlines))
                        timestamp = article_datetime.isoformat()

                    # Apply date filter if specified
                    if date_filter:
                        try:
                            filter_date = datetime.fromisoformat(date_filter)
                            # Only include articles from the specified date (same day)
                            if article_datetime.date() != filter_date.date():
                                continue
                        except:
                            self.logger.warning(f"Invalid date filter format: {date_filter}")

                    # Get provider info
                    provider = content.get('provider', {})
                    source = provider.get('displayName', 'Yahoo Finance')

                    # Get URL
                    canonical_url = content.get('canonicalUrl', {})
                    url = canonical_url.get('url', '')

                    headlines.append({
                        'headline': headline,
                        'symbol': symbol,
                        'timestamp': timestamp,
                        'source': source,
                        'url': url
                    })

                self.logger.info(f"Retrieved {len(headlines)} real headlines for {symbol}")
                return headlines

            else:
                self.logger.warning(f"No news found for {symbol}, falling back to search")
                return self._fallback_news_search(symbol, max_headlines)

        except ImportError:
            self.logger.error("yfinance not installed, using mock data")
            return self._generate_mock_headlines(symbol, max_headlines)
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {e}")
            return self._fallback_news_search(symbol, max_headlines)

    def _fallback_news_search(self, symbol: str, max_headlines: int) -> List[Dict]:
        """Fallback method to search for stock news"""
        headlines = []

        try:
            # Try Yahoo Finance search
            search_url = f"https://finance.yahoo.com/lookup?s={symbol}%20news"
            response = requests.get(search_url, headers=self.headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for any text that mentions the stock symbol
                text_elements = soup.find_all(text=re.compile(symbol, re.IGNORECASE))

                for i, element in enumerate(text_elements[:max_headlines]):
                    parent = element.parent
                    if parent and len(element.strip()) > 20:
                        headlines.append({
                            'headline': element.strip()[:200],  # Limit length
                            'symbol': symbol,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'Yahoo Finance Search'
                        })

        except Exception as e:
            self.logger.warning(f"Fallback search failed for {symbol}: {e}")

        return headlines

    def _generate_mock_headlines(self, symbol: str, count: int) -> List[Dict]:
        """Generate mock headlines for testing when scraping fails"""

        mock_templates = {
            'AAPL': [
                "Apple reports strong iPhone sales in latest quarter",
                "Apple stock rises on new product announcement rumors",
                "Analysts upgrade Apple price target on AI integration",
                "Apple services revenue shows continued growth",
                "Apple faces regulatory challenges in European markets"
            ],
            'TSLA': [
                "Tesla delivers record number of vehicles this quarter",
                "Elon Musk announces new Tesla factory location",
                "Tesla stock volatile on production concerns",
                "Tesla Cybertruck production update expected soon",
                "Tesla energy business shows strong growth"
            ],
            'NVDA': [
                "NVIDIA earnings beat expectations on AI chip demand",
                "NVIDIA announces new AI partnership deal",
                "NVIDIA stock surges on data center revenue growth",
                "NVIDIA faces competition in AI chip market",
                "NVIDIA gaming revenue shows mixed results"
            ],
            'META': [
                "Meta reports user growth across all platforms",
                "Meta faces regulatory scrutiny over privacy practices",
                "Meta VR division shows promising revenue growth",
                "Meta announces new AI initiatives and investments",
                "Meta stock rises on advertising revenue strength"
            ],
            'GOOGL': [
                "Google Cloud revenue accelerates in latest quarter",
                "Google faces antitrust lawsuit over search practices",
                "Google announces breakthrough in quantum computing",
                "Google advertising revenue remains strong despite headwinds",
                "Google AI advancements drive investor optimism"
            ],
            'AMZN': [
                "Amazon Web Services revenue growth exceeds expectations",
                "Amazon Prime membership continues steady growth",
                "Amazon faces logistics challenges during peak season",
                "Amazon announces new warehouse automation technology",
                "Amazon stock rises on e-commerce recovery signs"
            ]
        }

        templates = mock_templates.get(symbol, mock_templates['AAPL'])

        headlines = []
        for i in range(min(count, len(templates))):
            headlines.append({
                'headline': templates[i],
                'symbol': symbol,
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'source': 'Mock Data'
            })

        self.logger.info(f"Generated {len(headlines)} mock headlines for {symbol}")
        return headlines

    def get_multi_day_sentiment(self, symbol: str, days_back: int = 3) -> Dict:
        """Get sentiment analysis for multiple days"""

        sentiment_data = {
            'symbol': symbol,
            'current_day': None,
            'previous_day': None,
            'three_day_momentum': None,
            'headlines_analyzed': 0
        }

        # Get recent headlines
        headlines = self.get_stock_news(symbol, max_headlines=15)

        if not headlines:
            self.logger.warning(f"No headlines found for {symbol}")
            return sentiment_data

        if self.sentiment_analyzer:
            # Analyze sentiment for all headlines
            headline_texts = [h['headline'] for h in headlines]
            sentiment_results = self.sentiment_analyzer.analyze_batch(headline_texts)

            # Extract sentiment scores
            sentiment_scores = [r.normalized_score for r in sentiment_results]

            if sentiment_scores:
                # Split headlines by recency to simulate different days
                num_scores = len(sentiment_scores)

                # Current day sentiment (most recent 1/3 of headlines)
                current_start = 0
                current_end = max(1, num_scores // 3)
                if ADVANCED_FEATURES:
                    sentiment_data['current_day'] = np.mean(sentiment_scores[current_start:current_end])
                else:
                    sentiment_data['current_day'] = sum(sentiment_scores[current_start:current_end]) / len(sentiment_scores[current_start:current_end])

                # Previous day sentiment (middle 1/3 of headlines)
                prev_start = current_end
                prev_end = max(prev_start + 1, 2 * num_scores // 3)
                if prev_start < num_scores:
                    if ADVANCED_FEATURES:
                        sentiment_data['previous_day'] = np.mean(sentiment_scores[prev_start:prev_end])
                    else:
                        sentiment_data['previous_day'] = sum(sentiment_scores[prev_start:prev_end]) / len(sentiment_scores[prev_start:prev_end])
                else:
                    sentiment_data['previous_day'] = sentiment_data['current_day']

                # Three day momentum (oldest 1/3 of headlines)
                momentum_start = prev_end
                if momentum_start < num_scores:
                    if ADVANCED_FEATURES:
                        sentiment_data['three_day_momentum'] = np.mean(sentiment_scores[momentum_start:])
                    else:
                        sentiment_data['three_day_momentum'] = sum(sentiment_scores[momentum_start:]) / len(sentiment_scores[momentum_start:])
                else:
                    if ADVANCED_FEATURES:
                        sentiment_data['three_day_momentum'] = np.mean(sentiment_scores)
                    else:
                        sentiment_data['three_day_momentum'] = sum(sentiment_scores) / len(sentiment_scores)

                sentiment_data['headlines_analyzed'] = len(sentiment_scores)
        else:
            # Basic fallback sentiment analysis
            sentiment_data['current_day'] = 0.1  # Slightly positive default
            sentiment_data['previous_day'] = 0.0
            sentiment_data['three_day_momentum'] = 0.05
            sentiment_data['headlines_analyzed'] = len(headlines)

        return sentiment_data

    def get_all_stocks_sentiment(self) -> Dict:
        """Get sentiment data for all tracked stocks"""

        all_sentiment = {}

        for symbol in self.stocks:
            self.logger.info(f"Processing sentiment for {symbol}")

            try:
                sentiment_data = self.get_multi_day_sentiment(symbol)
                all_sentiment[symbol] = sentiment_data

            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")
                # Provide neutral sentiment as fallback
                all_sentiment[symbol] = {
                    'symbol': symbol,
                    'current_day': 0.0,
                    'previous_day': 0.0,
                    'three_day_momentum': 0.0,
                    'headlines_analyzed': 0
                }

        return all_sentiment

    def create_neat_sentiment_features(self, symbol: str) -> List[float]:
        """Create sentiment features formatted for NEAT input"""

        sentiment_data = self.get_multi_day_sentiment(symbol)

        # Format for NEAT: [previous_day, current_day, momentum]
        features = [
            sentiment_data.get('previous_day', 0.0),
            sentiment_data.get('current_day', 0.0),
            sentiment_data.get('three_day_momentum', 0.0)
        ]

        # Normalize to [-1, 1] range (they should already be, but ensure it)
        if ADVANCED_FEATURES:
            features = [np.clip(f, -1.0, 1.0) for f in features]
        else:
            features = [max(-1.0, min(1.0, f)) for f in features]

        return features

    def generate_ai_summary(self, symbol: str) -> Dict[str, Any]:
        """Generate AI-powered investment summary"""

        # Get news and sentiment data
        headlines = self.get_stock_news(symbol, max_headlines=10)
        sentiment_data = self.get_multi_day_sentiment(symbol)

        if not headlines:
            return {
                'symbol': symbol,
                'summary': f"No recent news available for {symbol}. Consider checking market conditions and company fundamentals before making investment decisions.",
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'headlines_count': 0,
                'recommendation': 'HOLD - Insufficient data',
                'timestamp': datetime.now().isoformat()
            }

        # Analyze overall sentiment
        headline_texts = [h['headline'] for h in headlines]
        if self.sentiment_analyzer:
            aggregate_sentiment = self.sentiment_analyzer.get_aggregate_sentiment(headline_texts)
        else:
            # Basic fallback sentiment
            aggregate_sentiment = {
                'aggregate_sentiment': 0.1,
                'sentiment_label': 'positive',
                'average_confidence': 0.5
            }

        # Generate summary based on sentiment and headlines
        current_sentiment = sentiment_data.get('current_day', 0.0)
        previous_sentiment = sentiment_data.get('previous_day', 0.0)
        momentum = sentiment_data.get('three_day_momentum', 0.0)

        # Determine trend
        if current_sentiment > previous_sentiment + 0.1:
            trend = "improving"
        elif current_sentiment < previous_sentiment - 0.1:
            trend = "declining"
        else:
            trend = "stable"

        # Generate recommendation
        overall_sentiment = aggregate_sentiment['aggregate_sentiment']
        if overall_sentiment > 0.2:
            recommendation = "BUY - Positive sentiment"
        elif overall_sentiment < -0.2:
            recommendation = "SELL - Negative sentiment"
        else:
            recommendation = "HOLD - Neutral sentiment"

        # Generate AI summary using Gemini if available
        headline_texts = [h['headline'] for h in headlines]

        if self.gemini_summarizer and self.gemini_summarizer.available:
            print(f"INFO: Using Gemini AI to generate summary for {symbol}")
            summary = self.gemini_summarizer.generate_investment_summary(
                symbol=symbol,
                headlines=headline_texts,
                sentiment_score=overall_sentiment,
                financial_data=None  # Could add financial data here if needed
            )
        else:
            print(f"INFO: Using fallback summary generation for {symbol}")
            # Fallback to original logic
            sentiment_description = {
                'positive': 'bullish',
                'negative': 'bearish',
                'neutral': 'mixed'
            }.get(aggregate_sentiment['sentiment_label'], 'mixed')

            # Get most recent headline for context
            recent_headline = headlines[0]['headline'] if headlines else "No recent news"

            summary = f"Recent news sentiment for {symbol} appears {sentiment_description} with {trend} momentum. "
            summary += f"Latest: \"{recent_headline[:100]}{'...' if len(recent_headline) > 100 else ''}\" "
            summary += f"Market sentiment shows {abs(overall_sentiment):.1%} {'positive' if overall_sentiment > 0 else 'negative'} bias. "
            summary += f"Based on {len(headlines)} recent articles, current outlook suggests {recommendation.split(' - ')[0].lower()} consideration."

        return {
            'symbol': symbol,
            'summary': summary,
            'sentiment_score': overall_sentiment,
            'sentiment_label': aggregate_sentiment['sentiment_label'],
            'confidence': aggregate_sentiment['average_confidence'],
            'headlines_count': len(headlines),
            'recommendation': recommendation,
            'trend': trend,
            'recent_headlines': [h['headline'] for h in headlines[:3]],  # Top 3 headlines
            'timestamp': datetime.now().isoformat()
        }