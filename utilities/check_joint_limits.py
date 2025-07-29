#!/usr/bin/env python3
"""
Joint Value Range Checker and Corrector

This script checks all joint values in robot configurations to ensure they are
within the valid range of [-π, π]. If a joint value is outside this range,
it adds or subtracts 2π to bring it within the valid range.

Usage:
    python check_joint_limits.py [--input CONFIG_FILE] [--output OUTPUT_FILE] [--fix]
"""

import json
import math
import argparse
import os
from typing import Dict, Any, List, Tuple

def normalize_joint_value(value: float) -> Tuple[float, bool]:
    """
    Normalize a joint value to be within [-π, π] range.
    
    Args:
        value: The joint value in radians
        
    Returns:
        Tuple of (normalized_value, was_modified)
    """
    original_value = value
    
    # Normalize to [-π, π] range
    while value > math.pi:
        value -= 2 * math.pi
    while value < -math.pi:
        value += 2 * math.pi
    
    was_modified = abs(original_value - value) > 1e-6
    return value, was_modified

def check_configuration(config: Dict[str, Any], config_name: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    Check and optionally fix joint values in a single configuration.
    
    Args:
        config: Configuration dictionary
        config_name: Name of the configuration
        
    Returns:
        Tuple of (updated_config, list_of_issues)
    """
    issues = []
    updated_config = json.loads(json.dumps(config))  # Deep copy
    
    if 'configuration' not in config:
        return updated_config, issues
    
    configuration = updated_config['configuration']
    
    # Check both left and right arms
    for arm_name in ['left_arm', 'right_arm']:
        if arm_name not in configuration:
            continue
            
        arm_config = configuration[arm_name]
        if 'joints' not in arm_config:
            continue
            
        joints = arm_config['joints']
        
        # Check each joint (j1 to j6)
        for joint_name in ['j1', 'j2', 'j3', 'j4', 'j5', 'j6']:
            if joint_name not in joints:
                continue
                
            original_value = joints[joint_name]
            normalized_value, was_modified = normalize_joint_value(original_value)
            
            if was_modified:
                issue = f"{config_name}.{arm_name}.{joint_name}: {original_value:.6f} -> {normalized_value:.6f}"
                issues.append(issue)
                joints[joint_name] = normalized_value
            
            # Also check if value is exactly at the boundary
            if abs(abs(original_value) - math.pi) < 1e-6:
                boundary_issue = f"{config_name}.{arm_name}.{joint_name}: At boundary ±π ({original_value:.6f})"
                issues.append(boundary_issue)
    
    # Update usage sections if joints were modified
    if issues and 'usage' in updated_config:
        usage = updated_config['usage']
        
        # Update phosphobot_api usage
        if 'phosphobot_api' in usage:
            for arm_name in ['left_arm', 'right_arm']:
                if arm_name in usage['phosphobot_api'] and arm_name in configuration:
                    arm_joints = configuration[arm_name].get('joints', {})
                    if arm_joints:
                        joint_values = [
                            arm_joints.get(f'j{i}', 0.0) for i in range(1, 7)
                        ]
                        joint_array_str = str(joint_values).replace("'", "")
                        
                        # Check if it's using robot ID format or standard format
                        current_usage = usage['phosphobot_api'][arm_name]
                        if '/robot/' in current_usage:
                            # Extract robot ID from current usage
                            robot_id = current_usage.split('/robot/')[1].split('/')[0]
                            usage['phosphobot_api'][arm_name] = f"POST /robot/{robot_id}/joints/write with body: {joint_array_str}"
                        else:
                            usage['phosphobot_api'][arm_name] = f"POST /joints/write with body: {joint_array_str}"
        
        # Update python_example usage
        if 'python_example' in usage and 'code' in usage['python_example']:
            code_lines = []
            for arm_name in ['left_arm', 'right_arm']:
                if arm_name in configuration:
                    arm_joints = configuration[arm_name].get('joints', {})
                    if arm_joints:
                        joint_values = [
                            arm_joints.get(f'j{i}', 0.0) for i in range(1, 7)
                        ]
                        joint_array_str = str(joint_values).replace("'", "")
                        code_lines.append(f"{arm_name}.move_j({joint_array_str})")
            
            if code_lines:
                usage['python_example']['code'] = '\n'.join(code_lines)
    
    return updated_config, issues

def main():
    # Detect the correct path to robot_configurations.json
    import os
    
    # Get the current working directory and script location
    cwd = os.getcwd()
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Try different possible paths for the config file
    possible_paths = [
        'temp_rules/robot_configurations.json',  # From project root
        '../temp_rules/robot_configurations.json',  # From utilities directory
        os.path.join(os.path.dirname(script_dir), 'temp_rules', 'robot_configurations.json')  # Absolute path
    ]
    
    default_config_path = None
    for path in possible_paths:
        if os.path.exists(path):
            default_config_path = path
            break
    
    # Fallback to relative path from project root if none found
    if default_config_path is None:
        default_config_path = 'temp_rules/robot_configurations.json'
    
    parser = argparse.ArgumentParser(description='Check and fix joint values in robot configurations')
    parser.add_argument('--input', '-i', 
                      default=default_config_path,
                      help='Input configuration file path')
    parser.add_argument('--output', '-o',
                      help='Output file path (if not specified, will use input file with _fixed suffix)')
    parser.add_argument('--fix', action='store_true',
                      help='Fix the joint values and save to output file')
    parser.add_argument('--check-only', action='store_true',
                      help='Only check values without fixing (default behavior)')
    
    args = parser.parse_args()
    
    # Load configuration file
    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.input}' not found.")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.input}': {e}")
        return 1
    
    print(f"🔍 Checking joint values in: {args.input}")
    print(f"📏 Valid range: [-π, π] = [{-math.pi:.6f}, {math.pi:.6f}]")
    print("-" * 80)
    
    all_issues = []
    updated_data = json.loads(json.dumps(data))  # Deep copy
    
    # Process configurations
    if 'configurations' in data:
        configurations = updated_data['configurations']
        
        for config_name, config in configurations.items():
            updated_config, issues = check_configuration(config, config_name)
            configurations[config_name] = updated_config
            all_issues.extend(issues)
    
    # Display results
    if all_issues:
        print(f"❌ Found {len(all_issues)} joint values outside valid range:")
        print()
        for issue in all_issues:
            print(f"  • {issue}")
        print()
        
        if args.fix:
            # Determine output file
            if args.output:
                output_file = args.output
            else:
                base_name = os.path.splitext(args.input)[0]
                output_file = f"{base_name}_fixed.json"
            
            # Save fixed configuration
            try:
                with open(output_file, 'w') as f:
                    json.dump(updated_data, f, indent=2)
                print(f"✅ Fixed joint values saved to: {output_file}")
                
                # Also update the original file if requested
                if args.output is None:
                    backup_file = f"{args.input}.backup"
                    os.rename(args.input, backup_file)
                    os.rename(output_file, args.input)
                    print(f"📁 Original file backed up to: {backup_file}")
                    print(f"📁 Updated original file: {args.input}")
                    
            except Exception as e:
                print(f"❌ Error saving fixed configuration: {e}")
                return 1
        else:
            print("💡 Use --fix flag to automatically correct these values.")
            
    else:
        print("✅ All joint values are within the valid range [-π, π].")
    
    print("-" * 80)
    print(f"📊 Summary:")
    print(f"  • Total configurations checked: {len(data.get('configurations', {}))}")
    print(f"  • Issues found: {len(all_issues)}")
    print(f"  • Range: [{-math.pi:.6f}, {math.pi:.6f}] radians")
    
    return 0

if __name__ == "__main__":
    exit(main())
