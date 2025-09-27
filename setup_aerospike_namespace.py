#!/usr/bin/env python3
"""
Aerospike Namespace Setup Script
Creates the VTHacks namespace if it doesn't exist
"""

import sys


def setup_aerospike_namespace():
    """Set up the VTHacks namespace in Aerospike"""
    
    print("🔧 Aerospike Namespace Setup")
    print("=" * 50)
    
    try:
        import aerospike
        from aerospike import exception as ex
        print("✅ Aerospike client imported successfully")
    except ImportError:
        print("❌ Aerospike client not installed")
        return False
    
    # Configuration
    config = {
        'hosts': [('127.0.0.1', 3000)],
        'policies': {
            'timeout': 5000
        }
    }
    
    try:
        print("🔗 Connecting to Aerospike...")
        client = aerospike.client(config).connect()
        print("✅ Connected successfully")
        
        # Check existing namespaces
        print("\n📋 Checking existing namespaces...")
        try:
            info_response = client.info('namespaces')
            print(f"Current namespaces: {info_response}")
            
            # Check if VTHacks exists
            namespaces = {}
            for host_info in info_response.values():
                if 'namespaces' in host_info:
                    # Parse namespace list
                    ns_list = host_info.split(';')[0].split('\t')[1] if '\t' in host_info else host_info
                    namespaces[host_info] = ns_list
            
            print(f"📦 Available namespaces: {list(namespaces.values())}")
            
        except Exception as e:
            print(f"⚠️  Could not retrieve namespace info: {e}")
        
        # Try to use 'test' namespace (default in Aerospike)
        print("\n🧪 Testing with 'test' namespace...")
        test_key = ('test', 'finance', 'test_record_001')
        test_data = {
            'symbol': 'TEST',
            'message': 'Hello Aerospike!'
        }
        
        try:
            client.put(test_key, test_data)
            print("✅ Successfully wrote to 'test' namespace")
            
            # Read it back
            (key, metadata, bins) = client.get(test_key)
            print(f"✅ Successfully read from 'test' namespace: {bins}")
            
            # Clean up
            client.remove(test_key)
            print("✅ Test record cleaned up")
            
            print("\n💡 Recommendation: Use 'test' namespace instead of 'VTHacks'")
            print("   Update your backend config to use namespace='test'")
            
            return True
            
        except Exception as e:
            print(f"❌ Test namespace also failed: {e}")
        
        # Try namespace creation (might not work in community edition)
        print("\n🏗️  Attempting to create VTHacks namespace...")
        try:
            # This typically requires Aerospike admin tools, not the Python client
            print("⚠️  Namespace creation requires admin tools")
            print("   Use aql or admin console to create namespace")
            print("   Command: CREATE NAMESPACE VTHacks")
            
        except Exception as e:
            print(f"❌ Could not create namespace: {e}")
        
        client.close()
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def main():
    """Main function"""
    success = setup_aerospike_namespace()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Namespace setup completed")
        print("\n📝 Next steps:")
        print("1. Update backend config to use namespace='test'")
        print("2. Start backend: python3 run_backend.py")
        print("3. Run tests: python3 test_aerospike_integration.py")
    else:
        print("❌ Namespace setup failed")
        print("\n📝 Solutions:")
        print("1. Use 'test' namespace (default in Aerospike)")
        print("2. Or create VTHacks namespace with admin tools")
        print("3. Check Aerospike configuration file")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)