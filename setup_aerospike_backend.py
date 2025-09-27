#!/usr/bin/env python3
"""
Quick Setup Script for Aerospike Backend
Installs dependencies and tests the setup
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Aerospike Backend Quick Setup")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    success = run_command("pip install -r requirements.txt", "Installing requirements")
    
    if not success:
        print("❌ Failed to install dependencies")
        return False
    
    # Test Aerospike direct connection
    print("\n🧪 Testing Aerospike connection...")
    success = run_command("python test_aerospike_direct.py", "Testing Aerospike")
    
    if not success:
        print("⚠️  Aerospike test failed, but continuing...")
    
    # Start backend in background for testing
    print("\n🌐 Starting backend for testing...")
    print("   Starting backend in background...")
    
    # Create a simple test
    test_script = '''
import requests
import time
import sys

# Wait for backend to start
time.sleep(3)

try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=10)
    if response.status_code == 200:
        print("✅ Backend is responding")
        
        # Test switch to Aerospike
        switch_response = requests.post("http://localhost:8000/api/v1/data/switch/primary", timeout=10)
        if switch_response.status_code == 200:
            data = switch_response.json()
            if data.get("success"):
                print("✅ Successfully switched to Aerospike")
            else:
                print("⚠️  Could not switch to Aerospike:", data.get("message"))
        
        sys.exit(0)
    else:
        print(f"❌ Backend returned {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Backend test failed: {e}")
    sys.exit(1)
'''
    
    with open('temp_test.py', 'w') as f:
        f.write(test_script)
    
    try:
        # Start backend and test
        backend_process = subprocess.Popen([sys.executable, 'run_backend.py'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
        
        # Run test
        test_result = run_command(f"{sys.executable} temp_test.py", "Testing backend startup")
        
        # Cleanup
        backend_process.terminate()
        backend_process.wait(timeout=5)
        
        if os.path.exists('temp_test.py'):
            os.remove('temp_test.py')
        
        if test_result:
            print("\n🎉 Setup completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Start the backend: python run_backend.py")
            print("2. Run full tests: python test_aerospike_integration.py")
            print("3. View API docs: http://localhost:8000/docs")
            print("4. Test individual endpoints: python test_backend.py")
            return True
        else:
            print("\n⚠️  Setup completed with warnings")
            return False
            
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False
    finally:
        if os.path.exists('temp_test.py'):
            os.remove('temp_test.py')


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)