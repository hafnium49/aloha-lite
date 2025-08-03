#!/usr/bin/env python3
"""
Test the robot service API endpoints with the new enable_duration_normalization flag.
Tests both the /robot/dispense and /multi_color_dispensing endpoints.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_multi_color_dispensing_with_normalization_enabled():
    """Test /multi_color_dispensing endpoint with normalization enabled"""
    
    print("🧪 Testing /multi_color_dispensing with normalization ENABLED")
    print("=" * 70)
    
    test_data = {
        "color_ratios": {
            "red": 30.0,
            "yellow": 50.0,
            "blue": 20.0
        },
        "base_duration": 2.0,
        "enable_duration_normalization": True
    }
    
    try:
        print(f"📤 Sending request to {BASE_URL}/multi_color_dispensing")
        print(f"   Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/multi_color_dispensing", json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request successful!")
            print(f"   Command ID: {result.get('cmd_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Procedure: {result.get('procedure')}")
            print(f"   Color Ratios: {result.get('color_ratios')}")
            print(f"   Base Duration: {result.get('base_duration')}")
            print(f"   Normalization Enabled: {result.get('enable_duration_normalization')}")
            
            # Check task status
            cmd_id = result.get('cmd_id')
            if cmd_id:
                time.sleep(1)  # Wait a moment for task to start
                status_response = requests.get(f"{BASE_URL}/task_status/{cmd_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Task Status: {status_data.get('status')}")
                
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multi_color_dispensing_with_normalization_disabled():
    """Test /multi_color_dispensing endpoint with normalization disabled"""
    
    print("\n🧪 Testing /multi_color_dispensing with normalization DISABLED")
    print("=" * 70)
    
    test_data = {
        "color_ratios": {
            "red": 30.0,
            "yellow": 50.0,
            "blue": 20.0
        },
        "base_duration": 3.0,
        "enable_duration_normalization": False
    }
    
    try:
        print(f"📤 Sending request to {BASE_URL}/multi_color_dispensing")
        print(f"   Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/multi_color_dispensing", json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request successful!")
            print(f"   Command ID: {result.get('cmd_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Procedure: {result.get('procedure')}")
            print(f"   Color Ratios: {result.get('color_ratios')}")
            print(f"   Base Duration: {result.get('base_duration')}")
            print(f"   Normalization Enabled: {result.get('enable_duration_normalization')}")
            
            # Check task status
            cmd_id = result.get('cmd_id')
            if cmd_id:
                time.sleep(1)  # Wait a moment for task to start
                status_response = requests.get(f"{BASE_URL}/task_status/{cmd_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Task Status: {status_data.get('status')}")
                
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multi_color_dispensing_default_normalization():
    """Test /multi_color_dispensing endpoint without specifying normalization (should use default)"""
    
    print("\n🧪 Testing /multi_color_dispensing with DEFAULT normalization setting")
    print("=" * 70)
    
    test_data = {
        "color_ratios": {
            "red": 25.0,
            "yellow": 35.0,
            "blue": 40.0
        },
        "base_duration": 1.5
        # Note: enable_duration_normalization not specified - should use default (false)
    }
    
    try:
        print(f"📤 Sending request to {BASE_URL}/multi_color_dispensing")
        print(f"   Data: {json.dumps(test_data, indent=2)}")
        print(f"   Note: enable_duration_normalization not specified (uses default)")
        
        response = requests.post(f"{BASE_URL}/multi_color_dispensing", json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request successful!")
            print(f"   Command ID: {result.get('cmd_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Color Ratios: {result.get('color_ratios')}")
            print(f"   Base Duration: {result.get('base_duration')}")
            print(f"   Normalization Enabled (default): {result.get('enable_duration_normalization')}")
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_robot_dispense_with_normalization():
    """Test /robot/dispense endpoint with multi-color data and normalization flag"""
    
    print("\n🧪 Testing /robot/dispense with multi-color and normalization")
    print("=" * 70)
    
    test_data = {
        "mix_id": 1,
        "run_id": 1,
        "colour": "red",  # Required for compatibility
        "color_ratios": {
            "red": 40.0,
            "yellow": 30.0,
            "blue": 30.0
        },
        "normalized_percentages": {
            "red": 40.0,
            "yellow": 30.0,
            "blue": 30.0
        },
        "enable_duration_normalization": True
    }
    
    try:
        print(f"📤 Sending request to {BASE_URL}/robot/dispense")
        print(f"   Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/robot/dispense", json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request successful!")
            print(f"   Command ID: {result.get('cmd_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Procedure: {result.get('procedure')}")
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_server_health():
    """Test if the robot service server is running"""
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Robot service server is responding")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to robot service server: {e}")
        print(f"   Make sure the server is running on {BASE_URL}")
        return False

def main():
    print("🚀 Robot Service API Tests - Normalization Feature")
    print("=" * 70)
    
    # Test server health first
    if not test_server_health():
        print("\n❌ Server health check failed. Please start the robot service server first.")
        print("   Run: REQUIRE_MODEL=false REQUIRE_ROBOT=false python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print("\n")
    
    # Run all tests
    tests = [
        test_multi_color_dispensing_with_normalization_enabled,
        test_multi_color_dispensing_with_normalization_disabled, 
        test_multi_color_dispensing_default_normalization,
        test_robot_dispense_with_normalization
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {i+1}. {test_func.__name__}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The normalization feature is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs and implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
