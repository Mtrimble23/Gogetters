#!/usr/bin/env python3
"""
Test Aerospike Database Storage
Verifies where and how data is stored in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.aerospike_repository import AerospikeRepository
from src.services.financial_risk_service import FinancialRiskService
import aerospike
import json
from datetime import datetime

def test_database_storage():
    """Test detailed database storage and retrieval"""
    print("🗄️  Testing Aerospike Database Storage")
    print("=" * 60)
    
    try:
        # Initialize components
        repository = AerospikeRepository()
        service = FinancialRiskService()
        
        # Test symbol
        symbol = "AAPL"
        
        print(f"📊 Testing storage for {symbol}...")
        print("-" * 40)
        
        # Get fresh analysis
        print("1️⃣ Generating fresh analysis...")
        analysis = service.analyze_single_stock(symbol)
        print(f"   ✅ Analysis generated with {len(analysis)} top-level fields")
        
        # Store in database
        print("2️⃣ Storing in database...")
        success = repository.store_stock_analysis(symbol, analysis)
        print(f"   ✅ Storage success: {success}")
        
        # Show storage details
        print("3️⃣ Database storage details:")
        print(f"   📍 Namespace: {repository.namespace}")
        print(f"   📍 Set: {repository.set_name}")
        print(f"   📍 Key: {symbol}")
        print(f"   📍 Host: {repository.host}:{repository.port}")
        
        # Retrieve and show what's actually stored
        print("4️⃣ Retrieving stored data...")
        stored_data = repository.get_stock_analysis(symbol)
        
        if stored_data:
            print("   ✅ Data successfully retrieved!")
            print(f"   📋 Top-level fields: {list(stored_data.keys())}")
            
            # Show nested structure
            for key, value in stored_data.items():
                if isinstance(value, dict):
                    print(f"   📂 {key}: {len(value)} fields")
                    for subkey in list(value.keys())[:5]:  # Show first 5 subfields
                        print(f"      └─ {subkey}: {type(value[subkey]).__name__}")
                    if len(value) > 5:
                        print(f"      └─ ... and {len(value)-5} more fields")
                else:
                    print(f"   📄 {key}: {type(value).__name__} = {value}")
        else:
            print("   ❌ No data retrieved!")
            
        return stored_data
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_raw_aerospike_access():
    """Test direct Aerospike database access to see raw storage"""
    print("\n🔧 Raw Aerospike Database Access")
    print("=" * 50)
    
    try:
        # Connect directly to Aerospike
        config = {
            'hosts': [('127.0.0.1', 3000)]
        }
        client = aerospike.client(config).connect()
        print("✅ Direct Aerospike connection established")
        
        # Define the key
        namespace = "financial_data"
        set_name = "stock_analysis"
        symbol = "AAPL"
        key = (namespace, set_name, symbol)
        
        print(f"📍 Looking for key: {key}")
        
        # Get raw record
        (key_tuple, metadata, record) = client.get(key)
        
        print("📋 Raw database record:")
        print(f"   Key: {key_tuple}")
        print(f"   Metadata: {metadata}")
        print(f"   Record bins: {list(record.keys()) if record else 'None'}")
        
        if record:
            for bin_name, bin_data in record.items():
                print(f"   📦 Bin '{bin_name}':")
                if isinstance(bin_data, str):
                    try:
                        # Try to parse as JSON
                        parsed = json.loads(bin_data)
                        print(f"      📊 JSON data with {len(parsed)} fields")
                        if isinstance(parsed, dict):
                            for k, v in list(parsed.items())[:3]:  # Show first 3 fields
                                print(f"         └─ {k}: {type(v).__name__}")
                    except:
                        print(f"      📄 String data: {bin_data[:100]}...")
                else:
                    print(f"      📄 {type(bin_data).__name__}: {bin_data}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Raw access failed: {e}")

def test_database_keys():
    """List all keys stored in the database"""
    print("\n🗂️  Database Keys Inventory")
    print("=" * 40)
    
    try:
        repository = AerospikeRepository()
        
        # Test multiple symbols to see what's stored
        test_symbols = ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'AMZN', 'META']
        
        stored_symbols = []
        
        for symbol in test_symbols:
            data = repository.get_stock_analysis(symbol)
            if data:
                stored_symbols.append(symbol)
                print(f"✅ {symbol}: Stored (last updated: {data.get('timestamp', 'unknown')})")
            else:
                print(f"❌ {symbol}: Not found")
        
        print(f"\n📊 Summary:")
        print(f"   Total symbols in database: {len(stored_symbols)}")
        print(f"   Stored symbols: {', '.join(stored_symbols)}")
        
    except Exception as e:
        print(f"❌ Keys inventory failed: {e}")

def test_data_persistence():
    """Test if data persists across connections"""
    print("\n🔄 Data Persistence Test")
    print("=" * 35)
    
    try:
        # Create new repository instance (simulates new connection)
        repo1 = AerospikeRepository()
        data1 = repo1.get_stock_analysis("AAPL")
        
        if data1:
            timestamp1 = data1.get('timestamp')
            print(f"✅ Connection 1: Data found (timestamp: {timestamp1})")
        else:
            print("❌ Connection 1: No data found")
            return
        
        # Close and create another instance
        del repo1
        
        repo2 = AerospikeRepository()
        data2 = repo2.get_stock_analysis("AAPL")
        
        if data2:
            timestamp2 = data2.get('timestamp')
            print(f"✅ Connection 2: Data found (timestamp: {timestamp2})")
            
            if timestamp1 == timestamp2:
                print("🎉 Data persistence confirmed - same timestamp across connections!")
            else:
                print("⚠️  Different timestamps - data may have been updated")
        else:
            print("❌ Connection 2: No data found")
        
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")

if __name__ == "__main__":
    stored_data = test_database_storage()
    test_raw_aerospike_access()
    test_database_keys()
    test_data_persistence()