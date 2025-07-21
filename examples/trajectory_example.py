#!/usr/bin/env python3
"""
Simple example demonstrating JointTrajectory wrapper usage
"""

import sys
from pathlib import Path

# Add utilities directory to path for trajectory_planner import
sys.path.append(str(Path(__file__).parent.parent / "utilities"))

from trajectory_planner import JointTrajectoryPlanner
import numpy as np

def simple_trajectory_example():
    """Simple example showing basic usage of the trajectory planner."""
    
    print("🚀 Simple Joint Trajectory Example")
    print("=" * 50)
    
    # Create planner
    planner = JointTrajectoryPlanner()
    
    # Define start and end positions (6 joints for ALOHA-Lite arm)
    start_joints = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]      # Home position
    end_joints = [0.5, -1.0, 1.0, -1.0, 0.5, 0.3]           # Target position
    
    print(f"\n📍 Start position: {[f'{x:.3f}' for x in start_joints]}")
    print(f"🎯 End position:   {[f'{x:.3f}' for x in end_joints]}")
    
    # Generate trajectory
    trajectory, timestamps = planner.plan_trajectory(
        initial_joints=start_joints,
        final_joints=end_joints,
        duration=3.0,           # 3 seconds
        num_waypoints=20,       # 20 waypoints
        method=5                # Quintic time scaling
    )
    
    print(f"\n📊 Generated trajectory:")
    print(f"   Shape: {trajectory.shape}")
    print(f"   Duration: {timestamps[-1]:.1f} seconds")
    print(f"   Time step: {timestamps[1] - timestamps[0]:.3f} seconds")
    
    # Show some waypoints
    print(f"\n📋 Sample waypoints:")
    for i in [0, 5, 10, 15, 19]:  # Show 5 waypoints
        waypoint = trajectory[i]
        time = timestamps[i]
        print(f"   t={time:.2f}s: [{', '.join(f'{x:.3f}' for x in waypoint)}]")
    
    # Verify trajectory starts and ends correctly
    start_error = np.linalg.norm(trajectory[0] - np.array(start_joints))
    end_error = np.linalg.norm(trajectory[-1] - np.array(end_joints))
    
    print(f"\n✅ Trajectory validation:")
    print(f"   Start error: {start_error:.6f} rad")
    print(f"   End error: {end_error:.6f} rad")
    
    return trajectory, timestamps

def safe_trajectory_example():
    """Example using automatic duration calculation based on velocity limits."""
    
    print("\n" + "=" * 50)
    print("🛡️ Safe Trajectory Example")
    print("=" * 50)
    
    planner = JointTrajectoryPlanner()
    
    # Large movement that needs careful velocity control
    start_joints = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]
    end_joints = [1.0, 0.5, 0.0, -2.5, 1.5, -0.8]  # Big movement
    
    # Generate safe trajectory
    trajectory, timestamps = planner.plan_safe_trajectory(
        initial_joints=start_joints,
        final_joints=end_joints,
        max_joint_velocity=0.4,  # 0.4 rad/s max velocity
        num_waypoints=40
    )
    
    # Analyze velocity profile
    velocities = []
    for i in range(1, len(trajectory)):
        dt = timestamps[i] - timestamps[i-1]
        joint_velocities = (trajectory[i] - trajectory[i-1]) / dt
        max_velocity = np.max(np.abs(joint_velocities))
        velocities.append(max_velocity)
    
    max_actual_velocity = max(velocities)
    print(f"\n📊 Velocity analysis:")
    print(f"   Max actual velocity: {max_actual_velocity:.3f} rad/s")
    print(f"   Velocity limit: 0.4 rad/s")
    print(f"   ✅ {'Within limits' if max_actual_velocity <= 0.41 else 'EXCEEDED LIMITS'}")
    
    return trajectory, timestamps

if __name__ == "__main__":
    # Run examples
    traj1, times1 = simple_trajectory_example()
    traj2, times2 = safe_trajectory_example()
    
    print(f"\n🎉 Examples completed!")
    print(f"💡 Use trajectory_executor.py to execute these on real robots")
