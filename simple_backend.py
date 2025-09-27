#!/usr/bin/env python3
"""
Simple Aerospike Backend Test Server
Minimal version to test Aerospike integration
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip3 install --break-system-packages fastapi uvicorn")
    exit(1)


# Simple Aerospike test
async def test_aerospike_connection():
    """Test Aerospike connection"""
    try:
        import aerospike
        
        config = {
            'hosts': [('127.0.0.1', 3000)],
            'policies': {'timeout': 5000}
        }
        
        client = aerospike.client(config).connect()
        
        # Test write/read
        test_key = ('test', 'finance', 'backend_test')
        test_data = {'message': 'Backend connected!', 'status': 'working'}
        
        client.put(test_key, test_data)
        (key, metadata, bins) = client.get(test_key)
        client.remove(test_key)
        client.close()
        
        return True, bins
        
    except Exception as e:
        return False, str(e)


# Create FastAPI app
app = FastAPI(
    title="Aerospike Test Backend",
    description="Simple test server for Aerospike integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Aerospike Test Backend",
        "status": "running",
        "endpoints": ["/health", "/test-aerospike", "/test-analysis"]
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "Aerospike Test Backend"
    }


@app.get("/test-aerospike")
async def test_aerospike():
    """Test Aerospike connection"""
    success, result = await test_aerospike_connection()
    
    return {
        "success": success,
        "aerospike_working": success,
        "data": result if success else None,
        "error": result if not success else None
    }


@app.post("/test-analysis")
async def test_analysis(data: Dict[str, Any]):
    """Test analysis functionality"""
    try:
        symbol = data.get('symbol', 'TEST')
        
        # Simple mock analysis
        mock_result = {
            'symbol': symbol,
            'risk_level': 'medium',
            'recommendation': 'HOLD',
            'sentiment_score': 0.5,
            'timestamp': '2025-09-27T03:45:00Z'
        }
        
        # Try to save to Aerospike
        aerospike_success = False
        try:
            import aerospike
            
            config = {'hosts': [('127.0.0.1', 3000)], 'policies': {'timeout': 5000}}
            client = aerospike.client(config).connect()
            
            key = ('test', 'finance', f'analysis_{symbol}')
            client.put(key, mock_result)
            client.close()
            
            aerospike_success = True
            
        except Exception as e:
            print(f"Aerospike save failed: {e}")
        
        return {
            "success": True,
            "analysis": mock_result,
            "saved_to_aerospike": aerospike_success
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/risk-level/{symbol}")
async def get_risk_level(symbol: str):
    """Get risk level for a specific symbol"""
    # Validate symbol format
    if not symbol or len(symbol) > 10 or not symbol.replace('.', '').replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid symbol format")
    
    try:
        import aerospike
        
        config = {'hosts': [('127.0.0.1', 3000)], 'policies': {'timeout': 5000}}
        client = aerospike.client(config).connect()
        
        # Try to get existing analysis first
        key = ('test', 'finance', f'analysis_{symbol.upper()}')
        
        try:
            (key_returned, metadata, record) = client.get(key)
            risk_level = record.get('risk_level', 'unknown')
            client.close()
            
            return {
                "success": True,
                "symbol": symbol.upper(),
                "risk_level": risk_level,
                "source": "stored_analysis",
                "data": record
            }
            
        except aerospike.exception.RecordNotFound:
            # If no stored analysis, calculate new risk level
            import random
            import time
            
            # Mock risk calculation based on symbol characteristics
            risk_factors = {
                'volatility': random.uniform(0.1, 0.9),
                'market_cap': random.choice(['large', 'mid', 'small']),
                'sector_risk': random.uniform(0.2, 0.8),
                'liquidity': random.uniform(0.3, 1.0)
            }
            
            # Simple risk scoring
            risk_score = (
                risk_factors['volatility'] * 0.4 +
                risk_factors['sector_risk'] * 0.3 +
                (0.8 if risk_factors['market_cap'] == 'small' else 0.3) * 0.2 +
                (1.0 - risk_factors['liquidity']) * 0.1
            )
            
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.6:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            # Store the new analysis
            new_analysis = {
                'symbol': symbol.upper(),
                'risk_level': risk_level,
                'risk_score': round(risk_score, 3),
                'risk_factors': risk_factors,
                'calculated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'method': 'auto_calculation'
            }
            
            try:
                client.put(key, new_analysis)
                stored = True
            except Exception as e:
                print(f"Failed to store new analysis: {e}")
                stored = False
            
            client.close()
            
            return {
                "success": True,
                "symbol": symbol.upper(),
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "source": "new_calculation",
                "stored_to_aerospike": stored
            }
            
    except ImportError:
        return {
            "success": False,
            "error": "Aerospike not available",
            "symbol": symbol.upper(),
            "risk_level": "unknown"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "symbol": symbol.upper()
        }


@app.post("/risk-level")
async def calculate_risk_level(data: Dict[str, Any]):
    """Calculate risk level for multiple symbols or with custom parameters"""
    try:
        symbols = data.get('symbols', [])
        custom_factors = data.get('risk_factors', {})
        
        if not symbols:
            symbols = [data.get('symbol', 'TEST')]
        
        results = []
        
        for symbol in symbols:
            # Get risk level for each symbol
            try:
                import aerospike
                import random
                import time
                
                config = {'hosts': [('127.0.0.1', 3000)], 'policies': {'timeout': 5000}}
                client = aerospike.client(config).connect()
                
                # Use custom factors if provided, otherwise generate random
                risk_factors = custom_factors if custom_factors else {
                    'volatility': random.uniform(0.1, 0.9),
                    'market_cap': random.choice(['large', 'mid', 'small']),
                    'sector_risk': random.uniform(0.2, 0.8),
                    'liquidity': random.uniform(0.3, 1.0)
                }
                
                # Calculate risk score
                risk_score = (
                    risk_factors.get('volatility', 0.5) * 0.4 +
                    risk_factors.get('sector_risk', 0.5) * 0.3 +
                    (0.8 if risk_factors.get('market_cap') == 'small' else 0.3) * 0.2 +
                    (1.0 - risk_factors.get('liquidity', 0.7)) * 0.1
                )
                
                if risk_score < 0.3:
                    risk_level = "low"
                elif risk_score < 0.6:
                    risk_level = "medium"
                else:
                    risk_level = "high"
                
                # Store in Aerospike
                key = ('test', 'finance', f'risk_analysis_{symbol.upper()}')
                analysis_data = {
                    'symbol': symbol.upper(),
                    'risk_level': risk_level,
                    'risk_score': round(risk_score, 3),
                    'risk_factors': risk_factors,
                    'calculated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'method': 'api_calculation'
                }
                
                client.put(key, analysis_data)
                client.close()
                
                results.append({
                    "symbol": symbol.upper(),
                    "risk_level": risk_level,
                    "risk_score": round(risk_score, 3),
                    "risk_factors": risk_factors
                })
                
            except Exception as e:
                results.append({
                    "symbol": symbol.upper(),
                    "error": str(e),
                    "risk_level": "error"
                })
        
        return {
            "success": True,
            "results": results,
            "total_analyzed": len(results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/stats")
async def get_stats():
    """Get system statistics and features"""
    return {
        "service": "VTHacks26 Risk Analysis API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Real-time risk analysis",
            "Batch processing",
            "Aerospike database integration",
            "Custom risk factors",
            "Stock sentiment analysis"
        ],
        "endpoints": {
            "health": "/health",
            "test_aerospike": "/test-aerospike", 
            "single_analysis": "/risk-level/{symbol}",
            "batch_analysis": "/risk-level",
            "statistics": "/stats"
        },
        "database": {
            "type": "Aerospike",
            "host": "127.0.0.1:3000",
            "namespace": "test",
            "set": "finance"
        }
    }


if __name__ == "__main__":
    print("🚀 Starting Aerospike Test Backend...")
    print("📊 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🧪 Test Aerospike: http://localhost:8000/test-aerospike")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )