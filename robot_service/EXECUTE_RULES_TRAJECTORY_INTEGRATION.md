# Enhanced execute_rules.py with Trajectory Planning Integration

## Overview

`execute_rules.py` has been enhanced with integrated smooth trajectory planning capabilities using the ModernRobotics library. The system automatically reads current joint positions from the phosphobot API and uses them as initial values for trajectory generation.

## Key Features

### 🎬 **Smooth Trajectory Mode (Default)**
- Automatically reads current joint positions from phosphobot API
- Generates smooth trajectories using ModernRobotics JointTrajectory function
- Velocity-controlled movement with quintic time scaling
- Real-time trajectory execution with precise timing

### 📐 **Step-Based Mode (Traditional)**
- Direct joint position commands (original behavior)
- Instant movement to target positions
- Backward compatible with existing workflows

### 🔄 **Automatic Fallback**
- If ModernRobotics is not available, automatically uses step-based mode
- Graceful degradation ensures system always works

## Usage Examples

### Basic Usage (Smooth by Default)
```bash
# Uses smooth trajectory planning automatically
python3 execute_rules.py --config standoff_configuration_stage1
```

### Explicit Mode Selection
```bash
# Force smooth trajectory mode
python3 execute_rules.py --config beaker_ready --smooth

# Force step-based mode (traditional)
python3 execute_rules.py --config beaker_ready --step
```

### Trajectory Customization
```bash
# Custom duration
python3 execute_rules.py --config beaker_ready --duration 5.0

# Slower movement (lower velocity limit)
python3 execute_rules.py --config beaker_ready --max-velocity 0.2

# Higher resolution (more waypoints)
python3 execute_rules.py --config beaker_ready --waypoints 50

# Combined options
python3 execute_rules.py --config beaker_ready --smooth --duration 4.0 --max-velocity 0.25 --waypoints 40
```

## Command Line Arguments

### Trajectory Control
- `--smooth` - Force smooth trajectory planning
- `--step` - Force step-based movement
- `--duration` / `-d` - Trajectory duration in seconds (auto-calculated if not specified)
- `--max-velocity` - Maximum joint velocity in rad/s (default: 0.3)
- `--waypoints` - Number of trajectory waypoints (default: 30)

### Robot Control (Existing)
- `--config` / `-c` - Configuration name to execute
- `--left-arm-id` - Left arm robot ID (default: 3)
- `--right-arm-id` - Right arm robot ID (default: 2)
- `--init` / `--no-init` - Robot initialization control

## Integration Details

### Current Joint Position Reading
The system automatically reads current joint positions from the phosphobot API before planning trajectories:

```python
# Reads current position from robot
current_joints = controller.get_current_joint_angles(robot_id)

# Uses as initial position for trajectory
trajectory = mr.JointTrajectory(current_joints, target_joints, duration, waypoints, method)
```

### Safe Velocity Calculation
For auto-duration mode, the system calculates safe trajectory duration:

```python
# Calculate maximum joint displacement
max_displacement = max(abs(f - i) for i, f in zip(current_joints, target_joints))

# Safe duration accounting for quintic time scaling peak velocity (1.875x average)
safe_duration = 1.875 * max_displacement / max_velocity
duration = max(safe_duration, 1.0)  # Minimum 1 second
```

### Real-Time Execution
Trajectories are executed with precise timing control:

```python
for i, (waypoint, target_time) in enumerate(zip(trajectory, timestamps)):
    # Maintain timing accuracy
    elapsed_time = time.time() - start_time
    sleep_time = max(0, target_time - elapsed_time)
    if sleep_time > 0:
        time.sleep(sleep_time)
    
    # Send waypoint to robot
    controller.write_joint_positions(robot_id, waypoint.tolist())
```

## Benefits

### ✅ **Smooth Motion**
- Eliminates jerky movements
- Reduces mechanical stress on robot joints
- Professional-quality motion profiles

### ✅ **Velocity Control**
- Respects joint velocity limits
- Automatic safe duration calculation
- Prevents overly fast or slow movements

### ✅ **Backwards Compatibility**
- All existing configurations work unchanged
- Step-based mode preserves original behavior
- Automatic fallback if trajectory planning unavailable

### ✅ **Current Position Aware**
- Reads actual robot state before movement
- Trajectories start from true current position
- No assumptions about robot state

### ✅ **Flexible Control**
- Command-line control of all trajectory parameters
- Easy switching between smooth and step modes
- Fine-tuning for specific applications

## Error Handling

The system gracefully handles various error conditions:

- **ModernRobotics not available**: Falls back to step-based mode
- **Robot communication failure**: Reports error and continues
- **Invalid configurations**: Clear error messages
- **Trajectory generation failure**: Falls back to step-based movement

## Dependencies

- `modern_robotics` - For trajectory planning (auto-installed from PyPI)
- `numpy` - For numerical computations
- `requests` - For phosphobot API communication

Install dependencies:
```bash
pip install -r requirements.txt
```

## Migration Guide

### For Existing Users
No changes required! Your existing commands work exactly the same:
```bash
# This still works exactly as before
python3 execute_rules.py --config your_config_name
```

The only difference is that movements will now be smooth by default instead of step-based.

### To Use Old Behavior
If you need the old step-based behavior:
```bash
# Force step-based mode
python3 execute_rules.py --config your_config_name --step
```

## Performance Notes

- **Smooth trajectories**: Slightly slower execution due to many waypoints, but much smoother motion
- **Step-based**: Instant movement, but potentially jerky
- **Memory usage**: Minimal increase for trajectory storage
- **CPU usage**: Light computational load for trajectory generation
