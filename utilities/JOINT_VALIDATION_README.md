# Joint Validation Tools

This directory contains Python tools for validating and correcting robot joint values to ensure they are within the valid range of [-π, π] radians.

## Tools Overview

### 1. `check_joint_limits.py` - Main Configuration Checker
A comprehensive tool for checking and fixing joint values in robot configuration files.

**Features:**
- Scans all configurations in `robot_configurations.json`
- Identifies joint values outside [-π, π] range
- Automatically corrects values by adding/subtracting 2π
- Updates usage examples (phosphobot_api and python_example)
- Creates backup files before making changes
- Smart path detection (works from project root or utilities directory)

**Usage:**
```bash
# From the utilities directory:
cd utilities
python3 check_joint_limits.py --check-only
python3 check_joint_limits.py --fix

# From the project root:
python3 utilities/check_joint_limits.py --check-only
python3 utilities/check_joint_limits.py --fix

# Use custom input/output files:
python3 check_joint_limits.py --input custom_config.json --output fixed_config.json --fix

# The script automatically detects the correct path to robot_configurations.json
```

### 2. `joint_validator.py` - Utility Module
A lightweight utility module that can be imported into other scripts.

**Features:**
- `normalize_angle(angle)` - Normalize single angle to [-π, π]
- `validate_joint_values(joints)` - Validate dictionary of joint values
- `check_robot_configuration(config)` - Check full robot configuration
- `print_joint_summary(joints)` - Display formatted joint summary

**Usage:**
```python
from joint_validator import validate_joint_values, normalize_angle

# Normalize single angle
corrected_angle = normalize_angle(4.5)  # Returns -1.783185

# Validate joint dictionary
joints = {'j1': 0.5, 'j2': 4.2, 'j3': -1.5}
normalized_joints, warnings = validate_joint_values(joints)
```

### 3. `verify_corrections.py` - Verification Tool
Verifies that joint corrections were applied correctly.

**Features:**
- Confirms mathematical accuracy of corrections
- Verifies corrected values are in valid range
- Ensures physical angle equivalence

### 4. `example_joint_validation.py` - Usage Examples
Demonstrates how to use the validation tools with practical examples.

## Mathematical Background

Robot joints have physical limits and software typically expects joint values to be within [-π, π] radians:

- **Valid Range**: [-π, π] = [-3.141593, 3.141593] radians
- **Correction Method**: Add or subtract 2π to bring values into range
- **Angle Equivalence**: Angles differing by 2π represent the same physical position

### Examples of Corrections:
- `4.145828` → `-2.137357` (subtract 2π)
- `-4.000000` → `2.283185` (add 2π)
- `3.141593` → `3.141593` (no change, at boundary)

## Configuration Files Affected

The tools work with:
- `../temp_rules/robot_configurations.json` (main config, default path)
- Individual configuration files like `dispensing_*.json`
- Any JSON file with robot configuration structure

## Recent Fixes Applied

During the last run, 3 joint values were corrected:
1. `dispensing_blue_to_beaker.left_arm.j5`: 4.145828 → -2.137357
2. `left_arm_stirer_standoff.left_arm.j5`: 4.649097 → -1.634088  
3. `left_arm_stirring.left_arm.j5`: 4.664440 → -1.618745

## Safety Notes

- **Backup Creation**: Original files are automatically backed up before modification
- **Physical Equivalence**: Corrected values represent the same physical robot position
- **Range Validation**: All tools verify values are within [-π, π] after correction
- **Usage Update**: API usage examples are automatically updated with corrected values

## Integration with Existing Tools

These validation tools integrate with:
- `utilities/joint_reader.py` - For reading current robot positions
- `execute_rules.py` - For applying configurations to robots
- Phosphobot API - Configurations remain compatible with API endpoints

Run the checker after any manual configuration edits or after importing new joint readings to ensure all values are within valid ranges.
