#!/usr/bin/env python3
"""
Simple Test for Aerospike Backend
Tests our simple backend server
"""

import time
import json

try:
    import requests
    print("🧪 Simple Aerospike Backend Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure backend is running: python3 simple_backend.py")
        exit(1)
    
    # Test 2: Aerospike connection
    print("\n2. Aerospike Connection Test")
    try:
        response = requests.get(f"{base_url}/test-aerospike", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Aerospike connection working")
                print(f"   📄 Test data: {data.get('data')}")
            else:
                print(f"   ❌ Aerospike connection failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Analysis test  
    print("\n3. Analysis Test")
    try:
        payload = {"symbol": "AAPL"}
        response = requests.post(f"{base_url}/test-analysis", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analysis = data.get('analysis', {})
                saved_to_aerospike = data.get('saved_to_aerospike', False)
                print(f"   ✅ Analysis completed for {analysis.get('symbol')}")
                print(f"   📊 Risk Level: {analysis.get('risk_level')}")
                print(f"   🎯 Recommendation: {analysis.get('recommendation')}")
                print(f"   💾 Saved to Aerospike: {'✅' if saved_to_aerospike else '❌'}")
            else:
                print(f"   ❌ Analysis failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Multiple symbols
    print("\n4. Multiple Symbol Test")
    symbols = ["AAPL", "MSFT", "GOOGL"]
    for symbol in symbols:
        try:
            payload = {"symbol": symbol}
            response = requests.post(f"{base_url}/test-analysis", json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('saved_to_aerospike'):
                    print(f"   ✅ {symbol} analyzed and saved to Aerospike")
                else:
                    print(f"   ⚠️  {symbol} analyzed but not saved to Aerospike")
            else:
                print(f"   ❌ {symbol} failed - HTTP {response.status_code}")
            
            time.sleep(0.1)  # Small delay
            
        except Exception as e:
            print(f"   ❌ {symbol} error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend Integration Test Complete!")
    print(f"📊 View API docs at: {base_url}/docs")
    print(f"🧪 Test Aerospike at: {base_url}/test-aerospike")

except ImportError:
    print("❌ requests not installed")
    print("Install with: pip3 install --break-system-packages requests")
    exit(1)
except KeyboardInterrupt:
    print("\n⛔ Test interrupted")
    exit(0)