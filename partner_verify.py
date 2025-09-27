#!/usr/bin/env python3
"""
Partner Verification Script
Quick verification that everything is working properly
"""

import requests
import json
import sys
import subprocess
import time

def check_step(step_name, check_func):
    """Run a verification step"""
    print(f"🔍 {step_name}...")
    try:
        success, message = check_func()
        if success:
            print(f"   ✅ {message}")
            return True
        else:
            print(f"   ❌ {message}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_docker():
    """Check if Docker and Aerospike are running"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'aerospike' in result.stdout:
            return True, "Aerospike container running"
        else:
            return False, "Aerospike container not found"
    except:
        return False, "Docker not available or not running"

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Backend healthy: {data.get('service')}"
        else:
            return False, f"Backend returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Backend not running on port 8000. Did you start it with: nohup python3 simple_backend.py > backend.log 2>&1 & ?"
    except Exception as e:
        return False, f"Health check failed: {e}"

def check_aerospike_connection():
    """Check if Aerospike integration works"""
    try:
        response = requests.get('http://localhost:8000/test-aerospike', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True, "Aerospike integration working"
            else:
                return False, f"Aerospike test failed: {data.get('error')}"
        else:
            return False, f"Aerospike test returned {response.status_code}"
    except Exception as e:
        return False, f"Aerospike connection test failed: {e}"

def check_risk_analysis():
    """Check if risk analysis works"""
    try:
        response = requests.get('http://localhost:8000/risk-level/AAPL', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                risk_level = data.get('risk_level')
                return True, f"Risk analysis working, AAPL risk: {risk_level}"
            else:
                return False, "Risk analysis returned unsuccessful"
        else:
            return False, f"Risk analysis returned {response.status_code}"
    except Exception as e:
        return False, f"Risk analysis failed: {e}"

def check_batch_processing():
    """Check if batch processing works"""
    try:
        payload = {"symbols": ["MSFT", "GOOGL"]}
        response = requests.post('http://localhost:8000/risk-level', 
                               json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analyzed = data.get('total_analyzed', 0)
                return True, f"Batch processing working, analyzed {analyzed} symbols"
            else:
                return False, "Batch processing unsuccessful"
        else:
            return False, f"Batch processing returned {response.status_code}"
    except Exception as e:
        return False, f"Batch processing failed: {e}"

def main():
    """Run all verification checks"""
    print("🧪 VTHacks26 Partner Verification")
    print("=" * 50)
    
    checks = [
        ("Docker & Aerospike", check_docker),
        ("Backend Health", check_backend_health), 
        ("Aerospike Connection", check_aerospike_connection),
        ("Risk Analysis", check_risk_analysis),
        ("Batch Processing", check_batch_processing)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, func in checks:
        if check_step(name, func):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Your setup is ready!")
        print("\n🚀 You can now:")
        print("   - View API docs: http://localhost:8000/docs")
        print("   - Test risk analysis: curl http://localhost:8000/risk-level/AAPL")
        print("   - Start building your application!")
        return 0
    else:
        print(f"⚠️  {total - passed} checks failed. Please review the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   - Run: python3 diagnose_backend.py")
        print("   - Check: docker ps (should show aerospike)")
        print("   - Ensure: python3 simple_backend.py is running")
        return 1

if __name__ == "__main__":
    sys.exit(main())