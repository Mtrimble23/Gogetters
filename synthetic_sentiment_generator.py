"""
Synthetic Sentiment Generator - Just the sentiment scores!
Real stock data from yfinance + synthetic sentiment for training
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import random

class SyntheticSentimentGenerator:
    """Generate realistic sentiment patterns for any date"""

    def __init__(self, seed: int = 42):
        self.seed = seed

        # Event types and their sentiment patterns
        self.event_patterns = {
            'earnings_beat': [0.4, 0.85, 0.75],      # Previous neutral, current very positive, momentum positive
            'earnings_miss': [0.6, 0.15, 0.25],     # Previous OK, current very negative, momentum bad
            'product_launch': [0.5, 0.75, 0.65],    # Neutral to positive excitement
            'regulatory_news': [0.45, 0.3, 0.35],   # Uncertainty and concern
            'analyst_upgrade': [0.5, 0.7, 0.6],     # Positive but not huge
            'market_selloff': [0.4, 0.25, 0.3],     # General negative sentiment
            'normal_day': [0.5, 0.5, 0.5]           # Neutral baseline
        }

        # Stock characteristics (how often events happen)
        self.stock_event_rates = {
            'AAPL': 0.15,   # Apple - steady, fewer big events
            'TSLA': 0.25,   # Tesla - very volatile, lots of news
            'NVDA': 0.20,   # NVIDIA - AI hype, frequent events
            'META': 0.18,   # Meta - social media controversies
            'GOOGL': 0.12,  # Google - more stable
            'AMZN': 0.16    # Amazon - moderate activity
        }

    def get_sentiment_for_date(self, symbol: str, date: str) -> List[float]:
        """
        Generate [previous_day, current_day, momentum] sentiment for any date
        Uses date + symbol as seed for reproducible results
        """

        # Create deterministic seed from date and symbol
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_seed = int(date_obj.strftime("%Y%m%d")) + hash(symbol) % 10000

        # Set random seed for this specific date+symbol
        np.random.seed(date_seed)
        random.seed(date_seed)

        # Determine if it's an "event" day
        event_rate = self.stock_event_rates.get(symbol, 0.15)

        if np.random.random() < event_rate:
            # Pick a random event type
            event_types = list(self.event_patterns.keys())[:-1]  # Exclude 'normal_day'
            event = random.choice(event_types)
        else:
            event = 'normal_day'

        # Get base sentiment pattern
        base_sentiment = self.event_patterns[event].copy()

        # Add some realistic noise (±10%)
        noise = np.random.normal(0, 0.08, 3)
        sentiment = [max(0.0, min(1.0, base + n)) for base, n in zip(base_sentiment, noise)]

        return sentiment

    def generate_sentiment_batch(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Generate sentiment for a date range"""

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        sentiment_data = {}
        current_date = start_dt

        while current_date <= end_dt:
            # Skip weekends
            if current_date.weekday() < 5:
                date_str = current_date.strftime("%Y-%m-%d")
                sentiment_data[date_str] = self.get_sentiment_for_date(symbol, date_str)

            current_date += timedelta(days=1)

        return sentiment_data

if __name__ == "__main__":
    # Test the generator
    generator = SyntheticSentimentGenerator()

    # Test single date
    print("🔍 Testing Synthetic Sentiment Generator")

    test_date = "2024-01-15"
    for symbol in ['AAPL', 'TSLA', 'NVDA']:
        sentiment = generator.get_sentiment_for_date(symbol, test_date)
        print(f"{symbol} on {test_date}: {sentiment}")

    print("\n📊 Testing batch generation")

    # Test batch generation
    batch_data = generator.generate_sentiment_batch('AAPL', '2024-01-01', '2024-01-07')
    for date, sentiment in batch_data.items():
        print(f"AAPL {date}: {sentiment}")

    print("\n✅ Synthetic sentiment generator working!")