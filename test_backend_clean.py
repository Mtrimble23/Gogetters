#!/usr/bin/env python3
"""
Comprehensive Test Suite for VTHacks26 Risk Level API
Tests all functionality of the clean backend
"""

import requests
import json
import time
import sys

def test_backend():
    """Run comprehensive backend tests"""
    base_url = "http://localhost:8000"
    
    print("🧪 VTHacks26 Risk Level API - Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    def run_test(name, test_func):
        nonlocal tests_passed, tests_failed
        print(f"\n🔍 {name}")
        try:
            success, details = test_func()
            if success:
                tests_passed += 1
                print(f"   ✅ PASSED - {details}")
            else:
                tests_failed += 1
                print(f"   ❌ FAILED - {details}")
        except Exception as e:
            tests_failed += 1
            print(f"   ❌ ERROR - {e}")
    
    # Test 1: Health Check
    def test_health():
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Status: {data.get('status')}, Aerospike: {data.get('aerospike_connected')}"
        return False, f"HTTP {response.status_code}"
    
    # Test 2: Root endpoint
    def test_root():
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Version: {data.get('version')}, Endpoints: {len(data.get('endpoints', {}))}"
        return False, f"HTTP {response.status_code}"
    
    # Test 3: Aerospike connection
    def test_aerospike():
        response = requests.get(f"{base_url}/test-aerospike", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Aerospike connection working"
            else:
                return False, f"Aerospike failed: {data.get('error', 'Unknown')}"
        return False, f"HTTP {response.status_code}"
    
    # Test 4: Single symbol analysis
    def test_single_analysis():
        response = requests.get(f"{base_url}/risk-level/AAPL", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                risk_level = data.get('risk_level')
                risk_score = data.get('risk_score')
                response_time = data.get('response_time')
                return True, f"Risk: {risk_level}, Score: {risk_score}, Time: {response_time}"
            else:
                return False, "Analysis unsuccessful"
        return False, f"HTTP {response.status_code}"
    
    # Test 5: Batch analysis
    def test_batch_analysis():
        payload = {"symbols": ["MSFT", "GOOGL", "TSLA"]}
        response = requests.post(f"{base_url}/risk-level", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data.get('summary', {})
                successful = summary.get('successful', 0)
                total_time = summary.get('total_time', 'N/A')
                return True, f"Analyzed {successful}/3 symbols, Time: {total_time}"
            else:
                return False, "Batch analysis unsuccessful"
        return False, f"HTTP {response.status_code}"
    
    # Test 6: Custom risk factors
    def test_custom_factors():
        payload = {
            "symbols": ["CUSTOM_TEST"],
            "risk_factors": {
                "volatility": 0.9,
                "market_cap": "small",
                "sector_risk": 0.8,
                "liquidity": 0.1
            }
        }
        response = requests.post(f"{base_url}/risk-level", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('results', [{}])[0]
                risk_level = result.get('risk_level')
                custom_used = data.get('summary', {}).get('custom_factors_used', False)
                return True, f"Custom factors: {custom_used}, Risk: {risk_level}"
            else:
                return False, "Custom factors test unsuccessful"
        return False, f"HTTP {response.status_code}"
    
    # Test 7: Performance test
    def test_performance():
        symbols = ["AMZN", "NVDA", "META", "NFLX", "CRM"]
        start_time = time.time()
        
        successful = 0
        for symbol in symbols:
            response = requests.get(f"{base_url}/risk-level/{symbol}", timeout=3)
            if response.status_code == 200:
                successful += 1
        
        total_time = time.time() - start_time
        avg_time = total_time / len(symbols)
        
        if successful == len(symbols) and avg_time < 0.5:
            return True, f"All {successful} successful, Avg: {avg_time:.3f}s/symbol"
        else:
            return False, f"Only {successful}/{len(symbols)} successful, Avg: {avg_time:.3f}s"
    
    # Test 8: Error handling
    def test_error_handling():
        # Test invalid symbol
        response = requests.get(f"{base_url}/risk-level/INVALID_VERY_LONG_SYMBOL_NAME", timeout=5)
        if response.status_code == 400:
            return True, "Properly handled invalid symbol"
        return False, f"Expected 400, got {response.status_code}"
    
    # Test 9: Stats endpoint
    def test_stats():
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            features = len(data.get('features', []))
            return True, f"Stats available, {features} features listed"
        return False, f"HTTP {response.status_code}"
    
    # Run all tests
    run_test("Health Check", test_health)
    run_test("Root Endpoint", test_root)
    run_test("Aerospike Connection", test_aerospike)
    run_test("Single Symbol Analysis", test_single_analysis)
    run_test("Batch Analysis", test_batch_analysis)
    run_test("Custom Risk Factors", test_custom_factors)
    run_test("Performance Test", test_performance)
    run_test("Error Handling", test_error_handling)
    run_test("Stats Endpoint", test_stats)
    
    # Results
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed} ✅")
    print(f"Failed: {tests_failed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! Backend is ready for production!")
        print("\n🚀 Your partner can now use:")
        print(f"   - API Documentation: {base_url}/docs")
        print(f"   - Risk Analysis: {base_url}/risk-level/AAPL")
        print(f"   - Batch Processing: POST {base_url}/risk-level")
    else:
        print(f"\n⚠️  {tests_failed} tests failed. Check the errors above.")
    
    return tests_failed == 0


if __name__ == "__main__":
    try:
        import requests
        success = test_backend()
        sys.exit(0 if success else 1)
    except ImportError:
        print("❌ requests not installed")
        print("Install with: pip3 install --break-system-packages requests")
        sys.exit(1)
    except requests.ConnectionError:
        print("❌ Cannot connect to backend")
        print("Make sure backend is running: python3 backend_server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⛔ Tests interrupted")
        sys.exit(1)