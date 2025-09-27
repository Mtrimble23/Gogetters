"""
Aerospike repository implementation
Ready for integration when Aerospike VM is available
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..models import AnalysisResult
from .base_repository import BaseRepository


class AerospikeRepository(BaseRepository[AnalysisResult]):
    """
    Aerospike repository for financial analysis results
    
    This implementation is ready to connect to Aerospike when the VM is available.
    For now, it provides the interface and structure needed.
    """
    
    def __init__(self, 
                 hosts: List[Dict[str, Any]] = None,
                 namespace: str = "financial_data",
                 set_name: str = "analysis_results"):
        """
        Initialize Aerospike repository
        
        Args:
            hosts: List of Aerospike host configurations
            namespace: Aerospike namespace
            set_name: Aerospike set name
        """
        self.hosts = hosts or [{"addr": "127.0.0.1", "port": 3000}]
        self.namespace = namespace
        self.set_name = set_name
        self.client = None
        self._connected = False
    
    async def connect(self):
        """Connect to Aerospike cluster"""
        try:
            # Import aerospike 
            import aerospike
            from aerospike import exception as ex
            
            config = {
                'hosts': self.hosts,
                'policies': {
                    'timeout': self.timeout if hasattr(self, 'timeout') else 5000
                }
            }
            
            self.client = aerospike.client(config).connect()
            self._connected = True
            
            print(f"✅ Connected to Aerospike at {self.hosts}")
            print(f"📦 Namespace: {self.namespace}, Set: {self.set_name}")
            
            # Create indexes for efficient queries
            await self._create_indexes()
            
        except ImportError:
            print("❌ Aerospike client not installed. Install with: pip install aerospike")
            raise
        except Exception as e:
            print(f"❌ Failed to connect to Aerospike: {e}")
            self._connected = False
            raise
    
    
    async def _create_indexes(self):
        """Create secondary indexes for efficient queries"""
        if not self.client:
            return
        
        try:
            import aerospike
            
            # Index for symbol queries
            try:
                self.client.index_string_create(
                    self.namespace, 
                    self.set_name, 
                    "symbol", 
                    "symbol_idx"
                )
                print("   ✅ Created symbol index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    print(f"   ⚠️  Symbol index warning: {e}")
            
            # Index for timestamp queries  
            try:
                self.client.index_integer_create(
                    self.namespace, 
                    self.set_name, 
                    "timestamp", 
                    "timestamp_idx"
                )
                print("   ✅ Created timestamp index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    print(f"   ⚠️  Timestamp index warning: {e}")
            
            # Index for risk level queries
            try:
                self.client.index_string_create(
                    self.namespace, 
                    self.set_name, 
                    "risk_level", 
                    "risk_level_idx"
                )
                print("   ✅ Created risk_level index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    print(f"   ⚠️  Risk level index warning: {e}")
                    
            # Index for sentiment score range queries
            try:
                self.client.index_numeric_create(
                    self.namespace,
                    self.set_name,
                    "sentiment_score",
                    "sentiment_score_idx"
                )
                print("   ✅ Created sentiment_score index")
            except Exception as e:
                if "Index already exists" not in str(e):
                    print(f"   ⚠️  Sentiment score index warning: {e}")
                    
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
    
    async def disconnect(self):
        """Disconnect from Aerospike"""
        if self.client:
            self.client.close()
            self._connected = False
    
    def _generate_key(self, symbol: str, timestamp: datetime = None) -> str:
        """Generate a unique key for the record"""
        if timestamp is None:
            timestamp = datetime.now()
        
        key_string = f"{symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def save(self, entity: AnalysisResult, key: str = None) -> str:
        """Save analysis result to Aerospike"""
        if not self._connected:
            await self.connect()
        
        if key is None:
            key = self._generate_key(entity.symbol, entity.analysis_timestamp)
        
        # Prepare data for Aerospike with double indexing
        bins = {
            # Primary data
            "symbol": entity.symbol,
            "analysis_data": json.dumps(entity.to_dict()),
            "timestamp": int(entity.analysis_timestamp.timestamp()),
            
            # Indexed fields for efficient queries
            "risk_level": entity.financial_data.risk_metrics.risk_level.value if entity.financial_data.risk_metrics and entity.financial_data.risk_metrics.risk_level else None,
            "sentiment_score": entity.overall_sentiment_score,
            "recommendation": entity.recommendation,
            "confidence_level": entity.confidence_level,
            
            # Financial metrics for filtering
            "debt_to_equity": entity.financial_data.risk_metrics.debt_to_equity if entity.financial_data.risk_metrics else None,
            "beta": entity.financial_data.risk_metrics.beta if entity.financial_data.risk_metrics else None,
            "roe": entity.financial_data.risk_metrics.roe if entity.financial_data.risk_metrics else None,
            "current_ratio": entity.financial_data.risk_metrics.current_ratio if entity.financial_data.risk_metrics else None,
            "overall_risk_score": entity.financial_data.risk_metrics.overall_risk_score if entity.financial_data.risk_metrics else None,
            
            # Additional metadata
            "company_name": entity.financial_data.company_name,
            "market_cap": entity.financial_data.market_cap,
            "price": entity.financial_data.price,
            "created_at": int(datetime.now().timestamp())
        }
        
        try:
            # Save to Aerospike
            self.client.put((self.namespace, self.set_name, key), bins)
            print(f"💾 Saved to Aerospike: key={key}, symbol={entity.symbol}")
            return key
        except Exception as e:
            print(f"❌ Error saving to Aerospike: {e}")
            raise
    
    async def get_by_key(self, key: str) -> Optional[AnalysisResult]:
        """Get analysis result by key"""
        if not self._connected:
            await self.connect()
        
        try:
            (key_tuple, metadata, bins) = self.client.get((self.namespace, self.set_name, key))
            if bins and "analysis_data" in bins:
                data = json.loads(bins["analysis_data"])
                return AnalysisResult.from_dict(data)
            return None
        except Exception as e:
            if "AEROSPIKE_ERR_RECORD_NOT_FOUND" in str(e):
                return None
            print(f"❌ Error getting from Aerospike: {e}")
            return None
    
    async def get_by_symbol(self, symbol: str) -> Optional[AnalysisResult]:
        """Get latest analysis result for symbol"""
        results = await self.get_latest_by_symbol(symbol, 1)
        return results[0] if results else None
    
    async def get_latest_by_symbol(self, symbol: str, limit: int = 10) -> List[AnalysisResult]:
        """Get latest analysis results for symbol"""
        if not self._connected:
            await self.connect()
        
        try:
            import aerospike
            from aerospike import predicates as p
            
            # Query using secondary index on symbol
            query = self.client.query(self.namespace, self.set_name)
            query.select("analysis_data", "timestamp")
            query.where(p.equals("symbol", symbol))
            
            results = []
            def callback(input_tuple):
                key, metadata, bins = input_tuple
                if bins and "analysis_data" in bins:
                    try:
                        data = json.loads(bins["analysis_data"])
                        result = AnalysisResult.from_dict(data)
                        results.append((bins.get("timestamp", 0), result))
                    except Exception as e:
                        print(f"⚠️  Error parsing result: {e}")
            
            query.foreach(callback)
            
            # Sort by timestamp (newest first) and apply limit
            results.sort(key=lambda x: x[0], reverse=True)
            return [result[1] for result in results[:limit]]
            
        except Exception as e:
            print(f"❌ Error querying Aerospike for symbol {symbol}: {e}")
            return []
    
    async def search(self, filters: Dict[str, Any]) -> List[AnalysisResult]:
        """Search analysis results by filters"""
        if not self._connected:
            await self.connect()
        
        try:
            import aerospike
            from aerospike import predicates as p
            
            # Build query based on filters
            query = self.client.query(self.namespace, self.set_name)
            query.select("analysis_data", "timestamp")
            
            # Apply filters using secondary indexes where possible
            if 'symbol' in filters:
                query.where(p.equals("symbol", filters['symbol']))
            elif 'risk_level' in filters:
                query.where(p.equals("risk_level", filters['risk_level']))
            
            results = []
            def callback(input_tuple):
                key, metadata, bins = input_tuple
                if bins and "analysis_data" in bins:
                    try:
                        data = json.loads(bins["analysis_data"])
                        result = AnalysisResult.from_dict(data)
                        
                        # Apply additional filters that can't use indexes
                        if self._matches_filters(result, bins, filters):
                            results.append((bins.get("timestamp", 0), result))
                    except Exception as e:
                        print(f"⚠️  Error parsing result: {e}")
            
            query.foreach(callback)
            
            # Sort by timestamp (newest first)
            results.sort(key=lambda x: x[0], reverse=True)
            return [result[1] for result in results]
            
        except Exception as e:
            print(f"❌ Error searching Aerospike: {e}")
            return []
    
    def _matches_filters(self, result: AnalysisResult, bins: Dict, filters: Dict[str, Any]) -> bool:
        """Check if result matches additional filters"""
        # Date range filters
        if 'start_date' in filters:
            start_date = datetime.fromisoformat(filters['start_date'])
            if result.analysis_timestamp < start_date:
                return False
        
        if 'end_date' in filters:
            end_date = datetime.fromisoformat(filters['end_date'])
            if result.analysis_timestamp > end_date:
                return False
        
        # Sentiment score range filters
        if 'min_sentiment' in filters and result.overall_sentiment_score is not None:
            if result.overall_sentiment_score < filters['min_sentiment']:
                return False
        
        if 'max_sentiment' in filters and result.overall_sentiment_score is not None:
            if result.overall_sentiment_score > filters['max_sentiment']:
                return False
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete analysis result by key"""
        if not self._connected:
            await self.connect()
        
        try:
            self.client.remove((self.namespace, self.set_name, key))
            print(f"🗑️  Deleted from Aerospike: key={key}")
            return True
        except Exception as e:
            if "AEROSPIKE_ERR_RECORD_NOT_FOUND" in str(e):
                return False
            print(f"❌ Error deleting from Aerospike: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if analysis result exists"""
        if not self._connected:
            await self.connect()
        
        try:
            (key_tuple, metadata) = self.client.exists((self.namespace, self.set_name, key))
            return metadata is not None
        except Exception as e:
            print(f"❌ Error checking existence in Aerospike: {e}")
            return False
    
    async def get_all_symbols(self) -> List[str]:
        """Get all unique symbols"""
        if not self._connected:
            await self.connect()
        
        try:
            # Scan all records and collect unique symbols
            scan = self.client.scan(self.namespace, self.set_name)
            scan.select("symbol")
            
            symbols = set()
            def callback(input_tuple):
                key, metadata, bins = input_tuple
                if bins and "symbol" in bins:
                    symbols.add(bins["symbol"])
            
            scan.foreach(callback)
            return sorted(list(symbols))
            
        except Exception as e:
            print(f"❌ Error getting symbols from Aerospike: {e}")
            return []