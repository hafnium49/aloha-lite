# Joint Reader Usage Guide

This guide explains how to use the joint reader functionality to read joint values from robot arms.

## Files Created

1. **`joint_reader.py`** - Main joint reader script with command-line interface
2. **`joint_reader_examples.py`** - Example usage demonstrations
3. **`JOINT_READER_GUIDE.md`** - This usage guide

## Quick Start

### Command Line Usage

```bash
# Read left arm joint values
python joint_reader.py --arm left

# Read right arm joint values  
python joint_reader.py --arm right

# Read both arms
python joint_reader.py --arm both

# Save joint values to a file
python joint_reader.py --arm left --save my_joints.json

# Use custom server URL
python joint_reader.py --arm left --server http://192.168.1.100:80
```

### Python Code Usage

```python
from joint_reader import RobotJointReader

# Create reader
reader = RobotJointReader(
    server_url="http://localhost:80",
    left_arm_id=0,
    right_arm_id=2
)

# Initialize
reader.initialize()

# Read left arm
joint_data = reader.read_joint_values("left")

if joint_data:
    # Access individual joints
    j1 = joint_data['joints']['j1']
    j6 = joint_data['joints']['j6']  # Gripper
    
    # Get all joints as list
    all_joints = joint_data['raw_angles']
    
    print(f"J1: {j1:.6f}, J6: {j6:.6f}")
    print(f"All joints: {all_joints}")
```

## Key Features

### 1. Single Arm Reading
- Read joint values from left or right arm
- Returns structured data with joint names and values
- Handles errors gracefully

### 2. Dual Arm Reading
- Read both arms simultaneously
- Compare joint positions between arms
- Useful for coordination tasks

### 3. Data Export
- Save joint values to JSON files
- Includes metadata and timestamps
- Compatible with configuration file formats

### 4. Continuous Monitoring
- Read joint values repeatedly
- Monitor joint changes over time
- Useful for debugging and analysis

## Data Structure

The joint reader returns data in this format:

```json
{
  "arm": "left",
  "robot_id": 0,
  "timestamp": 1721318400.123,
  "joints": {
    "j1": 0.101267,
    "j2": -0.383589,
    "j3": 0.156504,
    "j4": 0.461841,
    "j5": -2.036090,
    "j6": 0.906804
  },
  "joint_names": ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"],
  "units": "radians",
  "raw_angles": [0.101267, -0.383589, 0.156504, 0.461841, -2.036090, 0.906804]
}
```

## Integration with Sequential Execute

The joint reader uses the same infrastructure as `sequential_execute.py`:

- **Same controller**: Uses `PhosphobotJointController`
- **Same arm IDs**: Left arm (0), Right arm (2)
- **Same server URL**: Default `http://localhost:80`
- **Same error handling**: Consistent error messages and recovery

## Common Use Cases

### 1. Capture Current Position
```python
# Read current position for creating new configurations
joint_data = reader.read_joint_values("left")
if joint_data:
    # Use joint_data to create new configuration files
    pass
```

### 2. Verify Robot State
```python
# Check if robot is in expected position
joint_data = reader.read_joint_values("left")
if joint_data:
    current_j6 = joint_data['joints']['j6']
    if abs(current_j6 - 0.906804) < 0.01:
        print("Gripper is in correct position")
```

### 3. Monitor Joint Changes
```python
# Monitor joint values during operation
for i in range(10):
    joint_data = reader.read_joint_values("left")
    if joint_data:
        j6 = joint_data['joints']['j6']
        print(f"Reading {i+1}: J6 = {j6:.6f}")
    time.sleep(1)
```

## Error Handling

The joint reader handles common errors:

- **Connection errors**: Server unavailable
- **Invalid arm names**: Only "left" and "right" supported
- **Robot communication errors**: Arm not responding
- **Invalid robot IDs**: Non-existent robot IDs

## Command Line Options

```bash
python joint_reader.py --help

options:
  --arm {left,right,both}    Specify which arm to read (default: left)
  --server SERVER           Phosphobot server URL (default: http://localhost:80)
  --save FILENAME           Save joint values to specified JSON file
  --left-id ID              Left arm robot ID (default: 0)
  --right-id ID             Right arm robot ID (default: 2)
```

## Examples

Run the examples to see the joint reader in action:

```bash
python joint_reader_examples.py
```

This will demonstrate:
1. Reading single arm joint values
2. Reading both arms simultaneously
3. Saving joint values to files
4. Continuous monitoring

## Integration Notes

- Compatible with existing `execute_rules.py` infrastructure
- Uses same robot arm IDs as `sequential_execute.py`
- Output format compatible with configuration files
- Can be imported as a module or used as a command-line tool
