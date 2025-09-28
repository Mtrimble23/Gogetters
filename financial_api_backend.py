#!/usr/bin/env python3
"""
VTHacks26 Financial Risk Analysis API - Main Backend
Clean architecture with real Yahoo Finance data
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime, timezone

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip3 install --break-system-packages fastapi uvicorn yfinance pandas numpy")
    exit(1)

from services.financial_risk_service import FinancialRiskService
from repositories.aerospike_repository import AerospikeRepository

# Import news scraper with error handling and logging
try:
    from parsers.yahoo_finance_news_scraper import YahooFinanceNewsScraper
    NEWS_SCRAPER_AVAILABLE = True
    print("SUCCESS: News scraper imported successfully")
except ImportError as e:
    NEWS_SCRAPER_AVAILABLE = False
    print(f"ERROR: Failed to import news scraper: {e}")
except Exception as e:
    NEWS_SCRAPER_AVAILABLE = False
    print(f"ERROR: Unexpected error importing news scraper: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="VTHacks26 Financial Risk Analysis API",
    description="Real-time stock risk analysis with Yahoo Finance integration",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
print("INIT: Initializing services...")
financial_service = FinancialRiskService()
print("SUCCESS: Financial service initialized")

aerospike_repo = AerospikeRepository()
print("SUCCESS: Aerospike repository initialized")

# Initialize news scraper conditionally
if NEWS_SCRAPER_AVAILABLE:
    try:
        news_scraper = YahooFinanceNewsScraper()
        print("SUCCESS: News scraper initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize news scraper: {e}")
        news_scraper = None
else:
    print("WARNING: News scraper not available - AI endpoints will be disabled")
    news_scraper = None

@app.get("/")
async def root():
    """API information and available endpoints"""
    return {
        "service": "VTHacks26 Financial Risk Analysis API",
        "version": "2.0.0",
        "status": "operational",
        "supported_symbols": financial_service.get_supported_symbols(),
        "endpoints": {
            "health": "/health",
            "single_analysis": "/risk-level/{symbol}",
            "batch_analysis": "/risk-level",
            "stats": "/stats",
            "database_test": "/test-aerospike",
            "documentation": "/docs"
        },
        "data_sources": [
            "Yahoo Finance (real-time)",
            "CBOE Volatility (calculated)",
            "Aerospike Database (caching)"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_connected = aerospike_repo.is_connected()
    
    return {
        "status": "healthy",
        "service": "VTHacks26 Financial Risk Analysis API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database_connected": db_connected,
        "supported_symbols": len(financial_service.get_supported_symbols())
    }

@app.get("/risk-level/{symbol}")
async def analyze_single_stock(symbol: str):
    """Analyze risk level for a single stock symbol"""
    # Validate symbol
    if not symbol or len(symbol) > 10 or not symbol.replace('.', '').replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid symbol format")
    
    symbol = symbol.upper()
    
    # Check cache first
    cached_result = aerospike_repo.get_stock_analysis(symbol)
    if cached_result and cached_result.get('retrieved_from_cache'):
        return {
            "success": True,
            "symbol": symbol,
            "data": cached_result,
            "source": "cache",
            "cached_at": cached_result.get('cache_timestamp'),
            "response_time": "< 0.001s"
        }
    
    # Perform fresh analysis
    start_time = datetime.now()
    result = financial_service.analyze_single_stock(symbol)
    end_time = datetime.now()
    
    response_time = (end_time - start_time).total_seconds()
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    # Store in cache
    aerospike_repo.store_stock_analysis(symbol, result)
    
    return {
        "success": True,
        "symbol": symbol,
        "financial_data": result['financial_data'],
        "risk_analysis": result['risk_analysis'],
        "source": "fresh_analysis",
        "response_time": f"{response_time:.3f}s",
        "timestamp": result['timestamp']
    }

@app.post("/risk-level")
async def analyze_batch_stocks(request_data: Dict[str, Any]):
    """Analyze risk levels for multiple stock symbols"""
    symbols = request_data.get('symbols', [])
    custom_factors = request_data.get('custom_factors')
    
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    if len(symbols) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 symbols per request")
    
    # Validate symbols
    for symbol in symbols:
        if not symbol or len(symbol) > 10 or not symbol.replace('.', '').replace('-', '').isalnum():
            raise HTTPException(status_code=400, detail=f"Invalid symbol format: {symbol}")
    
    # Perform batch analysis
    start_time = datetime.now()
    batch_result = financial_service.analyze_batch_stocks(symbols, custom_factors)
    end_time = datetime.now()
    
    # Store results in cache
    successful_results = {}
    for result in batch_result['results']:
        if result['success']:
            successful_results[result['symbol']] = result
    
    if successful_results:
        aerospike_repo.store_batch_analysis(successful_results)
    
    # Add response timing
    batch_result['api_response_time'] = f"{(end_time - start_time).total_seconds():.3f}s"
    
    return batch_result

@app.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get full stock data including financial metrics"""
    # Validate symbol
    if not symbol or len(symbol) > 10 or not symbol.replace('.', '').replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid symbol format")

    symbol = symbol.upper()

    try:
        # Get stock data from Yahoo Finance parser
        from parsers.yahoo_finance_parser import YahooFinanceParser
        parser = YahooFinanceParser()
        stock_data = parser.get_stock_data(symbol)

        if not stock_data or stock_data.get('current_price', 0) == 0:
            raise HTTPException(status_code=404, detail=f"Stock data not found for {symbol}")

        return {
            "success": True,
            "symbol": symbol,
            "data": stock_data,
            "source": "yahoo_finance",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    service_stats = financial_service.get_service_stats()
    repo_stats = aerospike_repo.get_repository_stats()
    
    return {
        "service": service_stats,
        "database": repo_stats,
        "api_info": {
            "version": "2.0.0",
            "uptime_check": datetime.now(timezone.utc).isoformat(),
            "endpoints_available": 6,
            "max_batch_size": 10
        }
    }

@app.get("/test-aerospike")
async def test_aerospike_connection():
    """Test Aerospike database connection"""
    connection_test = aerospike_repo.test_connection()
    
    if connection_test['success']:
        return {
            "success": True,
            "message": "Aerospike connection working perfectly",
            "details": connection_test
        }
    else:
        return {
            "success": False,
            "message": "Aerospike connection failed",
            "error": connection_test.get('error', 'Unknown error'),
            "details": connection_test
        }

@app.get("/cache/clear/{symbol}")
async def clear_symbol_cache(symbol: str):
    """Clear cache for a specific symbol"""
    symbol = symbol.upper()
    success = aerospike_repo.clear_cache(symbol)
    
    return {
        "success": success,
        "message": f"Cache cleared for {symbol}" if success else f"Failed to clear cache for {symbol}",
        "symbol": symbol
    }

@app.get("/cache/status")
async def get_cache_status():
    """Get cache status and statistics"""
    cached_symbols = aerospike_repo.get_cached_symbols()

    return {
        "cache_enabled": aerospike_repo.is_connected(),
        "cached_symbols": cached_symbols,
        "cache_count": len(cached_symbols),
        "database_status": "connected" if aerospike_repo.is_connected() else "disconnected"
    }

@app.get("/predictions")
async def get_stock_predictions():
    """Get stock price predictions from Aerospike"""
    try:
        predictions = aerospike_repo.get_predictions()

        if predictions:
            return {
                "success": True,
                "data": predictions,
                "count": len(predictions),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "error": "No predictions found in database",
                "data": {},
                "count": 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving predictions: {str(e)}")

@app.get("/predictions/{symbol}")
async def get_symbol_prediction(symbol: str):
    """Get prediction for a specific stock symbol"""
    symbol = symbol.upper()

    try:
        predictions = aerospike_repo.get_predictions()

        if predictions and symbol in predictions:
            return {
                "success": True,
                "symbol": symbol,
                "prediction": predictions[symbol],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "symbol": symbol,
                "error": f"No prediction found for {symbol}",
                "prediction": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prediction for {symbol}: {str(e)}")

@app.get("/advanced-metrics")
async def get_all_advanced_metrics():
    """Get advanced risk metrics for all stocks from Aerospike"""
    try:
        all_metrics = aerospike_repo.get_all_advanced_metrics()

        if all_metrics:
            return {
                "success": True,
                "data": all_metrics,
                "count": len(all_metrics),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "error": "No advanced metrics found in database",
                "data": {},
                "count": 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving advanced metrics: {str(e)}")

@app.get("/advanced-metrics/{symbol}")
async def get_symbol_advanced_metrics(symbol: str):
    """Get advanced risk metrics for a specific stock symbol"""
    symbol = symbol.upper()

    try:
        metrics = aerospike_repo.get_advanced_risk_metrics(symbol)

        if metrics:
            return {
                "success": True,
                "symbol": symbol,
                "metrics": metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "symbol": symbol,
                "error": f"No advanced metrics found for {symbol}",
                "metrics": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving advanced metrics for {symbol}: {str(e)}")

# Conditionally register AI endpoints only if news scraper is available
if news_scraper is not None:
    print("REGISTER: AI summary endpoints...")

    @app.get("/ai-summary/{symbol}")
    async def get_ai_investment_summary(symbol: str):
        """Get AI-powered investment summary with sentiment analysis"""
        print(f"REQUEST: AI Summary requested for symbol: {symbol}")

        # Validate symbol
        if not symbol or len(symbol) > 10 or not symbol.replace('.', '').replace('-', '').isalnum():
            print(f"ERROR: Invalid symbol format: {symbol}")
            raise HTTPException(status_code=400, detail="Invalid symbol format")

        symbol = symbol.upper()
        print(f"SUCCESS: Symbol validated: {symbol}")

        try:
            print(f"PROCESSING: Generating AI summary for {symbol}...")
            # Generate AI summary using news scraper
            start_time = datetime.now()
            summary_data = news_scraper.generate_ai_summary(symbol)
            end_time = datetime.now()

            response_time = (end_time - start_time).total_seconds()
            print(f"SUCCESS: AI summary generated successfully in {response_time:.3f}s")

            return {
                "success": True,
                "symbol": symbol,
                "data": summary_data,
                "response_time": f"{response_time:.3f}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            print(f"ERROR: Error generating AI summary for {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating AI summary: {str(e)}")

    print("SUCCESS: AI summary endpoint registered")
else:
    print("WARNING: AI summary endpoints NOT registered - news scraper unavailable")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services and pre-load data on startup"""
    import asyncio
    
    print("VTHacks26 Financial Risk Analysis API")
    print("=" * 60)
    print("Real-time Yahoo Finance integration")
    print("CBOE volatility calculation")
    print("Aerospike database caching")
    print("Comprehensive risk analysis")
    print()
    print(f"Supported symbols: {', '.join(financial_service.get_supported_symbols())}")
    print(f"Database: {'Connected' if aerospike_repo.is_connected() else 'Disconnected (graceful fallback)'}")
    print(f"News Scraper: {'Available' if news_scraper is not None else 'Unavailable'}")
    print()
    print("Available Endpoints:")
    print("  Core APIs:")
    print("    GET /health - Health check")
    print("    GET /stats - System statistics")
    print("    GET /risk-level/{symbol} - Risk analysis")
    print("    GET /stock/{symbol} - Stock data")

    if news_scraper is not None:
        print("  AI/News APIs:")
        print("    GET /ai-summary/{symbol} - AI investment summary")
    else:
        print("  AI/News APIs: DISABLED (news scraper unavailable)")

    print()
    print("Quick Links:")
    print("  Documentation: http://localhost:8000/docs")
    print("  Health Check: http://localhost:8000/health")
    print("  Example: curl http://localhost:8000/risk-level/AAPL")

    if news_scraper is not None:
        print("  AI Summary: curl http://localhost:8000/ai-summary/AAPL")

    # Pre-load stock analysis data for all supported symbols
    print("\n🚀 STARTUP: Pre-loading stock analysis data...")
    supported_symbols = financial_service.get_supported_symbols()
    
    async def preload_symbol(symbol: str):
        """Pre-load data for a single symbol"""
        try:
            print(f"   Loading {symbol}...")
            # This will fetch YTD data and cache it in Aerospike
            result = financial_service.analyze_single_stock(symbol)
            if result.get('success'):
                # Store in cache
                success = aerospike_repo.store_stock_analysis(symbol, result)
                if success:
                    print(f"   ✅ {symbol} cached successfully")
                else:
                    print(f"   ⚠️  {symbol} analyzed but cache failed")
            else:
                print(f"   ❌ {symbol} analysis failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ {symbol} error: {str(e)}")
    
    # Pre-load all symbols concurrently
    tasks = [preload_symbol(symbol) for symbol in supported_symbols]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"✅ STARTUP: Pre-loaded analysis for {len(supported_symbols)} symbols")
    print("   All YTD data is now available in cache!")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    aerospike_repo.close()
    print("VTHacks26 API shutdown complete")

if __name__ == "__main__":
    print("Starting VTHacks26 Financial Risk Analysis API...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )