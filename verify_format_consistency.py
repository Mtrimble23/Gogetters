#!/usr/bin/env python3
"""
Verify Stock Format Consistency
Ensures all cached stocks have identical data structure
"""

import requests
import json

API_BASE = "http://localhost:8000"
SUPPORTED_STOCKS = ["AAPL", "AMZN", "GOOGL", "NVDA", "META", "TSLA"]

def get_structure_signature(data):
    """Get a consistent signature of the data structure"""
    def get_keys_recursive(obj, path=""):
        if isinstance(obj, dict):
            keys = []
            for k in sorted(obj.keys()):
                new_path = f"{path}.{k}" if path else k
                keys.append(new_path)
                keys.extend(get_keys_recursive(obj[k], new_path))
            return keys
        elif isinstance(obj, list) and obj:
            return get_keys_recursive(obj[0], f"{path}[0]")
        else:
            return []
    
    return sorted(get_keys_recursive(data))

def verify_format_consistency():
    """Verify all stocks have identical format"""
    print("🔍 Verifying stock format consistency...")
    print("=" * 50)
    
    structures = {}
    
    for symbol in SUPPORTED_STOCKS:
        try:
            response = requests.get(f"{API_BASE}/risk-level/{symbol}")
            if response.status_code == 200:
                data = response.json()
                signature = get_structure_signature(data)
                structures[symbol] = signature
                print(f"✅ {symbol}: {len(signature)} fields")
            else:
                print(f"❌ {symbol}: HTTP {response.status_code}")
                structures[symbol] = None
        except Exception as e:
            print(f"❌ {symbol}: {str(e)}")
            structures[symbol] = None
    
    # Compare all structures
    print("\n📊 Structure Analysis:")
    print("=" * 50)
    
    valid_structures = {k: v for k, v in structures.items() if v is not None}
    
    if len(valid_structures) < 2:
        print("❌ Need at least 2 valid responses to compare")
        return False
    
    reference_symbol = list(valid_structures.keys())[0]
    reference_structure = valid_structures[reference_symbol]
    
    all_identical = True
    
    for symbol, structure in valid_structures.items():
        if structure == reference_structure:
            print(f"✅ {symbol}: IDENTICAL to {reference_symbol}")
        else:
            print(f"❌ {symbol}: DIFFERENT from {reference_symbol}")
            all_identical = False
            
            # Show differences
            missing = set(reference_structure) - set(structure)
            extra = set(structure) - set(reference_structure)
            
            if missing:
                print(f"   Missing fields: {', '.join(missing)}")
            if extra:
                print(f"   Extra fields: {', '.join(extra)}")
    
    print("\n📋 Summary:")
    print("=" * 50)
    
    if all_identical:
        print("🎉 ALL STOCKS HAVE IDENTICAL FORMAT!")
        print(f"📊 Common structure has {len(reference_structure)} fields")
        print(f"✅ All {len(valid_structures)} stocks verified")
        
        # Show sample of common fields
        print("\n🗂️ Sample fields (first 10):")
        for field in reference_structure[:10]:
            print(f"  • {field}")
        if len(reference_structure) > 10:
            print(f"  ... and {len(reference_structure) - 10} more")
            
    else:
        print("❌ INCONSISTENT FORMATS DETECTED!")
        print("Some stocks have different data structures")
    
    return all_identical

if __name__ == "__main__":
    success = verify_format_consistency()
    exit(0 if success else 1)