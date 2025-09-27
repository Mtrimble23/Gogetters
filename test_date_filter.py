"""
Test date filtering functionality
"""

from news_scraper import YahooFinanceNewsScraper

def test_date_filter():
    print("🔍 Testing Date Filter Functionality")

    scraper = YahooFinanceNewsScraper()

    # Test specific date from 2023
    test_date = "2024-09-26"
    print(f"\n=== Testing date filter: {test_date} ===")

    for symbol in ['AAPL', 'TSLA']:
        print(f"\n--- {symbol} headlines from {test_date} ---")
        headlines = scraper.get_stock_news(symbol, max_headlines=10, date_filter=test_date)

        if headlines:
            print(f"Found {len(headlines)} headlines:")
            for i, headline_data in enumerate(headlines):
                print(f"{i+1}. {headline_data['headline']}")
                print(f"   Date: {headline_data['timestamp']}")
                print(f"   Source: {headline_data['source']}")
                print()
        else:
            print(f"No headlines found for {symbol} on {test_date}")

    # Compare with recent headlines
    print(f"\n=== Recent headlines (no date filter) ===")
    recent_headlines = scraper.get_stock_news('AAPL', max_headlines=3)

    if recent_headlines:
        print(f"Found {len(recent_headlines)} recent headlines:")
        for i, headline_data in enumerate(recent_headlines):
            print(f"{i+1}. {headline_data['headline']}")
            print(f"   Date: {headline_data['timestamp']}")
            print()

if __name__ == "__main__":
    test_date_filter()