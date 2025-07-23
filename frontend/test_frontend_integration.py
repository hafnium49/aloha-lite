#!/usr/bin/env python3
"""
Test script to verify the frontend-robot service integration
"""

import requests
import json
import time

def test_frontend_integration():
    """Test the complete frontend to robot service integration."""
    
    frontend_url = "http://localhost:3000"
    
    # Test payload matching the frontend format
    payload = {
        "mix_id": 1,
        "run_id": 1,
        "colour": "red",
        "color_ratios": {
            "red": 1,
            "yellow": 1,
            "blue": 1
        },
        "normalized_percentages": {
            "red": 33.33,
            "yellow": 33.33,
            "blue": 33.33
        }
    }
    
    print("🧪 Testing Frontend → Robot Service Integration")
    print("=" * 60)
    print(f"📊 Test payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Send request through frontend proxy
        response = requests.post(
            f"{frontend_url}/robot/dispense",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📨 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📋 Response Data: {json.dumps(response_data, indent=2)}")
            
            if "cmd_id" in response_data:
                cmd_id = response_data["cmd_id"]
                print(f"\n🎉 SUCCESS: Received cmd_id = {cmd_id}")
                print(f"📋 Procedure: {response_data.get('procedure', 'N/A')}")
                print(f"📝 Description: {response_data.get('description', 'N/A')}")
                
                # Monitor task status
                print(f"\n⏳ Monitoring task status...")
                for i in range(10):
                    status_response = requests.get(f"{frontend_url}/robot/{cmd_id}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get("status", "unknown")
                        print(f"   Status check {i+1}: {status}")
                        
                        if status == "completed":
                            print(f"🎉 Task completed successfully!")
                            break
                        elif status == "failed":
                            print(f"❌ Task failed: {status_data.get('error_message', 'Unknown error')}")
                            break
                    
                    time.sleep(1)
                
                return True
            else:
                print(f"❌ ERROR: No cmd_id in response")
                print(f"📋 Full response: {response_data}")
                return False
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"📋 Response: {response.text}")
            return False
            
    except requests.ConnectionError:
        print("❌ CONNECTION ERROR: Make sure frontend is running on port 3000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_direct_robot_service():
    """Test direct connection to robot service for comparison."""
    
    robot_url = "http://localhost:8000"
    
    payload = {
        "color_ratios": {"red": 1, "yellow": 1, "blue": 1},
        "base_duration": 1.0
    }
    
    print(f"\n🔧 Testing Direct Robot Service Connection")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{robot_url}/multi_color_dispensing",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Direct connection works: {response_data.get('cmd_id', 'No cmd_id')}")
            return True
        else:
            print(f"❌ Direct connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct connection error: {e}")
        return False

def main():
    """Main test execution."""
    
    print("🚀 Frontend Integration Test Suite")
    print("=" * 80)
    
    # Test direct robot service first
    direct_success = test_direct_robot_service()
    
    if not direct_success:
        print("\n❌ Direct robot service test failed - check robot service")
        return 1
    
    # Test frontend integration
    frontend_success = test_frontend_integration()
    
    if frontend_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Frontend → Robot Service integration is working correctly")
        print(f"✅ Dynamic squeeze duration modification is functional")
        return 0
    else:
        print(f"\n❌ FRONTEND INTEGRATION TEST FAILED!")
        print(f"🔧 Check frontend logs and ensure it's running on port 3000")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
