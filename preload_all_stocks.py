#!/usr/bin/env python3
"""
Preload All Stocks Script
Loads all supported stocks into Aerospike database with consistent formatting
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8000"
SUPPORTED_STOCKS = ["AAPL", "AMZN", "GOOGL", "NVDA", "META", "TSLA"]

def preload_all_stocks():
    """Load all supported stocks into the database"""
    print("🚀 Preloading all stocks into Aerospike database...")
    print("=" * 60)
    
    results = []
    
    for i, symbol in enumerate(SUPPORTED_STOCKS, 1):
        print(f"📊 [{i}/{len(SUPPORTED_STOCKS)}] Loading {symbol}...")
        
        try:
            # Make API call
            response = requests.get(f"{API_BASE}/risk-level/{symbol}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key info
                result = {
                    "symbol": data.get("symbol"),
                    "success": data.get("success"),
                    "source": data.get("source", "unknown"),
                    "response_time": data.get("response_time", "N/A"),
                    "has_financial_data": "financial_data" in data.get("data", {}),
                    "has_risk_analysis": "risk_analysis" in data.get("data", {}),
                    "current_price": None,
                    "risk_level": None
                }
                
                # Extract nested data if available
                if "data" in data and data["data"]:
                    if "financial_data" in data["data"]:
                        result["current_price"] = data["data"]["financial_data"].get("current_price")
                    if "risk_analysis" in data["data"]:
                        result["risk_level"] = data["data"]["risk_analysis"].get("risk_level")
                
                results.append(result)
                
                print(f"   ✅ {symbol}: {result['source']} - ${result['current_price']} - {result['risk_level']} risk")
                
            else:
                print(f"   ❌ {symbol}: HTTP {response.status_code}")
                results.append({
                    "symbol": symbol,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ {symbol}: Error - {str(e)}")
            results.append({
                "symbol": symbol,
                "success": False,
                "error": str(e)
            })
        
        # Small delay between requests
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("📊 PRELOAD RESULTS")
    print("=" * 60)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"✅ Successful: {len(successful)}/{len(SUPPORTED_STOCKS)}")
    print(f"❌ Failed: {len(failed)}/{len(SUPPORTED_STOCKS)}")
    
    if successful:
        print("\n📈 Loaded Stocks:")
        for result in successful:
            print(f"  • {result['symbol']}: ${result['current_price']} ({result['risk_level']} risk)")
    
    if failed:
        print("\n❌ Failed Stocks:")
        for result in failed:
            print(f"  • {result['symbol']}: {result.get('error', 'Unknown error')}")
    
    # Check cache status
    print("\n🗄️ Verifying cache status...")
    try:
        stats_response = requests.get(f"{API_BASE}/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            cached_symbols = stats.get("database", {}).get("cached_symbols", [])
            cache_count = stats.get("database", {}).get("cache_count", 0)
            
            print(f"   📊 Cached symbols: {cache_count}")
            print(f"   📂 Symbols in cache: {', '.join(cached_symbols)}")
            
            if cache_count == len(SUPPORTED_STOCKS):
                print("   🎉 All stocks successfully cached!")
            else:
                missing = [s for s in SUPPORTED_STOCKS if s not in cached_symbols]
                print(f"   ⚠️  Missing from cache: {', '.join(missing)}")
                
    except Exception as e:
        print(f"   ❌ Could not verify cache: {e}")
    
    print("\n✅ Preload complete!")
    return len(successful) == len(SUPPORTED_STOCKS)

if __name__ == "__main__":
    success = preload_all_stocks()
    exit(0 if success else 1)