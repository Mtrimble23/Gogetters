"""
Health check routes
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ..main import get_data_service, get_analysis_service
from ...services import DataIntegrationService, FinancialAnalysisService


router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Financial Risk Analyzer API"
    }


@router.get("/detailed")
async def detailed_health_check(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Detailed health check with service status"""
    
    # Get repository stats
    repo_stats = await data_service.get_repository_stats()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Financial Risk Analyzer API",
        "version": "1.0.0",
        "repositories": repo_stats,
        "services": {
            "data_integration": "active",
            "financial_analysis": "active"
        },
        "python_version": sys.version,
        "dependencies": {
            "fastapi": "available",
            "pandas": "available", 
            "yfinance": "available",
            "transformers": "available",
            "aerospike": "ready_to_install"
        }
    }


@router.get("/readiness")
async def readiness_check(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Readiness check for load balancers"""
    
    try:
        # Test basic functionality
        symbols = await data_service.get_all_symbols()
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "active_repository": "fallback" if data_service.use_fallback else "primary",
            "symbols_available": len(symbols)
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/liveness")
async def liveness_check() -> Dict[str, str]:
    """Liveness check for container orchestrators"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }