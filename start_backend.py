#!/usr/bin/env python3
"""
Start Simple Backend - Troubleshooting Version
This version provides better error messages and diagnostics
"""

import sys
import os

print("🚀 Starting Simple Aerospike Backend...")
print("=" * 50)

# Check if we're in the right directory
if not os.path.exists("simple_backend.py"):
    print("❌ simple_backend.py not found!")
    print("Make sure you're in the VTHacks26 directory")
    exit(1)

# Test imports first
print("🔧 Checking dependencies...")
try:
    import fastapi
    print("   ✅ FastAPI available")
except ImportError:
    print("   ❌ FastAPI missing - install with:")
    print("   pip3 install --break-system-packages fastapi uvicorn")
    exit(1)

try:
    import aerospike
    print("   ✅ Aerospike client available")
except ImportError:
    print("   ❌ Aerospike client missing - install with:")
    print("   pip3 install --break-system-packages aerospike")
    exit(1)

# Test Aerospike connection
print("🔗 Testing Aerospike connection...")
try:
    config = {'hosts': [('127.0.0.1', 3000)], 'policies': {'timeout': 5000}}
    client = aerospike.client(config).connect()
    client.close()
    print("   ✅ Aerospike connection successful")
except Exception as e:
    print(f"   ⚠️  Aerospike connection failed: {e}")
    print("   Make sure Aerospike is running: docker-compose up -d")
    print("   Continuing anyway...")

# Kill any existing backend
import subprocess
try:
    subprocess.run(["pkill", "-f", "simple_backend.py"], 
                   capture_output=True, text=True)
    print("🧹 Killed any existing backend processes")
except:
    pass

print("\n🚀 Starting backend server...")
print("📊 API will be available at: http://localhost:8000")
print("📚 API Documentation: http://localhost:8000/docs")
print("🧪 Test endpoints:")
print("   http://localhost:8000/health")
print("   http://localhost:8000/test-aerospike")
print("   http://localhost:8000/risk-level/AAPL")
print("\n💡 Press Ctrl+C to stop the server")
print("=" * 50)

# Import and run the backend
try:
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Import the backend components
    from simple_backend import app
    import uvicorn
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n👋 Backend stopped by user")
except Exception as e:
    print(f"\n❌ Backend failed to start: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're in the VTHacks26 directory")
    print("2. Install dependencies: pip3 install --break-system-packages fastapi uvicorn aerospike")
    print("3. Start Aerospike: docker-compose up -d")
    print("4. Try again: python3 start_backend.py")
    exit(1)