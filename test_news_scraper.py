"""
Test script for Yahoo Finance news scraper
"""

from news_scraper import YahooFinanceNewsScraper

def test_news_scraper():
    """Test the news scraper with our target stocks"""

    print("🚀 Testing Yahoo Finance News Scraper")

    # Initialize scraper
    scraper = YahooFinanceNewsScraper()

    # Test single stock
    print("\n=== Testing Single Stock (AAPL) ===")
    aapl_headlines = scraper.get_stock_news('AAPL', max_headlines=5)

    print(f"Found {len(aapl_headlines)} headlines for AAPL:")
    for i, headline in enumerate(aapl_headlines):
        print(f"{i+1}. {headline['headline']}")
        print(f"   Source: {headline['source']}")
        print()

    # Test sentiment analysis
    print("\n=== Testing Sentiment Analysis ===")
    aapl_sentiment = scraper.get_multi_day_sentiment('AAPL')

    print(f"AAPL Sentiment Data:")
    print(f"  Current Day: {aapl_sentiment['current_day']:.3f}")
    print(f"  Previous Day: {aapl_sentiment['previous_day']:.3f}")
    print(f"  3-Day Momentum: {aapl_sentiment['three_day_momentum']:.3f}")
    print(f"  Headlines Analyzed: {aapl_sentiment['headlines_analyzed']}")

    # Test NEAT feature format
    print("\n=== Testing NEAT Feature Format ===")
    neat_features = scraper.create_neat_sentiment_features('AAPL')
    print(f"NEAT features for AAPL: {neat_features}")
    print(f"Feature format: [previous_day, current_day, momentum]")

    # Test multiple stocks
    print("\n=== Testing Multiple Stocks ===")
    test_stocks = ['AAPL', 'TSLA', 'NVDA']

    for stock in test_stocks:
        features = scraper.create_neat_sentiment_features(stock)
        print(f"{stock}: {[f'{f:.3f}' for f in features]}")

    print("\n✅ News scraper test completed!")

if __name__ == "__main__":
    test_news_scraper()