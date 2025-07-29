#!/usr/bin/env python3
"""
Simple Joint Validator Utility

A lightweight utility for validating and normalizing robot joint values.
This can be imported as a module or used as a standalone script.
"""

import json
import math
from typing import Dict, List, Tuple, Any

def normalize_angle(angle: float) -> float:
    """
    Normalize an angle to be within [-π, π] range.
    
    Args:
        angle: Angle in radians
        
    Returns:
        Normalized angle within [-π, π]
    """
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle

def validate_joint_values(joints: Dict[str, float]) -> Tuple[Dict[str, float], List[str]]:
    """
    Validate and normalize joint values.
    
    Args:
        joints: Dictionary of joint names to values
        
    Returns:
        Tuple of (normalized_joints, list_of_warnings)
    """
    normalized_joints = {}
    warnings = []
    
    for joint_name, value in joints.items():
        if not isinstance(value, (int, float)):
            warnings.append(f"Non-numeric value for {joint_name}: {value}")
            normalized_joints[joint_name] = value
            continue
            
        original_value = float(value)
        normalized_value = normalize_angle(original_value)
        
        if abs(original_value - normalized_value) > 1e-6:
            warnings.append(f"{joint_name}: {original_value:.6f} -> {normalized_value:.6f} (normalized)")
        
        normalized_joints[joint_name] = normalized_value
    
    return normalized_joints, warnings

def check_robot_configuration(config: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Check and normalize joint values in a robot configuration.
    
    Args:
        config: Robot configuration dictionary
        
    Returns:
        Tuple of (updated_config, list_of_issues)
    """
    updated_config = json.loads(json.dumps(config))  # Deep copy
    all_issues = []
    
    if 'configuration' not in updated_config:
        return updated_config, all_issues
    
    configuration = updated_config['configuration']
    
    for arm_name in ['left_arm', 'right_arm']:
        if arm_name not in configuration:
            continue
            
        arm_config = configuration[arm_name]
        if 'joints' not in arm_config:
            continue
        
        joints = arm_config['joints']
        normalized_joints, warnings = validate_joint_values(joints)
        
        # Update joints with normalized values
        arm_config['joints'] = normalized_joints
        
        # Add arm name to warnings
        for warning in warnings:
            all_issues.append(f"{arm_name}.{warning}")
    
    return updated_config, all_issues

def print_joint_summary(joints: Dict[str, float], title: str = "Joint Values"):
    """Print a formatted summary of joint values."""
    print(f"\n{title}:")
    print("-" * 40)
    for joint_name in ['j1', 'j2', 'j3', 'j4', 'j5', 'j6']:
        if joint_name in joints:
            value = joints[joint_name]
            in_range = -math.pi <= value <= math.pi
            status = "✅" if in_range else "❌"
            print(f"  {joint_name}: {value:8.6f} rad {status}")

if __name__ == "__main__":
    # Example usage when run as a script
    print("Joint Validator Utility")
    print("=" * 50)
    
    # Example joint values (some out of range)
    example_joints = {
        'j1': 0.5,
        'j2': -2.8,
        'j3': 4.2,  # Out of range
        'j4': -1.5,
        'j5': 3.14159,  # At boundary
        'j6': 1.2
    }
    
    print_joint_summary(example_joints, "Original Joint Values")
    
    normalized_joints, warnings = validate_joint_values(example_joints)
    
    if warnings:
        print(f"\n⚠️  Normalization Applied:")
        for warning in warnings:
            print(f"  • {warning}")
    
    print_joint_summary(normalized_joints, "Normalized Joint Values")
    
    print(f"\nValid range: [-π, π] = [{-math.pi:.6f}, {math.pi:.6f}]")
