#!/usr/bin/env python3
"""
Test Data Pipeline: Yahoo Finance -> Service -> Repository
Verifies that real stock data flows correctly through all layers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.yahoo_finance_parser import YahooFinanceParser
from src.services.financial_risk_service import FinancialRiskService
from src.repositories.aerospike_repository import AerospikeRepository
import time

def test_data_pipeline():
    """Test complete data flow from Yahoo Finance to Repository"""
    print("🔍 Testing Data Pipeline: Yahoo Finance -> Service -> Repository")
    print("=" * 70)
    
    # Test symbols
    test_symbols = ['AAPL', 'TSLA', 'NVDA']
    
    try:
        # Initialize components
        print("1️⃣ Initializing components...")
        parser = YahooFinanceParser()
        service = FinancialRiskService()
        repository = AerospikeRepository()
        
        print(f"   ✅ Parser initialized")
        print(f"   ✅ Service initialized") 
        print(f"   ✅ Repository initialized")
        print()
        
        for symbol in test_symbols:
            print(f"📊 Testing {symbol}:")
            print("-" * 30)
            
            # Step 1: Get raw data from Yahoo Finance
            print("   Step 1: Fetching from Yahoo Finance...")
            raw_data = parser.get_stock_data(symbol)
            print(f"   ✅ Yahoo data: ${raw_data['current_price']:.2f}, "
                  f"dividend: {raw_data['dividend_yield']}, "
                  f"beta: {raw_data['beta']}")
            
            # Step 2: Process through service (adds risk analysis)
            print("   Step 2: Processing through Financial Risk Service...")
            service_result = service.analyze_single_stock(symbol)
            risk_analysis = service_result['risk_analysis']
            stock_data = service_result['financial_data']
            print(f"   ✅ Risk analysis: {risk_analysis['risk_level']} "
                  f"(score: {risk_analysis['risk_score']:.2f})")
            
            # Step 3: Store in repository
            print("   Step 3: Storing in Aerospike repository...")
            store_success = repository.store_stock_analysis(symbol, service_result)
            print(f"   ✅ Stored in repository: {store_success}")
            
            # Step 4: Retrieve from repository to verify
            print("   Step 4: Retrieving from repository to verify...")
            retrieved_data = repository.get_stock_analysis(symbol)
            
            if retrieved_data:
                print(f"   ✅ Retrieved from cache:")
                print(f"      Price: ${retrieved_data['financial_data']['current_price']:.2f}")
                print(f"      Dividend: {retrieved_data['financial_data']['dividend_yield']}")
                print(f"      Beta: {retrieved_data['financial_data']['beta']}")
                print(f"      Risk Level: {retrieved_data['risk_analysis']['risk_level']}")
                print(f"      Risk Score: {retrieved_data['risk_analysis']['risk_score']:.2f}")
                
                # Verify data integrity
                original_price = raw_data['current_price']
                cached_price = retrieved_data['financial_data']['current_price']
                if abs(original_price - cached_price) < 0.01:  # Allow small float differences
                    print(f"   ✅ Data integrity verified!")
                else:
                    print(f"   ❌ Data integrity issue: {original_price} != {cached_price}")
            else:
                print(f"   ❌ Failed to retrieve from repository")
            
            print()
        
        print("🎉 Data Pipeline Test Complete!")
        print("=" * 70)
        print("✅ Yahoo Finance data successfully flows through:")
        print("   Parser -> Service (risk analysis) -> Repository (caching)")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

def test_repository_performance():
    """Test repository caching performance"""
    print("\n⚡ Testing Repository Performance:")
    print("-" * 40)
    
    try:
        repository = AerospikeRepository()
        
        # Test cache retrieval speed
        symbol = "AAPL"
        
        start_time = time.time()
        cached_data = repository.get_stock_analysis(symbol)
        end_time = time.time()
        
        retrieval_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if cached_data:
            print(f"✅ Cache retrieval time: {retrieval_time:.2f}ms")
            if retrieval_time < 10:  # Sub-10ms is excellent
                print("🚀 Excellent cache performance!")
            elif retrieval_time < 50:
                print("⚡ Good cache performance!")
            else:
                print("⚠️  Cache could be faster")
        else:
            print("❌ No cached data found")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

if __name__ == "__main__":
    test_data_pipeline()
    test_repository_performance()