"""
Financial analysis API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ..main import get_analysis_service, get_data_service
from ...services import FinancialAnalysisService, DataIntegrationService
from ...models import AnalysisResult


router = APIRouter()


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    symbol: str
    include_sentiment: bool = True
    sentiment_sources: Optional[List[str]] = None


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    symbols: List[str]
    include_sentiment: bool = True


class SearchFilters(BaseModel):
    """Filters for searching analyses"""
    symbol: Optional[str] = None
    risk_level: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_sentiment: Optional[float] = None
    max_sentiment: Optional[float] = None


@router.post("/analyze")
async def analyze_stock(
    request: AnalysisRequest,
    analysis_service: FinancialAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Analyze a single stock"""
    
    try:
        result = await analysis_service.analyze_stock(
            symbol=request.symbol.upper(),
            include_sentiment=request.include_sentiment,
            sentiment_sources=request.sentiment_sources
        )
        
        return {
            "success": True,
            "data": result.to_dict(),
            "message": f"Analysis completed for {request.symbol.upper()}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/batch")
async def analyze_batch(
    request: BatchAnalysisRequest,
    analysis_service: FinancialAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Analyze multiple stocks"""
    
    if len(request.symbols) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed per batch")
    
    try:
        symbols = [s.upper() for s in request.symbols]
        results = await analysis_service.analyze_portfolio(symbols)
        
        success_count = sum(1 for r in results.values() if r is not None)
        
        return {
            "success": True,
            "data": {
                symbol: result.to_dict() if result else None 
                for symbol, result in results.items()
            },
            "summary": {
                "total_requested": len(symbols),
                "successful": success_count,
                "failed": len(symbols) - success_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/result/{symbol}")
async def get_analysis_result(
    symbol: str,
    analysis_service: FinancialAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Get latest analysis result for a symbol"""
    
    try:
        result = await analysis_service.get_analysis(symbol.upper())
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"No analysis found for {symbol.upper()}")
        
        return {
            "success": True,
            "data": result.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")


@router.get("/history/{symbol}")
async def get_analysis_history(
    symbol: str,
    limit: int = Query(default=10, ge=1, le=100),
    analysis_service: FinancialAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Get analysis history for a symbol"""
    
    try:
        results = await analysis_service.get_analysis_history(symbol.upper(), limit)
        
        return {
            "success": True,
            "data": [result.to_dict() for result in results],
            "count": len(results),
            "symbol": symbol.upper()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.post("/search")
async def search_analyses(
    filters: SearchFilters,
    limit: int = Query(default=50, ge=1, le=200),
    analysis_service: FinancialAnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Search analyses with filters"""
    
    try:
        # Convert filters to dict, removing None values
        filter_dict = {
            k: v for k, v in filters.dict().items() 
            if v is not None
        }
        
        results = await analysis_service.search_analyses(filter_dict)
        
        # Apply limit
        results = results[:limit]
        
        return {
            "success": True,
            "data": [result.to_dict() for result in results],
            "count": len(results),
            "filters": filter_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/symbols")
async def get_analyzed_symbols(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Get all symbols that have been analyzed"""
    
    try:
        symbols = await data_service.get_all_symbols()
        
        return {
            "success": True,
            "data": {
                "symbols": sorted(symbols),
                "count": len(symbols)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve symbols: {str(e)}")


@router.get("/summary")
async def get_analysis_summary(
    data_service: DataIntegrationService = Depends(get_data_service)
) -> Dict[str, Any]:
    """Get analysis summary statistics"""
    
    try:
        # Get repository stats
        repo_stats = await data_service.get_repository_stats()
        
        # Get all symbols for additional stats
        symbols = await data_service.get_all_symbols()
        
        return {
            "success": True,
            "data": {
                "total_symbols": len(symbols),
                "repository_info": repo_stats,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")