#!/usr/bin/env python3
"""
Test script for multi-color dispensing backend.
Updated for vision_bridge/tests location.
"""

import json
import time
import requests
import sys
import os

# Add the parent directories to path for any needed imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_multi_color_dispensing():
    """Test the multi-color dispensing API."""
    
    # Test payload matching the frontend format
    payload = {
        "mix_id": 1,
        "run_id": 1,
        "colour": "yellow",  # dominant color
        "color_ratios": {
            "red": 1.5,
            "yellow": 2.3,
            "blue": 0.8
        },
        "normalized_percentages": {
            "red": 32.61,
            "yellow": 50.00,
            "blue": 17.39
        }
    }
    
    print("🧪 Testing Multi-Color Dispensing API")
    print("=" * 50)
    
    try:
        # Start dispensing
        print(f"📤 Sending request: {json.dumps(payload, indent=2)}")
        response = requests.post(
            "http://localhost:8080/robot/dispense",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return
        
        result = response.json()
        cmd_id = result["cmd_id"]
        print(f"✅ Dispensing started with cmd_id: {cmd_id}")
        
        # Poll status
        print("\n📊 Polling status...")
        max_polls = 30  # 30 seconds max
        
        for i in range(max_polls):
            time.sleep(1)
            
            status_response = requests.get(f"http://localhost:8080/robot/{cmd_id}/status")
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                break
            
            status = status_response.json()
            current_status = status.get("status", "unknown")
            current_op = status.get("current_operation", "")
            
            print(f"  Status: {current_status} {current_op}")
            
            if current_status in ["completed", "failed"]:
                break
                
            if "color_operations" in status:
                operations = status["color_operations"]
                for op in operations:
                    print(f"    {op['color']}: {op['status']} ({op['duration']:.2f}s)")
        
        # Final status
        final_status = status_response.json() if status_response.status_code == 200 else {}
        
        if final_status.get("status") == "completed":
            print("🎉 Multi-color dispensing completed successfully!")
            
            if "color_operations" in final_status:
                print("\n📋 Operation Summary:")
                for op in final_status["color_operations"]:
                    print(f"  • {op['color'].capitalize()}: {op['duration']:.2f}s (ratio: {op['ratio']})")
        elif final_status.get("status") == "failed":
            error_msg = final_status.get("error_message", "Unknown error")
            print(f"❌ Dispensing failed: {error_msg}")
        else:
            print("⏱️  Dispensing still in progress or timed out")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to robot service. Make sure Docker services are running.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_multi_color_dispensing()
