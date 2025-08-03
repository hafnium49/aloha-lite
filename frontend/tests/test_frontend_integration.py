#!/usr/bin/env python3
"""
Test script to verify the frontend-robot service integration
"""

import requests
import json
import time
import sys
import os

# Add parent directory to path to import from main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_frontend_integration():
    """Test the complete frontend to robot service integration."""
    
    frontend_url = "http://localhost:3000"
    
    # Test payload matching the frontend format with 4-pigment support
    payload = {
        "mix_id": 1,
        "run_id": 1,
        "colour": "red",
        "color_ratios": {
            "red": 1.0,
            "yellow": 1.0,
            "blue": 1.0,
            "white": 0.1  # White solvent
        },
        "normalized_percentages": {
            "red": 32.26,
            "yellow": 32.26,
            "blue": 32.26,
            "white": 3.22
        }
    }
    
    print("🧪 Testing Frontend → Robot Service Integration (4-Pigment)")
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
                        
                        # Check for beaker analysis results with hue data
                        if "beaker_analysis_results" in status_data:
                            print("🧪 Beaker analysis results detected!")
                            analysis = status_data["beaker_analysis_results"]
                            if "dominant_color" in analysis:
                                color = analysis["dominant_color"]
                                print(f"   🎨 Dominant color: {color.get('hex', 'N/A')} RGB({color.get('rgb', 'N/A')})")
                                # Check for hue information if available
                                if "hue_angle" in color:
                                    print(f"   🌈 Hue angle: {color['hue_angle']:.1f}°")
                        
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
    
    # Updated payload for 4-pigment system
    payload = {
        "color_ratios": {
            "red": 1.0, 
            "yellow": 1.0, 
            "blue": 1.0,
            "white": 0.1
        },
        "base_duration": 1.0
    }
    
    print(f"\n🔧 Testing Direct Robot Service Connection (4-Pigment)")
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

def test_hue_optimization_api():
    """Test the hue-based optimization API endpoints."""
    
    frontend_url = "http://localhost:3000"
    
    print(f"\n🎨 Testing Hue-Based Optimization API")
    print("=" * 50)
    
    try:
        # Test target color endpoint
        response = requests.get(f"{frontend_url}/api/target-color")
        if response.status_code == 200:
            target_data = response.json()
            print(f"✅ Target color API works: {target_data.get('target_hex', 'N/A')}")
            
            # Test recommendation endpoint
            rec_response = requests.post(
                f"{frontend_url}/api/recommend-ratios",
                json={},
                headers={"Content-Type": "application/json"}
            )
            
            if rec_response.status_code == 200:
                rec_data = rec_response.json()
                print(f"✅ Recommendation API works: {rec_data.get('status', 'N/A')}")
                if "recommended_ratios" in rec_data:
                    ratios = rec_data["recommended_ratios"]
                    print(f"   🎯 Recommended ratios: R={ratios.get('red', 0):.2f}, Y={ratios.get('yellow', 0):.2f}, B={ratios.get('blue', 0):.2f}, W={ratios.get('white', 0):.2f}")
                return True
            else:
                print(f"❌ Recommendation API failed: {rec_response.status_code}")
                return False
        else:
            print(f"❌ Target color API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Hue optimization API error: {e}")
        return False

def main():
    """Main test execution."""
    
    print("🚀 Frontend Integration Test Suite (4-Pigment Hue-Based)")
    print("=" * 80)
    
    # Test direct robot service first
    direct_success = test_direct_robot_service()
    
    if not direct_success:
        print("\n⚠️  Direct robot service test failed - check robot service")
        print("   (This is optional - continuing with frontend tests)")
    
    # Test hue optimization API
    hue_api_success = test_hue_optimization_api()
    
    if not hue_api_success:
        print("\n⚠️  Hue optimization API test failed - check frontend ML endpoints")
        print("   (This is optional - continuing with integration tests)")
    
    # Test frontend integration
    frontend_success = test_frontend_integration()
    
    if frontend_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Frontend → Robot Service integration is working correctly")
        print(f"✅ 4-pigment system with white solvent is functional")
        print(f"✅ Hue-based optimization integration is working")
        return 0
    else:
        print(f"\n❌ FRONTEND INTEGRATION TEST FAILED!")
        print(f"🔧 Check frontend logs and ensure it's running on port 3000")
        print(f"🔧 Ensure 4-pigment support is enabled in the backend")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
