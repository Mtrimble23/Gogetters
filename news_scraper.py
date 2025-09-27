"""
Yahoo Finance News Scraper for NEAT Trading System
Scrapes financial news for AAPL, AMZN, GOOGL, NVDA, META, TSLA
3-day rolling sentiment window for optimal trading signals
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import json
import logging
from pathlib import Path
from urllib.parse import urlencode
import re

from sentiment_analyzer import SentimentAnalyzer

class YahooFinanceNewsScraper:
    """Scrape financial news from Yahoo Finance for major tech stocks"""

    def __init__(self, cache_dir: str = "./news_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Target stocks
        self.stocks = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']

        # Setup sentiment analyzer
        self.sentiment_analyzer = SentimentAnalyzer()

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
            sentiment_data['current_day'] = np.mean(sentiment_scores[current_start:current_end])

            # Previous day sentiment (middle 1/3 of headlines)
            prev_start = current_end
            prev_end = max(prev_start + 1, 2 * num_scores // 3)
            if prev_start < num_scores:
                sentiment_data['previous_day'] = np.mean(sentiment_scores[prev_start:prev_end])
            else:
                sentiment_data['previous_day'] = sentiment_data['current_day']

            # Three day momentum (oldest 1/3 of headlines)
            momentum_start = prev_end
            if momentum_start < num_scores:
                sentiment_data['three_day_momentum'] = np.mean(sentiment_scores[momentum_start:])
            else:
                sentiment_data['three_day_momentum'] = np.mean(sentiment_scores)

            sentiment_data['headlines_analyzed'] = len(sentiment_scores)

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
        features = [np.clip(f, -1.0, 1.0) for f in features]

        return features