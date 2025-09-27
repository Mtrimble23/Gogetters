#!/usr/bin/env python3
"""
Comprehensive Aerospike Integration Test Suite
Tests the backend with your Aerospike setup on port 3000
"""

import asyncio
import aiohttp
import json
import time
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta


class AerospikeBackendTester:
    """Comprehensive tester for the Aerospike-enabled backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the tester"""
        self.base_url = base_url
        self.session = None
        self.test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.results["tests_run"] += 1
        if success:
            self.results["tests_passed"] += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
            print(f"❌ {test_name}: FAILED {details}")
    
    async def test_health_check(self):
        """Test basic health check"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/health") as response:
                data = await response.json()
                success = response.status == 200 and data.get('status') == 'healthy'
                self.log_test("Health Check", success, f"Status: {data.get('status')}")
                return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    async def test_detailed_health_check(self):
        """Test detailed health check"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/health/detailed") as response:
                data = await response.json()
                success = response.status == 200
                repo_info = data.get('repositories', {})
                primary_available = repo_info.get('primary_available', False)
                
                details = f"Primary (Aerospike): {'Available' if primary_available else 'Not Available'}"
                self.log_test("Detailed Health Check", success, details)
                return success, primary_available
        except Exception as e:
            self.log_test("Detailed Health Check", False, str(e))
            return False, False
    
    async def test_switch_to_aerospike(self):
        """Test switching to Aerospike repository"""
        try:
            async with self.session.post(f"{self.base_url}/api/v1/data/switch/primary") as response:
                data = await response.json()
                success = response.status == 200 and data.get('success', False)
                active_repo = data.get('active_repository', 'unknown')
                
                details = f"Active Repository: {active_repo}"
                self.log_test("Switch to Aerospike", success, details)
                return success
        except Exception as e:
            self.log_test("Switch to Aerospike", False, str(e))
            return False
    
    async def test_single_stock_analysis(self, symbol: str = "AAPL"):
        """Test single stock analysis"""
        try:
            payload = {"symbol": symbol, "include_sentiment": True}
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/v1/analysis/analyze",
                json=payload
            ) as response:
                data = await response.json()
                end_time = time.time()
                
                success = response.status == 200 and data.get('success', False)
                
                if success:
                    analysis_data = data.get('data', {})
                    risk_level = analysis_data.get('financial_data', {}).get('risk_metrics', {}).get('risk_level')
                    recommendation = analysis_data.get('recommendation')
                    sentiment_score = analysis_data.get('overall_sentiment_score')
                    
                    details = f"{symbol} - Risk: {risk_level}, Rec: {recommendation}, Sentiment: {sentiment_score:.2f if sentiment_score else 'N/A'}, Time: {end_time - start_time:.2f}s"
                else:
                    details = data.get('detail', 'Unknown error')
                
                self.log_test(f"Single Analysis ({symbol})", success, details)
                return success, data if success else None
        except Exception as e:
            self.log_test(f"Single Analysis ({symbol})", False, str(e))
            return False, None
    
    async def test_batch_analysis(self, symbols: List[str] = None):
        """Test batch stock analysis"""
        if symbols is None:
            symbols = self.test_symbols[:5]  # First 5 symbols
        
        try:
            payload = {"symbols": symbols, "include_sentiment": True}
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/v1/analysis/analyze/batch",
                json=payload
            ) as response:
                data = await response.json()
                end_time = time.time()
                
                success = response.status == 200 and data.get('success', False)
                
                if success:
                    summary = data.get('summary', {})
                    successful = summary.get('successful', 0)
                    total = summary.get('total_requested', 0)
                    
                    details = f"{successful}/{total} successful, Time: {end_time - start_time:.2f}s"
                else:
                    details = data.get('detail', 'Unknown error')
                
                self.log_test("Batch Analysis", success, details)
                return success, data if success else None
        except Exception as e:
            self.log_test("Batch Analysis", False, str(e))
            return False, None
    
    async def test_data_retrieval(self, symbol: str = "AAPL"):
        """Test data retrieval from Aerospike"""
        try:
            # Get latest analysis
            async with self.session.get(
                f"{self.base_url}/api/v1/analysis/result/{symbol}"
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get('success', False)
                
                details = f"Retrieved analysis for {symbol}" if success else data.get('detail', 'Not found')
                self.log_test(f"Data Retrieval ({symbol})", success, details)
                return success
        except Exception as e:
            self.log_test(f"Data Retrieval ({symbol})", False, str(e))
            return False
    
    async def test_analysis_history(self, symbol: str = "AAPL", limit: int = 5):
        """Test analysis history retrieval"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/analysis/history/{symbol}?limit={limit}"
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get('success', False)
                
                if success:
                    count = data.get('count', 0)
                    details = f"Retrieved {count} historical records for {symbol}"
                else:
                    details = data.get('detail', 'Unknown error')
                
                self.log_test(f"Analysis History ({symbol})", success, details)
                return success
        except Exception as e:
            self.log_test(f"Analysis History ({symbol})", False, str(e))
            return False
    
    async def test_search_functionality(self):
        """Test search functionality"""
        try:
            # Search by risk level
            filters = {"risk_level": "medium"}
            
            async with self.session.post(
                f"{self.base_url}/api/v1/analysis/search",
                json=filters
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get('success', False)
                
                if success:
                    count = data.get('count', 0)
                    details = f"Found {count} records with medium risk"
                else:
                    details = data.get('detail', 'Unknown error')
                
                self.log_test("Search Functionality", success, details)
                return success
        except Exception as e:
            self.log_test("Search Functionality", False, str(e))
            return False
    
    async def test_symbols_endpoint(self):
        """Test symbols endpoint"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/analysis/symbols"
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get('success', False)
                
                if success:
                    symbols_data = data.get('data', {})
                    count = symbols_data.get('count', 0)
                    symbols = symbols_data.get('symbols', [])
                    
                    details = f"Found {count} unique symbols: {symbols[:3]}{'...' if len(symbols) > 3 else ''}"
                else:
                    details = data.get('detail', 'Unknown error')
                
                self.log_test("Symbols Endpoint", success, details)
                return success
        except Exception as e:
            self.log_test("Symbols Endpoint", False, str(e))
            return False
    
    async def test_data_status(self):
        """Test data repository status"""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/data/status"
            ) as response:
                data = await response.json()
                success = response.status == 200 and data.get('success', False)
                
                if success:
                    repo_data = data.get('data', {})
                    active_repo = repo_data.get('active_repository', 'unknown')
                    primary_available = repo_data.get('primary_available', False)
                    
                    details = f"Active: {active_repo}, Aerospike Available: {primary_available}"
                else:
                    details = data.get('detail', 'Unknown error')
                
                self.log_test("Data Status", success, details)
                return success, data.get('data', {}) if success else {}
        except Exception as e:
            self.log_test("Data Status", False, str(e))
            return False, {}
    
    async def test_aerospike_performance(self, num_analyses: int = 10):
        """Test Aerospike performance with multiple operations"""
        print(f"\n🚀 Performance Test: Running {num_analyses} analyses...")
        
        symbols = random.choices(self.test_symbols, k=num_analyses)
        start_time = time.time()
        
        successful = 0
        failed = 0
        
        for i, symbol in enumerate(symbols, 1):
            try:
                success, _ = await self.test_single_stock_analysis(symbol)
                if success:
                    successful += 1
                else:
                    failed += 1
                
                print(f"   Progress: {i}/{num_analyses} ({successful} successful, {failed} failed)")
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed += 1
                print(f"   Error on {symbol}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        success = successful > 0 and failed < successful
        details = f"{successful}/{num_analyses} successful, {total_time:.2f}s total, {total_time/num_analyses:.2f}s avg"
        
        self.log_test("Performance Test", success, details)
        return success
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Aerospike Backend Integration Tests")
        print("=" * 60)
        
        # Phase 1: Basic connectivity
        print("\n📡 Phase 1: Basic Connectivity Tests")
        await self.test_health_check()
        success, aerospike_available = await self.test_detailed_health_check()
        
        if not aerospike_available:
            print("\n⚠️  Aerospike not available, attempting to switch...")
            await self.test_switch_to_aerospike()
        
        # Phase 2: Data operations
        print("\n💾 Phase 2: Data Operations Tests")
        await self.test_single_stock_analysis("AAPL")
        await self.test_single_stock_analysis("MSFT")
        await self.test_batch_analysis(["GOOGL", "TSLA", "AMZN"])
        
        # Phase 3: Data retrieval
        print("\n🔍 Phase 3: Data Retrieval Tests")
        await self.test_data_retrieval("AAPL")
        await self.test_analysis_history("AAPL")
        await self.test_search_functionality()
        await self.test_symbols_endpoint()
        
        # Phase 4: Repository status
        print("\n📊 Phase 4: Repository Status Tests")
        await self.test_data_status()
        
        # Phase 5: Performance tests
        print("\n⚡ Phase 5: Performance Tests")
        await self.test_aerospike_performance(5)
        
        # Results summary
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['tests_run']}")
        print(f"Passed: {self.results['tests_passed']} ✅")
        print(f"Failed: {self.results['tests_failed']} ❌")
        print(f"Success Rate: {(self.results['tests_passed']/self.results['tests_run']*100):.1f}%")
        
        if self.results['errors']:
            print("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        return self.results['tests_failed'] == 0


async def main():
    """Main test runner"""
    print("🔧 Aerospike Backend Integration Tester")
    print(f"🎯 Target: http://localhost:8000")
    print(f"🗄️  Expected: Aerospike on port 3000, namespace=VTHacks, set=finance")
    print()
    
    try:
        async with AerospikeBackendTester() as tester:
            all_passed = await tester.run_all_tests()
            
            if all_passed:
                print("\n🎉 ALL TESTS PASSED! Your Aerospike backend is working perfectly!")
            else:
                print("\n⚠️  Some tests failed. Check the errors above.")
                
            return 0 if all_passed else 1
            
    except KeyboardInterrupt:
        print("\n⛔ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        return 1


if __name__ == "__main__":
    try:
        import aiohttp
        exit_code = asyncio.run(main())
        exit(exit_code)
    except ImportError:
        print("❌ aiohttp not installed. Install with: pip install aiohttp")
        print("Or install all requirements: pip install -r requirements.txt")
        exit(1)