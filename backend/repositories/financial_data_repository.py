"""
In-memory repository for development/testing
Falls back to this when Aerospike is not available
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models import AnalysisResult
from .base_repository import BaseRepository


class FinancialDataRepository(BaseRepository[AnalysisResult]):
    """
    In-memory repository for financial analysis results
    Used for development and as fallback when Aerospike is not available
    """
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._data: Dict[str, AnalysisResult] = {}
        self._symbol_index: Dict[str, List[str]] = {}
    
    def _generate_key(self, symbol: str, timestamp: datetime = None) -> str:
        """Generate a unique key for the record"""
        if timestamp is None:
            timestamp = datetime.now()
        
        return f"{symbol}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _update_symbol_index(self, symbol: str, key: str):
        """Update symbol index for faster lookups"""
        if symbol not in self._symbol_index:
            self._symbol_index[symbol] = []
        
        if key not in self._symbol_index[symbol]:
            self._symbol_index[symbol].append(key)
            # Keep sorted by timestamp (newest first)
            self._symbol_index[symbol].sort(
                key=lambda k: self._data[k].analysis_timestamp,
                reverse=True
            )
    
    async def save(self, entity: AnalysisResult, key: str = None) -> str:
        """Save analysis result to memory"""
        if key is None:
            key = self._generate_key(entity.symbol, entity.analysis_timestamp)
        
        entity.analysis_id = key
        self._data[key] = entity
        self._update_symbol_index(entity.symbol, key)
        
        print(f"Saved analysis result: {key} for {entity.symbol}")
        return key
    
    async def get_by_key(self, key: str) -> Optional[AnalysisResult]:
        """Get analysis result by key"""
        return self._data.get(key)
    
    async def get_by_symbol(self, symbol: str) -> Optional[AnalysisResult]:
        """Get latest analysis result for symbol"""
        results = await self.get_latest_by_symbol(symbol, 1)
        return results[0] if results else None
    
    async def get_latest_by_symbol(self, symbol: str, limit: int = 10) -> List[AnalysisResult]:
        """Get latest analysis results for symbol"""
        if symbol not in self._symbol_index:
            return []
        
        keys = self._symbol_index[symbol][:limit]
        return [self._data[key] for key in keys if key in self._data]
    
    async def search(self, filters: Dict[str, Any]) -> List[AnalysisResult]:
        """Search analysis results by filters"""
        results = []
        
        for result in self._data.values():
            match = True
            
            # Filter by symbol
            if 'symbol' in filters and result.symbol != filters['symbol']:
                match = False
            
            # Filter by risk level
            if 'risk_level' in filters and result.financial_data.risk_metrics:
                if result.financial_data.risk_metrics.risk_level.value != filters['risk_level']:
                    match = False
            
            # Filter by date range
            if 'start_date' in filters:
                start_date = datetime.fromisoformat(filters['start_date'])
                if result.analysis_timestamp < start_date:
                    match = False
            
            if 'end_date' in filters:
                end_date = datetime.fromisoformat(filters['end_date'])
                if result.analysis_timestamp > end_date:
                    match = False
            
            # Filter by sentiment score range
            if 'min_sentiment' in filters and result.overall_sentiment_score is not None:
                if result.overall_sentiment_score < filters['min_sentiment']:
                    match = False
            
            if 'max_sentiment' in filters and result.overall_sentiment_score is not None:
                if result.overall_sentiment_score > filters['max_sentiment']:
                    match = False
            
            if match:
                results.append(result)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda r: r.analysis_timestamp, reverse=True)
        return results
    
    async def delete(self, key: str) -> bool:
        """Delete analysis result by key"""
        if key in self._data:
            result = self._data[key]
            symbol = result.symbol
            
            # Remove from data
            del self._data[key]
            
            # Remove from symbol index
            if symbol in self._symbol_index and key in self._symbol_index[symbol]:
                self._symbol_index[symbol].remove(key)
                if not self._symbol_index[symbol]:
                    del self._symbol_index[symbol]
            
            print(f"Deleted analysis result: {key}")
            return True
        
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if analysis result exists"""
        return key in self._data
    
    async def get_all_symbols(self) -> List[str]:
        """Get all unique symbols"""
        return list(self._symbol_index.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        return {
            'total_records': len(self._data),
            'unique_symbols': len(self._symbol_index),
            'symbols': list(self._symbol_index.keys()),
            'memory_size_mb': len(json.dumps([r.to_dict() for r in self._data.values()])) / (1024 * 1024)
        }