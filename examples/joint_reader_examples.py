#!/usr/bin/env python3
"""
Example usage of the joint reader functionality.

This script demonstrates how to use the RobotJointReader class to read joint values
from robot arms programmatically.
"""

import sys
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from joint_reader import RobotJointReader

def example_read_single_arm():
    """Example: Read joint values from a single arm."""
    print("=" * 60)
    print("📖 Example: Reading joint values from left arm")
    print("=" * 60)
    
    # Create joint reader
    reader = RobotJointReader(
        server_url="http://localhost:80",
        left_arm_id=0,
        right_arm_id=2
    )
    
    # Initialize
    reader.initialize()
    
    # Read left arm joint values
    joint_data = reader.read_joint_values("left")
    
    if joint_data:
        print(f"\n🎯 Joint data structure:")
        print(f"   Arm: {joint_data['arm']}")
        print(f"   Robot ID: {joint_data['robot_id']}")
        print(f"   Timestamp: {joint_data['timestamp']}")
        print(f"   Units: {joint_data['units']}")
        
        # Access individual joint values
        j1 = joint_data['joints']['j1']
        j6 = joint_data['joints']['j6']  # Gripper joint
        
        print(f"\n🦾 Individual joint access:")
        print(f"   J1 (shoulder_pan): {j1:.6f} rad")
        print(f"   J6 (wrist_3/gripper): {j6:.6f} rad")
        
        # Get all joint values as a list (useful for robot commands)
        all_joints = joint_data['raw_angles']
        print(f"\n📊 All joints as list: {[f'{j:.6f}' for j in all_joints]}")
        
        return joint_data
    else:
        print("❌ Failed to read joint values")
        return None

def example_read_both_arms():
    """Example: Read joint values from both arms."""
    print("\n" + "=" * 60)
    print("📖 Example: Reading joint values from both arms")
    print("=" * 60)
    
    # Create joint reader
    reader = RobotJointReader()
    
    # Initialize
    reader.initialize()
    
    # Read both arms
    joint_data = reader.read_both_arms()
    
    if joint_data:
        print(f"\n🎯 Successfully read both arms:")
        
        if "left_arm" in joint_data:
            left_j6 = joint_data["left_arm"]["joints"]["j6"]
            print(f"   🦾 Left arm J6 (gripper): {left_j6:.6f} rad")
        
        if "right_arm" in joint_data:
            right_j6 = joint_data["right_arm"]["joints"]["j6"]
            print(f"   🦾 Right arm J6 (gripper): {right_j6:.6f} rad")
        
        return joint_data
    else:
        print("❌ Failed to read joint values from both arms")
        return None

def example_save_joint_values():
    """Example: Read and save joint values to a file."""
    print("\n" + "=" * 60)
    print("📖 Example: Reading and saving joint values")
    print("=" * 60)
    
    # Create joint reader
    reader = RobotJointReader()
    
    # Initialize
    reader.initialize()
    
    # Read left arm
    joint_data = reader.read_joint_values("left")
    
    if joint_data:
        # Save to file
        filename = f"captured_joints_{int(time.time())}.json"
        reader.save_joint_values(joint_data, filename)
        print(f"✅ Joint values saved to {filename}")
        return filename
    else:
        print("❌ Failed to read joint values for saving")
        return None

def example_continuous_monitoring():
    """Example: Continuously monitor joint values."""
    print("\n" + "=" * 60)
    print("📖 Example: Continuous joint monitoring (5 readings)")
    print("=" * 60)
    
    # Create joint reader
    reader = RobotJointReader()
    
    # Initialize
    reader.initialize()
    
    print("\n🔄 Starting continuous monitoring...")
    print("📊 Monitoring J6 (gripper) joint for both arms:")
    
    for i in range(5):
        print(f"\n📍 Reading {i+1}/5:")
        
        # Read both arms
        joint_data = reader.read_both_arms()
        
        if joint_data:
            if "left_arm" in joint_data:
                left_j6 = joint_data["left_arm"]["joints"]["j6"]
                print(f"   🦾 Left J6:  {left_j6:.6f} rad")
            
            if "right_arm" in joint_data:
                right_j6 = joint_data["right_arm"]["joints"]["j6"]
                print(f"   🦾 Right J6: {right_j6:.6f} rad")
        else:
            print("   ❌ Failed to read joint values")
        
        # Wait before next reading
        if i < 4:  # Don't wait after the last reading
            time.sleep(2)
    
    print("\n✅ Monitoring complete!")

def main():
    """Run all examples."""
    print("🤖 Joint Reader Examples")
    print("=" * 60)
    
    try:
        # Example 1: Read single arm
        example_read_single_arm()
        
        # Example 2: Read both arms
        example_read_both_arms()
        
        # Example 3: Save joint values
        example_save_joint_values()
        
        # Example 4: Continuous monitoring
        example_continuous_monitoring()
        
        print("\n🎉 All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")

if __name__ == "__main__":
    main()
