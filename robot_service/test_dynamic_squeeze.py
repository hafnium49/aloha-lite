#!/usr/bin/env python3
"""
Test script to verify the modified robot_service with dynamic squeeze duration modification
using sequential_execute.py with temporary sequences.
"""

import requests
import json
import time

# Test the modified multi-color dispensing task with different color ratios
def test_dynamic_squeeze_durations():
    """Test dynamic squeeze duration modification."""
    
    base_url = "http://localhost:8000"
    
    # Test with custom color ratios
    test_ratios = {
        "red": 2.0,    # Should get longer squeeze duration
        "yellow": 1.0, # Should get medium squeeze duration  
        "blue": 0.5    # Should get shorter squeeze duration
    }
    
    payload = {
        "color_ratios": test_ratios,
        "base_duration": 1.0
    }
    
    print("🧪 Testing dynamic squeeze duration modification...")
    print(f"📊 Test color ratios: {test_ratios}")
    print(f"📊 Expected normalized durations (10s total):")
    total_ratio = sum(test_ratios.values())
    for color, ratio in test_ratios.items():
        expected_duration = max(0.5, (ratio / total_ratio) * 10.0)
        print(f"   {color}: {expected_duration:.2f}s")
    
    try:
        # Start the multi-color dispensing task
        response = requests.post(f"{base_url}/multi_color_dispensing", json=payload)
        if response.status_code == 200:
            result = response.json()
            cmd_id = result.get("cmd_id")
            print(f"✅ Task started with cmd_id: {cmd_id}")
            
            # Monitor task progress
            for i in range(30):  # Wait up to 30 seconds
                status_response = requests.get(f"{base_url}/task_status/{cmd_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"⏳ Task status: {status['status']}")
                    
                    if status['status'] == 'completed':
                        print("🎉 Task completed successfully!")
                        break
                    elif status['status'] == 'failed':
                        print(f"❌ Task failed: {status.get('error_message', 'Unknown error')}")
                        break
                        
                time.sleep(1)
            
        else:
            print(f"❌ Failed to start task: {response.status_code} - {response.text}")
            
    except requests.ConnectionError:
        print("❌ Connection error: Make sure robot_service is running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dynamic_squeeze_durations()
