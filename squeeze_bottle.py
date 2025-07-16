#!/usr/bin/env python3
"""
Squeezing Washing Bottle Function
Dynamically squeezes the right arm end effector for a specified duration and returns to original position.
"""

import time
import json
from pathlib import Path
from execute_rules import PhosphobotJointController


def squeeze_washing_bottle(duration: float, squeeze_angle: float = 0.3, config_name: str = "dispensing_red_to_beaker", left_arm_id: int = 3, right_arm_id: int = 2):
    """
    Squeeze the washing bottle by closing the right arm end effector for a specified duration.
    
    Args:
        duration (float): Duration in seconds to hold the squeeze
        squeeze_angle (float): Angle in radians for the squeeze (default: 0.3)
        config_name (str): Base configuration to use (default: "dispensing_red_to_beaker")
        left_arm_id (int): Left arm robot ID (default: 3)
        right_arm_id (int): Right arm robot ID (default: 2)
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print(f"🧴 Starting washing bottle squeeze...")
    print(f"⏱️  Duration: {duration}s")
    print(f"🎯 Squeeze angle: {squeeze_angle} radians")
    print(f"📋 Base configuration: {config_name}")
    print(f"🔧 Left arm ID: {left_arm_id}, Right arm ID: {right_arm_id}")
    
    try:
        # Initialize controller
        controller = PhosphobotJointController()
        
        # Load base configuration
        config_path = Path(f"temp_rules/{config_name}.json")
        if not config_path.exists():
            # Try from robot_configurations.json
            main_config_path = Path("temp_rules/robot_configurations.json")
            if main_config_path.exists():
                with open(main_config_path, 'r') as f:
                    main_config = json.load(f)
                    if config_name in main_config["configurations"]:
                        base_config = main_config["configurations"][config_name]
                    else:
                        print(f"❌ Configuration '{config_name}' not found in robot_configurations.json")
                        return False
            else:
                print(f"❌ Configuration file not found: {config_path}")
                return False
        else:
            with open(config_path, 'r') as f:
                base_config = json.load(f)
        
        # Extract joint positions
        left_joints = list(base_config["configuration"]["left_arm"]["joints"].values())
        right_joints = list(base_config["configuration"]["right_arm"]["joints"].values())
        
        # Store original right arm j6 position
        original_j6 = right_joints[5]
        
        print(f"📖 Original right arm j6: {original_j6} radians")
        print(f"🎯 Moving to base position...")
        
        # Move to base configuration
        controller.write_joint_positions(left_arm_id, left_joints)
        controller.write_joint_positions(right_arm_id, right_joints)
        
        # Wait a moment for movement to complete
        time.sleep(1.0)
        
        # Create squeeze configuration (modify only right arm j6)
        squeeze_right_joints = right_joints.copy()
        squeeze_right_joints[5] = squeeze_angle
        
        print(f"🤏 Squeezing bottle (j6: {original_j6} → {squeeze_angle})...")
        
        # Execute squeeze (only move right arm)
        controller.write_joint_positions(right_arm_id, squeeze_right_joints)
        
        # Hold squeeze for specified duration
        print(f"⏸️  Holding squeeze for {duration} seconds...")
        time.sleep(duration)
        
        # Release squeeze (return to original j6 position)
        print(f"🔓 Releasing squeeze (j6: {squeeze_angle} → {original_j6})...")
        controller.write_joint_positions(right_arm_id, right_joints)
        
        # Wait for movement to complete
        time.sleep(0.5)
        
        # Read final positions for verification
        print("📖 Reading final joint positions...")
        final_left = controller.read_joint_positions(left_arm_id)
        final_right = controller.read_joint_positions(right_arm_id)
        
        if final_left and 'angles' in final_left:
            print(f"📖 Final left arm joints: {[f'{j:.3f}' for j in final_left['angles']]}")
        if final_right and 'angles' in final_right:
            print(f"📖 Final right arm joints: {[f'{j:.3f}' for j in final_right['angles']]}")
        
        controller.close()
        
        print("🎉 Washing bottle squeeze completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during bottle squeeze: {e}")
        return False


def main():
    """
    Main function for command line usage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Squeeze washing bottle for specified duration")
    parser.add_argument("duration", type=float, help="Duration in seconds to hold squeeze")
    parser.add_argument("--angle", type=float, default=0.3, help="Squeeze angle in radians (default: 0.3)")
    parser.add_argument("--config", type=str, default="dispensing_red_to_beaker", help="Base configuration name")
    parser.add_argument("--left-arm-id", type=int, default=3, help="Left arm robot ID (default: 3)")
    parser.add_argument("--right-arm-id", type=int, default=2, help="Right arm robot ID (default: 2)")
    
    args = parser.parse_args()
    
    success = squeeze_washing_bottle(args.duration, args.angle, args.config, args.left_arm_id, args.right_arm_id)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
