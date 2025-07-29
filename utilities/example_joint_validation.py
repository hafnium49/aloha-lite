#!/usr/bin/env python3
"""
Example Usage of Joint Validation Tools

This script demonstrates how to use the joint validation utilities
for robot configuration management.
"""

import json
from joint_validator import validate_joint_values, check_robot_configuration, print_joint_summary

def example_usage():
    """Demonstrate the joint validation tools."""
    
    print("Joint Validation Tools - Example Usage")
    print("=" * 60)
    
    # Example 1: Validate individual joint values
    print("\n1. Validating Individual Joint Values")
    print("-" * 40)
    
    joints = {
        'j1': 0.5,
        'j2': -2.8,
        'j3': 4.2,      # > π, needs correction
        'j4': -1.5,
        'j5': -4.0,     # < -π, needs correction  
        'j6': 1.2
    }
    
    print_joint_summary(joints, "Before Validation")
    
    normalized_joints, warnings = validate_joint_values(joints)
    
    if warnings:
        print(f"\n⚠️  Issues Found and Fixed:")
        for warning in warnings:
            print(f"  • {warning}")
    
    print_joint_summary(normalized_joints, "After Validation")
    
    # Example 2: Validate a robot configuration
    print("\n\n2. Validating Robot Configuration")
    print("-" * 40)
    
    config = {
        "name": "example_config",
        "configuration": {
            "left_arm": {
                "name": "SO-101 Left Arm",
                "joints": {
                    "j1": 0.5,
                    "j2": -1.2,
                    "j3": 4.5,  # > π
                    "j4": -1.8,
                    "j5": -3.8,  # < -π
                    "j6": 1.0
                }
            },
            "right_arm": {
                "name": "SO-101 Right Arm", 
                "joints": {
                    "j1": 0.3,
                    "j2": -0.8,
                    "j3": 1.0,
                    "j4": -1.2,
                    "j5": 3.5,  # > π
                    "j6": 1.5
                }
            }
        }
    }
    
    print("Original Configuration:")
    for arm_name, arm_config in config["configuration"].items():
        print_joint_summary(arm_config["joints"], f"{arm_name} joints")
    
    # Validate and fix the configuration
    fixed_config, issues = check_robot_configuration(config)
    
    if issues:
        print(f"\n⚠️  Issues Found and Fixed:")
        for issue in issues:
            print(f"  • {issue}")
    
    print("\nFixed Configuration:")
    for arm_name, arm_config in fixed_config["configuration"].items():
        print_joint_summary(arm_config["joints"], f"{arm_name} joints")
    
    # Example 3: Save fixed configuration
    print("\n\n3. Saving Fixed Configuration")
    print("-" * 40)
    
    output_file = "example_fixed_config.json"
    
    try:
        with open(output_file, 'w') as f:
            json.dump(fixed_config, f, indent=2)
        print(f"✅ Fixed configuration saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  • Joint validation ensures all values are in [-π, π]")
    print(f"  • Physical angles remain equivalent after normalization")
    print(f"  • Tools work with individual joints or full configurations")
    print(f"  • Backup files are created automatically when fixing")

if __name__ == "__main__":
    example_usage()
