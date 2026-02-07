#!/usr/bin/env python3
"""
Deployment Test Script
Tests all API endpoints and verifies system is ready
"""

import requests
import json
import sys
import time
from pathlib import Path

BASE_URL = "http://localhost:5000"
ENDPOINTS = {
    "status": "/api/status",
    "events": "/api/events",
    "analytics": "/api/analytics",
}

def test_endpoint(name, path, timeout=5):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ {name:15} | Status: {response.status_code} | Size: {len(str(data))} bytes")
                return True
            except:
                print(f"✅ {name:15} | Status: {response.status_code} | Raw response")
                return True
        else:
            print(f"❌ {name:15} | Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:15} | Connection refused - App not running?")
        return False
    except Exception as e:
        print(f"❌ {name:15} | Error: {str(e)[:50]}")
        return False

def check_files():
    """Verify all required files exist"""
    required = [
        "software/main.py",
        "software/config.py",
        "software/detector.py",
        "software/database_handler.py",
        "config/camera_settings.json",
        "config/detection_config.json",
        "data/camera.db",
    ]
    
    print("\n📁 Checking Files:")
    all_exist = True
    for file in required:
        path = Path(file)
        status = "✅" if path.exists() else "❌"
        print(f"{status} {file}")
        if not path.exists():
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("🚀 AI CAMERA DEPLOYMENT TEST")
    print("=" * 60)
    
    # Check files
    if not check_files():
        print("\n⚠️  Some files missing!")
        return False
    
    # Test API
    print("\n🌐 Testing API Endpoints:")
    print("-" * 60)
    
    results = {}
    for name, path in ENDPOINTS.items():
        results[name] = test_endpoint(name, path)
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🎉 System is ready for deployment!")
        print("\nNext steps:")
        print("1. Configure alerts in config/alert_rules.json")
        print("2. Add known faces to database")
        print("3. Deploy to hardware or keep API running")
        return True
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\nTroubleshooting:")
        print("- Is app running? python software/main.py --api-only")
        print("- Check logs: tail -f camera.log")
        print("- Is port 5000 accessible?")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
