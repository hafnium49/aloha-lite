# Joint Trajectory Planner for ALOHA-Lite

This directory contains a comprehensive wrapper around the ModernRobotics `JointTrajectory` function for generating smooth robot arm trajectories.

## Files

### `trajectory_planner.py`
Core wrapper for ModernRobotics `JointTrajectory` function:
- **`JointTrajectoryPlanner`** class with easy-to-use interface
- **`plan_trajectory()`** - Generate trajectory between initial and final joint configurations
- **`plan_safe_trajectory()`** - Automatic duration calculation based on velocity limits
- Proper velocity limit enforcement (accounts for quintic time scaling peak velocity = 1.875x average)

### `trajectory_executor.py`
Integration with ALOHA-Lite robot control system:
- **`TrajectoryExecutor`** class combining trajectory planning with robot execution
- **`execute_smooth_trajectory()`** - Execute trajectory on real robot with timing control
- **`execute_trajectory_from_config()`** - Load JSON config and execute smooth trajectory
- Command-line interface for easy usage

### `trajectory_example.py`
Simple examples demonstrating usage:
- Basic trajectory generation
- Velocity-limited safe trajectory planning
- Trajectory validation and analysis

## Usage Examples

### Basic Trajectory Planning
```python
from trajectory_planner import JointTrajectoryPlanner

planner = JointTrajectoryPlanner()

# Define start and end positions (6 joints)
start = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]  # Home position
end = [0.5, -1.0, 1.0, -1.0, 0.5, 0.3]       # Target position

# Generate smooth trajectory
trajectory, timestamps = planner.plan_trajectory(
    initial_joints=start,
    final_joints=end,
    duration=3.0,        # 3 seconds
    num_waypoints=50,    # 50 waypoints
    method=5             # Quintic time scaling
)

# trajectory is a (50 x 6) numpy array
# timestamps is a list of 50 time values
```

### Safe Trajectory with Velocity Limits
```python
# Automatic duration calculation based on velocity limits
trajectory, timestamps = planner.plan_safe_trajectory(
    initial_joints=start,
    final_joints=end,
    max_joint_velocity=0.3,  # 0.3 rad/s max velocity
    num_waypoints=40
)
```

### Robot Execution
```bash
# Execute configuration with smooth trajectory
python3 trajectory_executor.py --config left_arm_standoff_with_beaker

# Move specific robot to joint target
python3 trajectory_executor.py --target 0.0,-1.57,1.57,-1.57,0.0,0.0 --robot-id 2

# Custom trajectory parameters
python3 trajectory_executor.py --config beaker_ready --duration 5.0 --waypoints 50
python3 trajectory_executor.py --target 0.5,0.0,1.0,-1.0,0.5,0.3 --max-velocity 0.2
```

### Integration with Execute Rules
```python
from trajectory_executor import TrajectoryExecutor

executor = TrajectoryExecutor()

# Execute smooth trajectory to existing configuration
success = executor.execute_trajectory_from_config(
    "left_arm_standoff_with_beaker",
    duration=4.0,
    num_waypoints=40
)

# Direct joint target execution
target_joints = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]
success = executor.execute_smooth_trajectory(
    robot_id=2,
    target_joints=target_joints,
    max_velocity=0.3
)
```

## Key Features

### Time Scaling Methods
- **Method 3**: Cubic time scaling (zero velocity at start/end)
- **Method 5**: Quintic time scaling (zero velocity and acceleration at start/end) - **Recommended**

### Velocity Control
- Automatic velocity limit enforcement
- Accurate calculation: peak velocity = 1.875 × average velocity for quintic scaling
- Safe trajectory duration: `1.875 × max_displacement / max_velocity`

### Robot Integration
- Compatible with existing `execute_rules.py` framework
- Supports both single-arm and dual-arm movements
- Real-time trajectory execution with timing control
- Automatic current position reading for seamless transitions

### Error Handling
- Input validation (6 joints required)
- Trajectory validation (start/end position accuracy)
- Robot communication error handling
- Graceful degradation on failures

## Mathematical Background

The wrapper uses ModernRobotics library functions:
- **`JointTrajectory(theta_start, theta_end, Tf, N, method)`** - Core trajectory generation
- **`QuinticTimeScaling(Tf, t)`** - Smooth time parameterization with continuous acceleration
- **`CubicTimeScaling(Tf, t)`** - Simpler time parameterization

For quintic time scaling: `s(t) = 10τ³ - 15τ⁴ + 6τ⁵` where `τ = t/Tf`

Peak velocity occurs at `τ ≈ 0.5` with magnitude `1.875 × (total_displacement / total_time)`

## Dependencies

- `numpy` - Numerical computations
- `requests` - Robot communication (via execute_rules.py)
- `modern_robotics` - Trajectory generation

### Installing ModernRobotics

```bash
pip install modern_robotics
```

This installs the official ModernRobotics package from PyPI.

## Robot IDs
- **Robot ID 2**: Right arm (5A68009540)  
- **Robot ID 3**: Left arm (5A68011258)

Use these IDs when executing trajectories on specific arms.
