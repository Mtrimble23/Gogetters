#!/usr/bin/env python3
"""
Diagnostic Script for Simple Backend Issues
Run this to identify what's wrong with simple_backend.py
"""

print("🔧 Simple Backend Diagnostic Tool")
print("=" * 50)

# Test 1: Python version
import sys
print(f"\n1. Python Version: {sys.version}")

# Test 2: Required imports
print("\n2. Testing Required Imports:")

try:
    import fastapi
    print("   ✅ FastAPI available")
    print(f"      Version: {fastapi.__version__}")
except ImportError as e:
    print(f"   ❌ FastAPI missing: {e}")
    print("   Fix: pip3 install --break-system-packages fastapi")

try:
    import uvicorn
    print("   ✅ Uvicorn available")
except ImportError as e:
    print(f"   ❌ Uvicorn missing: {e}")
    print("   Fix: pip3 install --break-system-packages uvicorn")

try:
    import aerospike
    print("   ✅ Aerospike client available")
    try:
        print(f"      Version: {aerospike.__version__}")
    except AttributeError:
        print("      Version: Available (version info not accessible)")
except ImportError as e:
    print(f"   ❌ Aerospike client missing: {e}")
    print("   Fix: pip3 install --break-system-packages aerospike")

# Test 3: Port availability
print("\n3. Testing Port 8000:")
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result == 0:
        print("   ⚠️  Port 8000 is already in use")
        print("   Fix: pkill -f simple_backend.py")
    else:
        print("   ✅ Port 8000 is available")
except Exception as e:
    print(f"   ❌ Port check failed: {e}")

# Test 4: Aerospike connection
print("\n4. Testing Aerospike Connection:")
try:
    import aerospike
    config = {
        'hosts': [('127.0.0.1', 3000)],
        'policies': {'timeout': 5000}
    }
    
    client = aerospike.client(config).connect()
    print("   ✅ Aerospike connection successful")
    client.close()
except ImportError:
    print("   ❌ Aerospike client not installed")
except Exception as e:
    print(f"   ❌ Aerospike connection failed: {e}")
    print("   Fix: Make sure Aerospike is running: docker-compose up -d")

# Test 5: File permissions
print("\n5. Testing File Permissions:")
import os
current_file = "simple_backend.py"
if os.path.exists(current_file):
    if os.access(current_file, os.R_OK):
        print(f"   ✅ {current_file} is readable")
    else:
        print(f"   ❌ {current_file} is not readable")
    
    if os.access(current_file, os.X_OK):
        print(f"   ✅ {current_file} is executable")
    else:
        print(f"   ⚠️  {current_file} is not executable")
        print(f"   Fix: chmod +x {current_file}")
else:
    print(f"   ❌ {current_file} not found")

print("\n" + "=" * 50)
print("🚀 QUICK FIXES:")
print("If imports are missing:")
print("   pip3 install --break-system-packages fastapi uvicorn aerospike")
print("\nIf port is busy:")
print("   pkill -f simple_backend.py")
print("\nIf Aerospike is down:")
print("   docker-compose up -d")
print("\nThen try:")
print("   python3 simple_backend.py")