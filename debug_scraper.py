"""
Debug script to see what's happening with sentiment analysis
"""

from news_scraper import YahooFinanceNewsScraper
from sentiment_analyzer import SentimentAnalyzer

def debug_sentiment_pipeline():
    """Debug each step of the sentiment analysis"""

    print("🔍 Debugging Sentiment Analysis Pipeline")

    # Test 1: Check sentiment analyzer directly
    print("\n=== Test 1: Direct Sentiment Analyzer ===")
    analyzer = SentimentAnalyzer()

    test_headlines = [
        "Tesla stock surges on strong delivery numbers",
        "Apple faces challenges in China market",
        "NVIDIA reports record AI chip sales"
    ]

    for headline in test_headlines:
        result = analyzer.analyze_single(headline)
        print(f"Headline: {headline}")
        print(f"Sentiment: {result.label} (score: {result.score:.3f}, normalized: {result.normalized_score:.3f})")
        print()

    # Test 2: Check scraper headlines
    print("\n=== Test 2: Scraper Headlines ===")
    scraper = YahooFinanceNewsScraper()

    tsla_headlines = scraper.get_stock_news('TSLA', max_headlines=3)
    print(f"Found {len(tsla_headlines)} TSLA headlines:")

    for i, headline_data in enumerate(tsla_headlines):
        print(f"{i+1}. {headline_data['headline']}")
        print(f"   Length: {len(headline_data['headline'])} characters")
        print(f"   Source: {headline_data['source']}")

        # Test sentiment on this headline
        result = analyzer.analyze_single(headline_data['headline'])
        print(f"   Sentiment: {result.label} (normalized: {result.normalized_score:.3f})")
        print()

    # Test 3: Check multi-day sentiment function with detailed breakdown
    print("\n=== Test 3: Multi-day Sentiment Function ===")

    # Get headlines first
    tsla_headlines = scraper.get_stock_news('TSLA', max_headlines=15)
    print(f"Got {len(tsla_headlines)} headlines for detailed analysis:")

    for i, headline_data in enumerate(tsla_headlines):
        headline = headline_data['headline']
        result = analyzer.analyze_single(headline)
        print(f"{i+1}. {headline}")
        print(f"   Raw sentiment: {result.label} (score: {result.score:.3f}, normalized: {result.normalized_score:.3f})")

    print("\n--- Sentiment Grouping ---")
    # Analyze how they're grouped into time periods
    headline_texts = [h['headline'] for h in tsla_headlines]
    sentiment_results = analyzer.analyze_batch(headline_texts)
    sentiment_scores = [r.normalized_score for r in sentiment_results]

    num_scores = len(sentiment_scores)
    current_end = max(1, num_scores // 3)
    prev_start = current_end
    prev_end = max(prev_start + 1, 2 * num_scores // 3)
    momentum_start = prev_end

    print(f"Total headlines: {num_scores}")
    print(f"Current day (0 to {current_end}): {sentiment_scores[0:current_end]} -> avg: {sum(sentiment_scores[0:current_end])/len(sentiment_scores[0:current_end]):.3f}")
    print(f"Previous day ({prev_start} to {prev_end}): {sentiment_scores[prev_start:prev_end]} -> avg: {sum(sentiment_scores[prev_start:prev_end])/len(sentiment_scores[prev_start:prev_end]):.3f}")
    print(f"3-day momentum ({momentum_start} to end): {sentiment_scores[momentum_start:]} -> avg: {sum(sentiment_scores[momentum_start:])/len(sentiment_scores[momentum_start:]):.3f}")

    sentiment_data = scraper.get_multi_day_sentiment('TSLA')
    print(f"\nFinal sentiment data:")
    for key, value in sentiment_data.items():
        print(f"  {key}: {value}")

    # Test 4: Check NEAT features
    print("\n=== Test 4: NEAT Features ===")
    neat_features = scraper.create_neat_sentiment_features('TSLA')
    print(f"NEAT features: {neat_features}")

    print("\n✅ Debug completed!")

if __name__ == "__main__":
    debug_sentiment_pipeline()