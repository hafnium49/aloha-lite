#!/usr/bin/env python3
"""
Joint Reader for Robot Arms

This script reads joint values from a specified robot arm using the same infrastructure
as sequential_execute.py. It provides a simple interface to query current joint positions
from either the left or right arm.
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
import requests

# Import the existing functionality from execute_rules.py
sys.path.append(str(Path(__file__).parent.parent / "robot_service"))
from execute_rules import PhosphobotJointController

class RobotJointReader:
    """Read joint values from robot arms."""
    
    def __init__(self, server_url: str = "http://localhost:80", 
                 left_arm_id: int = 0, right_arm_id: int = 2):
        """Initialize the joint reader.
        
        Args:
            server_url: URL of the phosphobot server
            left_arm_id: ID of the left arm (default: 0)
            right_arm_id: ID of the right arm (default: 2)
        """
        self.server_url = server_url
        self.left_arm_id = left_arm_id
        self.right_arm_id = right_arm_id
        self.controller = None
        
    def initialize(self):
        """Initialize the robot controller."""
        self.controller = PhosphobotJointController(self.server_url)
        time.sleep(1)
        
        print(f"🔧 Left arm ID: {self.left_arm_id} (5A68011258)")
        print(f"🔧 Right arm ID: {self.right_arm_id} (5A68009540)")
        print(f"🌐 Server URL: {self.server_url}")
    
    def read_joint_values(self, arm_name: str = "left") -> dict:
        """Read joint values from the specified arm.
        
        Args:
            arm_name: Name of the arm ("left" or "right")
            
        Returns:
            Dictionary containing joint information or None if failed
        """
        # Determine robot ID based on arm name
        if arm_name.lower() == "left":
            robot_id = self.left_arm_id
            arm_description = f"Left arm (ID {self.left_arm_id})"
        elif arm_name.lower() == "right":
            robot_id = self.right_arm_id
            arm_description = f"Right arm (ID {self.right_arm_id})"
        else:
            print(f"❌ Invalid arm name: {arm_name}. Use 'left' or 'right'")
            return None
        
        print(f"\n📖 Reading joint values from {arm_description}...")
        
        try:
            # Read joint positions using the controller
            result = self.controller.read_joint_positions(robot_id)
            
            if result and 'angles' in result:
                angles = result['angles']
                
                # Display joint values
                print(f"✅ Successfully read joint values:")
                print(f"   🦾 Arm: {arm_description}")
                print(f"   📊 Joint values:")
                
                joint_names = ["j1 (shoulder_pan)", "j2 (shoulder_lift)", "j3 (elbow)", 
                              "j4 (wrist_1)", "j5 (wrist_2)", "j6 (wrist_3)"]
                
                for i, (name, angle) in enumerate(zip(joint_names, angles)):
                    print(f"      {name}: {angle:.6f} rad")
                
                # Return structured data
                return {
                    "arm": arm_name,
                    "robot_id": robot_id,
                    "timestamp": time.time(),
                    "joints": {
                        "j1": angles[0],
                        "j2": angles[1],
                        "j3": angles[2],
                        "j4": angles[3],
                        "j5": angles[4],
                        "j6": angles[5]
                    },
                    "joint_names": ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"],
                    "units": "radians",
                    "raw_angles": angles
                }
            else:
                print(f"❌ Failed to read joint values from {arm_description}")
                return None
                
        except Exception as e:
            print(f"❌ Error reading joint values: {e}")
            return None
    
    def read_both_arms(self) -> dict:
        """Read joint values from both arms.
        
        Returns:
            Dictionary containing joint information for both arms
        """
        print("\n📖 Reading joint values from both arms...")
        
        results = {}
        
        # Read left arm
        left_result = self.read_joint_values("left")
        if left_result:
            results["left_arm"] = left_result
        
        # Read right arm  
        right_result = self.read_joint_values("right")
        if right_result:
            results["right_arm"] = right_result
            
        return results
    
    def save_joint_values(self, joint_data: dict, filename: str):
        """Save joint values to a JSON file.
        
        Args:
            joint_data: Joint data dictionary
            filename: Output filename
        """
        try:
            # Add metadata
            output_data = {
                "name": f"joint_reading_{int(time.time())}",
                "description": "Joint values captured using joint reader",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": {
                    "method": "real_time_capture",
                    "tool": "joint_reader.py"
                },
                "data": joint_data
            }
            
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"💾 Joint values saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving joint values: {e}")


def main():
    """Main function to run the joint reader."""
    parser = argparse.ArgumentParser(description="Read joint values from robot arms")
    parser.add_argument("--arm", "-a", choices=["left", "right", "both"], 
                       default="left", help="Specify which arm to read (default: left)")
    parser.add_argument("--server", "-s", default="http://localhost:80",
                       help="Phosphobot server URL (default: http://localhost:80)")
    parser.add_argument("--save", "-o", type=str, 
                       help="Save joint values to specified JSON file")
    parser.add_argument("--left-id", type=int, default=0,
                       help="Left arm robot ID (default: 0)")
    parser.add_argument("--right-id", type=int, default=2,
                       help="Right arm robot ID (default: 2)")
    
    args = parser.parse_args()
    
    # Create joint reader
    reader = RobotJointReader(
        server_url=args.server,
        left_arm_id=args.left_id,
        right_arm_id=args.right_id
    )
    
    # Initialize
    reader.initialize()
    
    # Read joint values
    if args.arm == "both":
        joint_data = reader.read_both_arms()
    else:
        joint_data = reader.read_joint_values(args.arm)
    
    # Save if requested
    if args.save and joint_data:
        reader.save_joint_values(joint_data, args.save)
    
    # Print summary
    if joint_data:
        print(f"\n🎯 Summary:")
        if args.arm == "both":
            print(f"   📊 Read joint values from both arms")
            if "left_arm" in joint_data:
                print(f"   🦾 Left arm: {len(joint_data['left_arm']['joints'])} joints")
            if "right_arm" in joint_data:
                print(f"   🦾 Right arm: {len(joint_data['right_arm']['joints'])} joints")
        else:
            print(f"   📊 Read joint values from {args.arm} arm")
            print(f"   🦾 Joint count: {len(joint_data['joints'])}")
        
        if args.save:
            print(f"   💾 Saved to: {args.save}")
    else:
        print(f"\n❌ Failed to read joint values")


if __name__ == "__main__":
    main()
