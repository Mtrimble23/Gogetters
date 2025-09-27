"""
Debug yfinance API to see the actual structure
"""

import yfinance as yf
import json

def debug_yfinance_structure():
    print("🔍 Debugging yfinance news structure for TSLA")

    stock = yf.Ticker("TSLA")
    news = stock.news

    print(f"Found {len(news)} news articles")

    if news:
        print("\n=== First article structure ===")
        first_article = news[0]
        print(json.dumps(first_article, indent=2, default=str))

        print("\n=== Available keys ===")
        for key in first_article.keys():
            print(f"- {key}: {type(first_article[key])}")

    print("\n=== Testing different title fields ===")
    for i, article in enumerate(news[:3]):
        print(f"\nArticle {i+1}:")
        # Try different possible title fields
        title_fields = ['title', 'headline', 'summary', 'text']
        for field in title_fields:
            if field in article:
                print(f"  {field}: {article[field]}")

        # Check if there's a uuid or other identifier
        if 'uuid' in article:
            print(f"  uuid: {article['uuid']}")

if __name__ == "__main__":
    debug_yfinance_structure()