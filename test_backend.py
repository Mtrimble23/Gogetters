#!/usr/bin/env python3
"""
Test client for the Financial Risk Analyzer Backend
Demonstrates how to interact with the API
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List


class FinancialRiskAPIClient:
    """Client for interacting with the Financial Risk Analyzer API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client"""
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        async with self.session.get(f"{self.base_url}/api/v1/health") as response:
            return await response.json()
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """Get detailed health information"""
        async with self.session.get(f"{self.base_url}/api/v1/health/detailed") as response:
            return await response.json()
    
    async def analyze_stock(self, symbol: str, include_sentiment: bool = True) -> Dict[str, Any]:
        """Analyze a single stock"""
        payload = {
            "symbol": symbol,
            "include_sentiment": include_sentiment
        }
        
        async with self.session.post(
            f"{self.base_url}/api/v1/analysis/analyze",
            json=payload
        ) as response:
            return await response.json()
    
    async def analyze_batch(self, symbols: List[str], include_sentiment: bool = True) -> Dict[str, Any]:
        """Analyze multiple stocks"""
        payload = {
            "symbols": symbols,
            "include_sentiment": include_sentiment
        }
        
        async with self.session.post(
            f"{self.base_url}/api/v1/analysis/analyze/batch",
            json=payload
        ) as response:
            return await response.json()
    
    async def get_analysis_result(self, symbol: str) -> Dict[str, Any]:
        """Get latest analysis result for a symbol"""
        async with self.session.get(
            f"{self.base_url}/api/v1/analysis/result/{symbol}"
        ) as response:
            return await response.json()
    
    async def get_analysis_history(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Get analysis history for a symbol"""
        async with self.session.get(
            f"{self.base_url}/api/v1/analysis/history/{symbol}?limit={limit}"
        ) as response:
            return await response.json()
    
    async def search_analyses(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search analyses with filters"""
        async with self.session.post(
            f"{self.base_url}/api/v1/analysis/search",
            json=filters
        ) as response:
            return await response.json()
    
    async def get_analyzed_symbols(self) -> Dict[str, Any]:
        """Get all analyzed symbols"""
        async with self.session.get(
            f"{self.base_url}/api/v1/analysis/symbols"
        ) as response:
            return await response.json()
    
    async def get_data_status(self) -> Dict[str, Any]:
        """Get data repository status"""
        async with self.session.get(
            f"{self.base_url}/api/v1/data/status"
        ) as response:
            return await response.json()
    
    async def migrate_data(self, from_repo: str = "fallback", to_repo: str = "primary") -> Dict[str, Any]:
        """Migrate data between repositories"""
        payload = {
            "from_repo": from_repo,
            "to_repo": to_repo
        }
        
        async with self.session.post(
            f"{self.base_url}/api/v1/data/migrate",
            json=payload
        ) as response:
            return await response.json()


async def demo_backend():
    """Demonstrate the backend functionality"""
    
    print("🔧 Financial Risk Analyzer Backend Demo")
    print("=" * 50)
    
    async with FinancialRiskAPIClient() as client:
        try:
            # Health check
            print("\n1. Health Check")
            health = await client.health_check()
            print(f"   Status: {health.get('status', 'unknown')}")
            
            # Detailed health check
            print("\n2. Detailed Health Check")
            detailed_health = await client.detailed_health_check()
            active_repo = detailed_health.get('repositories', {}).get('active_repository', 'unknown')
            print(f"   Active Repository: {active_repo}")
            
            # Analyze a single stock
            print("\n3. Single Stock Analysis")
            symbol = "AAPL"
            print(f"   Analyzing {symbol}...")
            analysis = await client.analyze_stock(symbol)
            
            if analysis.get('success'):
                print(f"   ✅ Analysis completed for {symbol}")
                risk_level = analysis['data']['financial_data'].get('risk_metrics', {}).get('risk_level')
                recommendation = analysis['data'].get('recommendation')
                print(f"   Risk Level: {risk_level}")
                print(f"   Recommendation: {recommendation}")
            else:
                print(f"   ❌ Analysis failed for {symbol}")
            
            # Batch analysis
            print("\n4. Batch Stock Analysis")
            batch_symbols = ["MSFT", "GOOGL", "TSLA"]
            print(f"   Analyzing batch: {batch_symbols}")
            batch_analysis = await client.analyze_batch(batch_symbols)
            
            if batch_analysis.get('success'):
                summary = batch_analysis.get('summary', {})
                print(f"   ✅ Batch analysis completed")
                print(f"   Successful: {summary.get('successful', 0)}")
                print(f"   Failed: {summary.get('failed', 0)}")
            else:
                print(f"   ❌ Batch analysis failed")
            
            # Get analyzed symbols
            print("\n5. Analyzed Symbols")
            symbols_result = await client.get_analyzed_symbols()
            if symbols_result.get('success'):
                symbols = symbols_result['data']['symbols']
                print(f"   Total symbols analyzed: {len(symbols)}")
                print(f"   Symbols: {symbols[:5]}{'...' if len(symbols) > 5 else ''}")
            
            # Search analyses
            print("\n6. Search Analyses")
            search_filters = {
                "risk_level": "medium"
            }
            search_results = await client.search_analyses(search_filters)
            if search_results.get('success'):
                count = search_results.get('count', 0)
                print(f"   Found {count} analyses with medium risk")
            
            # Data status
            print("\n7. Data Repository Status")
            data_status = await client.get_data_status()
            if data_status.get('success'):
                status_data = data_status['data']
                active_repo = status_data.get('active_repository', 'unknown')
                primary_available = status_data.get('primary_available', False)
                print(f"   Active Repository: {active_repo}")
                print(f"   Primary (Aerospike) Available: {primary_available}")
            
            print("\n✅ Demo completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print("Make sure the backend server is running on http://localhost:8000")


if __name__ == "__main__":
    # Check if aiohttp is available
    try:
        import aiohttp
        asyncio.run(demo_backend())
    except ImportError:
        print("❌ aiohttp not installed. Install with: pip install aiohttp")
        print("Running a simple demonstration instead...")
        
        print("\n🔧 Financial Risk Analyzer Backend Demo (Static)")
        print("=" * 50)
        print("Backend Structure Created:")
        print("  📁 backend/")
        print("    ├── 📁 models/        # Data models (FinancialData, RiskMetrics, etc.)")
        print("    ├── 📁 repositories/  # Data access layer (Aerospike + in-memory)")
        print("    ├── 📁 services/      # Business logic (FinancialAnalysisService)")
        print("    ├── 📁 api/          # FastAPI routes and endpoints")
        print("    └── 📁 config/       # Configuration management")
        print("\n🚀 To start the backend:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run backend: python run_backend.py")
        print("  3. Visit: http://localhost:8000/docs")
        print("\n🗄️  Aerospike Integration:")
        print("  - Ready to connect when your partner sets up the VM")
        print("  - Falls back to in-memory storage for now")
        print("  - Migration tools ready for data transfer")