#!/usr/bin/env python3
"""
Aerospike Repository
Handles all database operations for financial data storage
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone


class AerospikeRepository:
    """Repository for Aerospike database operations"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 3000):
        self.host = host
        self.port = port
        self.namespace = 'test'
        self.set_name = 'finance'
        self.client = None
        self.connected = False
        
        self._connect()
    
    def _connect(self) -> bool:
        """Establish connection to Aerospike"""
        try:
            import aerospike
            
            config = {
                'hosts': [(self.host, self.port)],
                'policies': {'timeout': 5000}
            }
            
            self.client = aerospike.client(config).connect()
            self.connected = True
            print(f"SUCCESS: Connected to Aerospike at {self.host}:{self.port}")
            return True
            
        except ImportError:
            print("ERROR: Aerospike client not installed. Install with: pip install aerospike")
            return False
        except Exception as e:
            print(f"ERROR: Failed to connect to Aerospike: {e}")
            self.connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Aerospike"""
        if not self.connected or not self.client:
            return False
        
        try:
            # Test connection with a simple operation
            test_key = (self.namespace, self.set_name, 'connection_test')
            self.client.put(test_key, {'test': 'connection'})
            self.client.remove(test_key)
            return True
        except Exception:
            self.connected = False
            return False
    
    def store_stock_analysis(self, symbol: str, analysis_data: Dict[str, Any]) -> bool:
        """Store stock analysis results"""
        if not self.is_connected():
            print(f"⚠️  Aerospike not connected, skipping storage for {symbol}")
            return False
        
        try:
            import aerospike
            key = (self.namespace, self.set_name, f'analysis_{symbol}')
            
            # Prepare data for storage
            storage_data = {
                'symbol': symbol,
                'analysis_data': json.dumps(analysis_data),
                'stored_at': datetime.now(timezone.utc).isoformat(),
                'ttl': 3600  # 1 hour TTL
            }
            
            # Store with TTL policy
            policy = {'gen': aerospike.POLICY_GEN_IGNORE}
            self.client.put(key, storage_data, policy=policy)
            
            print(f"SUCCESS: Stored analysis for {symbol}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to store analysis for {symbol}: {e}")
            return False
    
    def get_stock_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored stock analysis"""
        if not self.is_connected():
            return None
        
        try:
            key = (self.namespace, self.set_name, f'analysis_{symbol}')
            
            (returned_key, metadata, bins) = self.client.get(key)
            
            if bins:
                stored_data = json.loads(bins['analysis_data'])
                stored_data['retrieved_from_cache'] = True
                stored_data['cache_timestamp'] = bins['stored_at']
                return stored_data
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to retrieve analysis for {symbol}: {e}")
            return None
    
    def store_batch_analysis(self, batch_results: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Store batch analysis results"""
        storage_results = {}
        
        for symbol, analysis_data in batch_results.items():
            success = self.store_stock_analysis(symbol, analysis_data)
            storage_results[symbol] = success
        
        return storage_results
    
    def get_cached_symbols(self) -> List[str]:
        """Get list of symbols with cached data"""
        if not self.is_connected():
            return []
        
        try:
            # This is a simplified approach - in production you'd use a proper scan
            cached_symbols = []
            test_symbols = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']
            
            for symbol in test_symbols:
                if self.get_stock_analysis(symbol) is not None:
                    cached_symbols.append(symbol)
            
            return cached_symbols
            
        except Exception as e:
            print(f"❌ Failed to get cached symbols: {e}")
            return []
    
    def clear_cache(self, symbol: Optional[str] = None) -> bool:
        """Clear cached data for a symbol or all symbols"""
        if not self.is_connected():
            return False
        
        try:
            if symbol:
                # Clear specific symbol
                key = (self.namespace, self.set_name, f'analysis_{symbol}')
                self.client.remove(key)
                print(f"SUCCESS: Cleared cache for {symbol}")
                return True
            else:
                # Clear all cached analyses
                test_symbols = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']
                cleared_count = 0
                
                for sym in test_symbols:
                    try:
                        key = (self.namespace, self.set_name, f'analysis_{sym}')
                        self.client.remove(key)
                        cleared_count += 1
                    except:
                        pass  # Key might not exist
                
                print(f"SUCCESS: Cleared cache for {cleared_count} symbols")
                return True
                
        except Exception as e:
            print(f"❌ Failed to clear cache: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Aerospike connection and operations"""
        if not self.is_connected():
            return {
                'success': False,
                'error': 'Not connected to Aerospike',
                'host': f"{self.host}:{self.port}"
            }
        
        try:
            # Test write/read cycle
            test_key = (self.namespace, self.set_name, 'repository_test')
            test_data = {
                'message': 'Repository test successful',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'test_type': 'connection_verification'
            }
            
            # Write
            start_time = time.time()
            self.client.put(test_key, test_data)
            
            # Read
            (key, metadata, bins) = self.client.get(test_key)
            read_time = time.time()
            
            # Clean up
            self.client.remove(test_key)
            
            return {
                'success': True,
                'message': 'Aerospike repository working correctly',
                'host': f"{self.host}:{self.port}",
                'namespace': self.namespace,
                'set': self.set_name,
                'round_trip_time_ms': round((read_time - start_time) * 1000, 2),
                'data_verified': bins['message'] == test_data['message']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Repository test failed: {str(e)}',
                'host': f"{self.host}:{self.port}"
            }
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        stats = {
            'connected': self.is_connected(),
            'host': f"{self.host}:{self.port}",
            'namespace': self.namespace,
            'set_name': self.set_name,
            'cached_symbols': self.get_cached_symbols(),
            'cache_count': len(self.get_cached_symbols())
        }
        
        if self.is_connected():
            test_result = self.test_connection()
            stats['connection_test'] = test_result
        
        return stats
    
    def close(self):
        """Close Aerospike connection"""
        if self.client and self.connected:
            try:
                self.client.close()
                print("SUCCESS: Aerospike connection closed")
            except Exception as e:
                print(f"⚠️  Error closing Aerospike connection: {e}")
        
        self.connected = False
        self.client = None


def test_aerospike_repository():
    """Test the Aerospike repository"""
    repo = AerospikeRepository()
    
    print("🧪 Testing Aerospike Repository")
    print("=" * 50)
    
    # Test connection
    connection_test = repo.test_connection()
    print(f"Connection Test: {'SUCCESS' if connection_test['success'] else 'FAILED'}")
    if connection_test['success']:
        print(f"Round-trip time: {connection_test['round_trip_time_ms']}ms")
    else:
        print(f"Error: {connection_test['error']}")
    
    # Test storage and retrieval
    if repo.is_connected():
        print("\nTesting storage operations...")
        test_data = {
            'symbol': 'TEST',
            'price': 150.00,
            'risk_level': 'medium',
            'test': True
        }
        
        # Store
        stored = repo.store_stock_analysis('TEST', test_data)
        print(f"Storage: {'SUCCESS' if stored else 'FAILED'}")
        
        # Retrieve
        retrieved = repo.get_stock_analysis('TEST')
        if retrieved:
            print("SUCCESS: Retrieval: SUCCESS")
            print(f"Retrieved data includes cache info: {retrieved.get('retrieved_from_cache', False)}")
        else:
            print("❌ Retrieval: FAILED")
        
        # Clean up
        repo.clear_cache('TEST')
    
    # Get stats
    stats = repo.get_repository_stats()
    print(f"\nRepository Stats:")
    print(f"Connected: {stats['connected']}")
    print(f"Cached symbols: {len(stats['cached_symbols'])}")
    
    repo.close()


if __name__ == "__main__":
    test_aerospike_repository()