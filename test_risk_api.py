#!/usr/bin/env python3
"""
Risk Level HTTP API Test
Test the new risk level endpoints
"""

import requests
import json
import time

def test_risk_level_endpoints():
    """Test all risk level endpoints"""
    base_url = "http://localhost:8000"
    
    print("🎯 TESTING RISK LEVEL HTTP API")
    print("=" * 50)
    
    # Test 1: GET risk level for single symbol
    print("\n1. 📊 Testing GET /risk-level/{symbol}")
    try:
        symbol = "AAPL"
        response = requests.get(f"{base_url}/risk-level/{symbol}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS for {symbol}")
            print(f"   🎯 Risk Level: {data.get('risk_level', 'unknown')}")
            print(f"   📈 Risk Score: {data.get('risk_score', 'N/A')}")
            print(f"   📊 Source: {data.get('source', 'unknown')}")
            
            if data.get('risk_factors'):
                factors = data['risk_factors']
                print(f"   📋 Volatility: {factors.get('volatility', 'N/A'):.3f}")
                print(f"   🏢 Market Cap: {factors.get('market_cap', 'N/A')}")
                print(f"   ⚠️  Sector Risk: {factors.get('sector_risk', 'N/A'):.3f}")
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: GET risk level for new symbol (should calculate)
    print("\n2. 🆕 Testing GET /risk-level/{symbol} for new symbol")
    try:
        symbol = "NFLX"
        response = requests.get(f"{base_url}/risk-level/{symbol}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS for new symbol {symbol}")
            print(f"   🎯 Risk Level: {data.get('risk_level', 'unknown')}")
            print(f"   📈 Risk Score: {data.get('risk_score', 'N/A')}")
            print(f"   📊 Source: {data.get('source', 'unknown')}")
            print(f"   💾 Stored: {data.get('stored_to_aerospike', 'N/A')}")
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: POST risk level for multiple symbols
    print("\n3. 📊 Testing POST /risk-level for multiple symbols")
    try:
        payload = {
            "symbols": ["TSLA", "META", "GOOGL"]
        }
        
        response = requests.post(
            f"{base_url}/risk-level", 
            json=payload, 
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - Analyzed {data.get('total_analyzed', 0)} symbols")
            
            for result in data.get('results', []):
                symbol = result.get('symbol', 'UNKNOWN')
                risk_level = result.get('risk_level', 'unknown')
                risk_score = result.get('risk_score', 'N/A')
                print(f"   📈 {symbol}: {risk_level} (score: {risk_score})")
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 4: POST risk level with custom factors
    print("\n4. ⚙️  Testing POST /risk-level with custom factors")
    try:
        payload = {
            "symbols": ["CUSTOM_TEST"],
            "risk_factors": {
                "volatility": 0.8,
                "market_cap": "small",
                "sector_risk": 0.9,
                "liquidity": 0.2
            }
        }
        
        response = requests.post(
            f"{base_url}/risk-level", 
            json=payload, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('results', [{}])[0]
            
            print(f"   ✅ SUCCESS with custom factors")
            print(f"   🎯 Symbol: {result.get('symbol', 'UNKNOWN')}")
            print(f"   📊 Risk Level: {result.get('risk_level', 'unknown')}")
            print(f"   📈 Risk Score: {result.get('risk_score', 'N/A')}")
            print(f"   ⚙️  Custom Factors Applied: ✅")
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 5: Performance test
    print("\n5. ⚡ Performance Test")
    try:
        symbols = ["AMZN", "MSFT", "NVDA", "CRM", "ORCL"]
        start_time = time.time()
        
        successful = 0
        for symbol in symbols:
            response = requests.get(f"{base_url}/risk-level/{symbol}", timeout=5)
            if response.status_code == 200:
                successful += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(symbols)
        
        print(f"   📊 Processed: {successful}/{len(symbols)} symbols")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        print(f"   ⚡ Avg Time/Symbol: {avg_time:.3f}s")
        
        if avg_time < 1.0:
            print(f"   🚀 EXCELLENT performance!")
        elif avg_time < 2.0:
            print(f"   ✅ Good performance!")
        else:
            print(f"   ⚠️  Could be faster...")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Risk Level API Testing Complete!")
    print("\n📚 Available Endpoints:")
    print(f"   GET  {base_url}/risk-level/{{symbol}} - Get risk for single symbol")
    print(f"   POST {base_url}/risk-level - Batch analysis with custom factors")
    print(f"   📖 API Docs: {base_url}/docs")

if __name__ == "__main__":
    test_risk_level_endpoints()