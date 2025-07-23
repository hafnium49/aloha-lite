#!/usr/bin/env python3
"""
Test script for the beaker analysis functionality
"""
import sys
import os
from pathlib import Path

# Add the parent directory to path to import modules from robot_service
sys.path.append(str(Path(__file__).parent.parent))

# Import from the parent robot_service directory
from sequential_execute import SequentialRobotExecutor

def test_beaker_analysis():
    """Test the beaker analysis special function."""
    print("🧪 Testing Beaker Analysis Function")
    print("=" * 50)
    
    # Create a test executor (without actual robot hardware)
    executor = SequentialRobotExecutor(
        server_url="http://localhost:5000",  # Dummy URL for testing
        left_arm_id=0,
        right_arm_id=2
    )
    
    # Test the special function recognition
    test_commands = [
        "analyze beaker color",
        "beaker analysis", 
        "analyze solution color",
        "color analysis"
    ]
    
    print("\n📋 Testing special function recognition:")
    for cmd in test_commands:
        is_special = executor._is_special_function(cmd)
        print(f"   '{cmd}' -> {'✅ Recognized' if is_special else '❌ Not recognized'}")
    
    print("\n🔬 Testing beaker analysis execution:")
    try:
        # Test the beaker analysis function
        success = executor._execute_beaker_analysis()
        if success:
            print("✅ Beaker analysis test completed successfully!")
        else:
            print("❌ Beaker analysis test failed")
    except Exception as e:
        print(f"❌ Error during beaker analysis test: {e}")
        print("💡 Note: This test requires the vision bridge server to be running")

if __name__ == "__main__":
    test_beaker_analysis()
