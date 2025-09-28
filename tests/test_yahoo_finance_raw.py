#!/usr/bin/env python3
"""
Simple Yahoo Finance Test - No Backend, No Docker
Just test raw Yahoo Finance data fetching
"""

import yfinance as yf
import sys

def test_yahoo_finance():
    print("🧪 Testing Yahoo Finance Raw Data Fetching...")
    print("=" * 60)
    
    symbols = ["AAPL", "NVDA", "TSLA"]
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}:")
        try:
            # Create ticker
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Key metrics
            current_price = info.get('currentPrice')
            previous_close = info.get('previousClose')
            dividend_yield = info.get('dividendYield')
            beta = info.get('beta')
            pe_ratio = info.get('forwardPE', info.get('trailingPE'))
            market_cap = info.get('marketCap')
            
            print(f"   Price: ${current_price}")
            print(f"   Previous Close: ${previous_close}")
            print(f"   Dividend Yield: {dividend_yield}")
            print(f"   Beta: {beta}")
            print(f"   P/E Ratio: {pe_ratio}")
            print(f"   Market Cap: {market_cap:,}" if market_cap else "   Market Cap: N/A")
            
            # Test historical data
            hist = ticker.history(period='5d')
            print(f"   Historical Points: {len(hist)} days")
            
            # Verify we got real data
            if current_price and current_price > 0:
                print(f"   ✅ {symbol}: Real data retrieved")
            else:
                print(f"   ⚠️  {symbol}: Price data missing")
                
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {e}")
    
    print(f"\n{'='*60}")
    print("🎯 YAHOO FINANCE TEST COMPLETE")
    print("✅ If you see prices above, Yahoo Finance is working!")
    print("✅ Your partner will get real stock data")

if __name__ == "__main__":
    test_yahoo_finance()