#!/usr/bin/env python3
"""
Squeezing Washing Bottle Function
Uses the enhanced partial configuration system to squeeze the washing bottle.
"""

import time
import json
from pathlib import Path
from execute_rules import execute_configuration


def squeeze_washing_bottle(duration: float, squeeze_angle: float = 0.3, base_config_name: str = "dispensing_red_to_beaker", release_config_name: str = None):
    """
    Squeeze the washing bottle using the partial configuration system.
    
    Args:
        duration (float): Duration in seconds to hold the squeeze
        squeeze_angle (float): Angle in radians for the squeeze (default: 0.3)
        base_config_name (str): Base configuration to move to first (default: "dispensing_red_to_beaker")
        release_config_name (str): Configuration to return to after squeeze (default: same as base_config_name)
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Use base config as release config if not specified
    if release_config_name is None:
        release_config_name = base_config_name
    
    print(f"🧴 Starting washing bottle squeeze using partial configuration system...")
    print(f"⏱️  Duration: {duration}s")
    print(f"🎯 Squeeze angle: {squeeze_angle} radians")
    print(f"📋 Base configuration: {base_config_name}")
    print(f"� Release configuration: {release_config_name}")
    
    try:
        # Step 1: Move to base position
        print(f"🎯 Step 1: Moving to base position ({base_config_name})...")
        if not execute_configuration(base_config_name):
            print(f"❌ Failed to execute base configuration: {base_config_name}")
            return False
        
        # Brief pause between movements
        time.sleep(1.0)
        
        # Step 2: Create and execute dynamic squeeze configuration
        print(f"🤏 Step 2: Creating dynamic squeeze configuration (j6: {squeeze_angle})...")
        
        # Create temporary squeeze configuration with custom angle
        squeeze_config = {
            "name": f"dynamic_squeeze_{squeeze_angle}",
            "description": f"Dynamic squeeze configuration with j6={squeeze_angle} radians",
            "source": {
                "type": "dynamic_partial_configuration",
                "purpose": "custom_bottle_squeezing"
            },
            "timestamp": "2025-07-16",
            "configuration": {
                "right_arm": {
                    "name": "SO-101 Right Arm",
                    "joints": {
                        "j6": squeeze_angle
                    },
                    "description": f"Right arm with custom j6={squeeze_angle} for dynamic squeezing"
                }
            }
        }
        
        # Save temporary configuration
        temp_config_path = Path("temp_rules/dynamic_squeeze_temp.json")
        with open(temp_config_path, 'w') as f:
            json.dump(squeeze_config, f, indent=2)
        
        # Execute squeeze using partial configuration
        if not execute_configuration("dynamic_squeeze_temp"):
            print("❌ Failed to execute squeeze configuration")
            return False
        
        # Step 3: Hold squeeze for specified duration
        print(f"⏸️  Step 3: Holding squeeze for {duration} seconds...")
        time.sleep(duration)
        
        # Step 4: Release squeeze by returning to release configuration
        print(f"🔓 Step 4: Releasing squeeze (returning to {release_config_name})...")
        if not execute_configuration(release_config_name):
            print(f"❌ Failed to execute release configuration: {release_config_name}")
            return False
        
        # Cleanup temporary file
        if temp_config_path.exists():
            temp_config_path.unlink()
        
        print("🎉 Washing bottle squeeze completed successfully using partial configuration system!")
        return True
        
    except Exception as e:
        print(f"❌ Error during bottle squeeze: {e}")
        return False


def squeeze_washing_bottle_simple(duration: float = 2.0):
    """
    Simple squeeze function using the predefined squeeze_washing_bottle partial configuration.
    
    Args:
        duration (float): Duration in seconds to hold the squeeze (default: 2.0)
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print(f"🧴 Starting simple washing bottle squeeze...")
    print(f"⏱️  Duration: {duration}s")
    print(f"🎯 Using predefined squeeze_washing_bottle partial configuration")
    
    try:
        # Step 1: Execute squeeze using predefined partial configuration
        print(f"🤏 Step 1: Executing squeeze_washing_bottle configuration...")
        if not execute_configuration("squeeze_washing_bottle"):
            print("❌ Failed to execute squeeze_washing_bottle configuration")
            return False
        
        # Step 2: Hold squeeze for specified duration
        print(f"⏸️  Step 2: Holding squeeze for {duration} seconds...")
        time.sleep(duration)
        
        # Step 3: Release squeeze using dispensing configuration
        print(f"🔓 Step 3: Releasing squeeze (returning to dispensing_red_to_beaker)...")
        if not execute_configuration("dispensing_red_to_beaker"):
            print("❌ Failed to execute release configuration")
            return False
        
        print("🎉 Simple washing bottle squeeze completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during simple bottle squeeze: {e}")
        return False


def main():
    """
    Main function for command line usage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Squeeze washing bottle using partial configuration system")
    parser.add_argument("duration", type=float, help="Duration in seconds to hold squeeze")
    parser.add_argument("--angle", type=float, default=0.3, help="Squeeze angle in radians (default: 0.3)")
    parser.add_argument("--base-config", type=str, default="dispensing_red_to_beaker", help="Base configuration name")
    parser.add_argument("--release-config", type=str, help="Release configuration name (default: same as base)")
    parser.add_argument("--simple", action="store_true", help="Use simple predefined squeeze_washing_bottle configuration")
    
    args = parser.parse_args()
    
    if args.simple:
        success = squeeze_washing_bottle_simple(args.duration)
    else:
        success = squeeze_washing_bottle(args.duration, args.angle, args.base_config, args.release_config)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
