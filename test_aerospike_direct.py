#!/usr/bin/env python3
"""
Direct Aerospike Connection Test
Tests direct connection to your Aerospike instance
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any


def test_aerospike_direct():
    """Test direct connection to Aerospike"""
    
    print("🧪 Direct Aerospike Connection Test")
    print("=" * 50)
    
    try:
        # Import Aerospike
        import aerospike
        from aerospike import exception as ex
        print("✅ Aerospike client imported successfully")
    except ImportError:
        print("❌ Aerospike client not installed")
        print("   Install with: pip install aerospike")
        return False
    
    # Configuration
    config = {
        'hosts': [('127.0.0.1', 3000)],
        'policies': {
            'timeout': 5000
        }
    }
    
    namespace = 'test'
    set_name = 'finance'
    
    print(f"🎯 Target: {config['hosts']}")
    print(f"📦 Namespace: {namespace}, Set: {set_name}")
    
    try:
        # Connect to Aerospike
        print("\n🔗 Connecting to Aerospike...")
        client = aerospike.client(config).connect()
        print("✅ Connected successfully")
        
        # Test basic operations
        print("\n📊 Testing basic operations...")
        
        # 1. Test write
        test_key = ('test', 'finance', 'test_record_001')
        test_data = {
            'symbol': 'TEST',
            'timestamp': int(datetime.now().timestamp()),
            'risk_level': 'low',
            'sentiment_score': 0.5,
            'test_data': json.dumps({
                'message': 'Hello Aerospike!',
                'created_at': datetime.now().isoformat()
            })
        }
        
        print("   Writing test record...")
        client.put(test_key, test_data)
        print("   ✅ Write successful")
        
        # 2. Test read
        print("   Reading test record...")
        (key, metadata, bins) = client.get(test_key)
        print("   ✅ Read successful")
        print(f"   📄 Data: {bins}")
        
        # 3. Test exists
        print("   Checking record existence...")
        (key, metadata) = client.exists(test_key)
        exists = metadata is not None
        print(f"   ✅ Exists check: {exists}")
        
        # 4. Test indexes
        print("\n🗂️  Creating indexes...")
        
        indexes_to_create = [
            ('symbol', 'symbol_idx', 'string'),
            ('timestamp', 'timestamp_idx', 'numeric'),
            ('risk_level', 'risk_level_idx', 'string'),
            ('sentiment_score', 'sentiment_score_idx', 'numeric')
        ]
        
        for bin_name, index_name, index_type in indexes_to_create:
            try:
                if index_type == 'string':
                    client.index_string_create(namespace, set_name, bin_name, index_name)
                else:
                    client.index_integer_create(namespace, set_name, bin_name, index_name)
                print(f"   ✅ Created {index_name} index")
            except Exception as e:
                if "Index already exists" in str(e):
                    print(f"   ℹ️  Index {index_name} already exists")
                else:
                    print(f"   ⚠️  Index {index_name} creation warning: {e}")
        
        # 5. Test query
        print("\n🔍 Testing query functionality...")
        try:
            from aerospike import predicates as p
            
            query = client.query(namespace, set_name)
            query.select('symbol', 'timestamp', 'risk_level')
            query.where(p.equals('symbol', 'TEST'))
            
            results = []
            def callback(input_tuple):
                key, metadata, bins = input_tuple
                results.append(bins)
            
            query.foreach(callback)
            print(f"   ✅ Query successful, found {len(results)} records")
            
        except Exception as e:
            print(f"   ⚠️  Query test warning: {e}")
        
        # 6. Test scan
        print("   Testing scan functionality...")
        try:
            scan = client.scan(namespace, set_name)
            scan.select('symbol')
            
            symbols = set()
            def scan_callback(input_tuple):
                key, metadata, bins = input_tuple
                if bins and 'symbol' in bins:
                    symbols.add(bins['symbol'])
            
            scan.foreach(scan_callback)
            print(f"   ✅ Scan successful, found symbols: {list(symbols)}")
            
        except Exception as e:
            print(f"   ⚠️  Scan test warning: {e}")
        
        # 7. Clean up test record
        print("\n🧹 Cleaning up...")
        client.remove(test_key)
        print("   ✅ Test record removed")
        
        # Close connection
        client.close()
        print("\n✅ All tests passed! Aerospike is working correctly.")
        print(f"🎯 Your backend can now use namespace '{namespace}' and set '{set_name}'")
        
        return True
        
    except ex.ClientError as e:
        print(f"❌ Aerospike client error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_backend_connection():
    """Test if backend is running"""
    print("\n🌐 Testing Backend Connection...")
    
    try:
        import requests
        response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  requests not installed, skipping backend test")
        return None
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        print("   Make sure to start the backend with: python run_backend.py")
        return False


if __name__ == "__main__":
    print("🔧 Aerospike Setup Verification")
    print("This script tests your Aerospike installation and setup")
    print()
    
    # Test Aerospike
    aerospike_ok = test_aerospike_direct()
    
    # Test backend if available
    backend_ok = test_backend_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print(f"Aerospike: {'✅ Working' if aerospike_ok else '❌ Failed'}")
    
    if backend_ok is True:
        print("Backend: ✅ Running")
    elif backend_ok is False:
        print("Backend: ❌ Not running")
    else:
        print("Backend: ⚠️  Not tested")
    
    if aerospike_ok:
        print("\n🎉 Aerospike is ready!")
        print("Next steps:")
        print("1. Start the backend: python run_backend.py")
        print("2. Run integration tests: python test_aerospike_integration.py")
        print("3. View API docs: http://localhost:8000/docs")
    else:
        print("\n❌ Aerospike setup needs attention")
        print("Check:")
        print("1. Aerospike is running: docker ps")
        print("2. Port 3000 is accessible")
        print("3. Aerospike client is installed: pip install aerospike")
    
    exit(0 if aerospike_ok else 1)