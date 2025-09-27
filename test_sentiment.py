"""
Test script for sentiment analyzer
"""

from sentiment_analyzer import SentimentAnalyzer
import pandas as pd

def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample financial news"""

    # Initialize analyzer
    print("Initializing sentiment analyzer...")
    analyzer = SentimentAnalyzer(batch_size=16)

    # Test sample financial texts
    test_texts = [
        "Apple stock surges after record quarterly earnings beat expectations",
        "Tesla plunges on disappointing delivery numbers and production concerns",
        "Market volatility increases amid inflation concerns and Fed uncertainty",
        "Strong economic data boosts investor confidence in tech sector",
        "Banking stocks decline following credit risk warnings from analysts",
        "Bitcoin reaches new all-time high as institutional adoption grows",
        "US labor board withdraws claims Apple CEO violated employee rights"
    ]

    print("\n=== Testing Single Text Analysis ===")
    for text in test_texts[:2]:
        result = analyzer.analyze_single(text, source="test")
        print(f"Text: {text}")
        print(f"Sentiment: {result.label} (score: {result.score:.3f}, normalized: {result.normalized_score:.3f})")
        print()

    print("\n=== Testing Batch Analysis ===")
    batch_results = analyzer.analyze_batch(test_texts, sources=["test"] * len(test_texts))

    for i, result in enumerate(batch_results):
        print(f"Text {i+1}: {result.label} ({result.normalized_score:.3f})")

    # Test aggregated sentiment
    print(f"\nAggregated sentiment (weighted): {analyzer.get_aggregated_sentiment(batch_results):.3f}")

    print("\n=== Testing DataFrame Analysis ===")
    df = pd.DataFrame({
        'headline': test_texts,
        'source': ['Reuters', 'Bloomberg', 'CNBC', 'WSJ', 'Yahoo Finance', 'CoinDesk', 'Associated Press']
    })

    df_results = analyzer.analyze_dataframe(df, 'headline', 'source')
    print(df_results[['headline', 'sentiment_label', 'sentiment_normalized']].to_string())

    print("\n✅ Sentiment analyzer test completed successfully!")

if __name__ == "__main__":
    test_sentiment_analyzer()