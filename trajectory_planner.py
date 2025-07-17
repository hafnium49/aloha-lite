#!/usr/bin/env python3
"""
Joint Trajectory Wrapper for ALOHA-Lite Robot Arms
Wrapper around ModernRobotics JointTrajectory function for easy waypoint generation
"""

import sys
import os
import numpy as np
from typing import List, Tuple, Optional

# Add ModernRobotics to Python path
mr_path = os.path.join(os.path.dirname(__file__), 'ModernRobotics', 'packages', 'Python')
sys.path.insert(0, mr_path)

try:
    import modern_robotics as mr
except ImportError as e:
    print(f"❌ Failed to import ModernRobotics: {e}")
    print(f"📍 Searched path: {mr_path}")
    print("💡 Make sure ModernRobotics subtree is properly installed")
    raise

class JointTrajectoryPlanner:
    """
    Wrapper for ModernRobotics JointTrajectory function for ALOHA-Lite robot arms.
    
    Provides easy-to-use interface for generating smooth joint trajectories between
    initial and final joint configurations.
    """
    
    def __init__(self):
        """Initialize the trajectory planner."""
        self.joint_names = ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"]
        print("🤖 Joint Trajectory Planner initialized")
        print(f"📐 Using ModernRobotics library for trajectory generation")
    
    def plan_trajectory(self, 
                       initial_joints: List[float], 
                       final_joints: List[float],
                       duration: float = 3.0,
                       num_waypoints: int = 50,
                       method: int = 5) -> Tuple[np.ndarray, List[float]]:
        """
        Generate a smooth joint trajectory between initial and final configurations.
        
        Args:
            initial_joints: Starting joint angles [j1, j2, j3, j4, j5, j6] in radians
            final_joints: Target joint angles [j1, j2, j3, j4, j5, j6] in radians
            duration: Total trajectory time in seconds (default: 3.0)
            num_waypoints: Number of trajectory points including start/end (default: 50)
            method: Time scaling method - 3 for cubic, 5 for quintic (default: 5)
        
        Returns:
            Tuple containing:
            - trajectory: (num_waypoints x 6) numpy array of joint angles
            - timestamps: List of timestamps for each waypoint
        
        Raises:
            ValueError: If joint arrays don't have exactly 6 elements
            
        Example:
            planner = JointTrajectoryPlanner()
            
            # Define start and end configurations
            start = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]  # Home position
            end = [0.5, -1.0, 1.0, -1.0, 0.5, 0.3]      # Target position
            
            # Generate trajectory
            traj, times = planner.plan_trajectory(start, end, duration=4.0, num_waypoints=100)
            
            # Execute trajectory
            for i, waypoint in enumerate(traj):
                print(f"Time {times[i]:.2f}s: {waypoint}")
        """
        
        # Validate inputs
        if len(initial_joints) != 6:
            raise ValueError(f"Initial joints must have 6 elements, got {len(initial_joints)}")
        if len(final_joints) != 6:
            raise ValueError(f"Final joints must have 6 elements, got {len(final_joints)}")
        if duration <= 0:
            raise ValueError(f"Duration must be positive, got {duration}")
        if num_waypoints < 2:
            raise ValueError(f"Number of waypoints must be at least 2, got {num_waypoints}")
        if method not in [3, 5]:
            raise ValueError(f"Method must be 3 (cubic) or 5 (quintic), got {method}")
        
        # Convert to numpy arrays
        theta_start = np.array(initial_joints)
        theta_end = np.array(final_joints)
        
        print(f"🎯 Planning trajectory:")
        print(f"   ⏱️  Duration: {duration:.1f} seconds")
        print(f"   📍 Waypoints: {num_waypoints}")
        print(f"   📈 Method: {'Quintic' if method == 5 else 'Cubic'} time scaling")
        print(f"   🎚️  Joint ranges:")
        
        for i, (name, start_val, end_val) in enumerate(zip(self.joint_names, initial_joints, final_joints)):
            diff = end_val - start_val
            diff_deg = np.degrees(diff)
            print(f"      {name}: {start_val:.3f} → {end_val:.3f} rad ({diff_deg:+.1f}°)")
        
        try:
            # Generate trajectory using ModernRobotics
            trajectory = mr.JointTrajectory(theta_start, theta_end, duration, num_waypoints, method)
            
            # Generate timestamps
            timestamps = [i * duration / (num_waypoints - 1) for i in range(num_waypoints)]
            
            # Validate trajectory generation
            if trajectory.shape[0] != num_waypoints or trajectory.shape[1] != 6:
                raise ValueError(f"Unexpected trajectory shape: {trajectory.shape}")
            
            print(f"✅ Trajectory generated successfully!")
            print(f"   📊 Shape: {trajectory.shape} (waypoints x joints)")
            print(f"   ⏱️  Time step: {duration/(num_waypoints-1):.3f} seconds")
            
            return trajectory, timestamps
            
        except Exception as e:
            print(f"❌ Failed to generate trajectory: {e}")
            raise
    
    def plan_safe_trajectory(self,
                           initial_joints: List[float],
                           final_joints: List[float],
                           max_joint_velocity: float = 0.5,
                           num_waypoints: int = 50,
                           method: int = 5) -> Tuple[np.ndarray, List[float]]:
        """
        Generate a trajectory with automatic duration calculation based on velocity limits.
        
        Args:
            initial_joints: Starting joint angles [j1, j2, j3, j4, j5, j6] in radians
            final_joints: Target joint angles [j1, j2, j3, j4, j5, j6] in radians
            max_joint_velocity: Maximum joint velocity in rad/s (default: 0.5)
            num_waypoints: Number of trajectory points (default: 50)
            method: Time scaling method - 3 for cubic, 5 for quintic (default: 5)
        
        Returns:
            Tuple containing trajectory and timestamps
        """
        
        # Calculate maximum joint displacement
        max_displacement = max(abs(f - i) for i, f in zip(initial_joints, final_joints))
        
        # Calculate safe duration based on velocity limit
        # For quintic time scaling, peak velocity = 1.875 * average velocity
        # So required_duration = 1.875 * max_displacement / max_velocity
        safe_duration = 1.875 * max_displacement / max_joint_velocity
        
        # Minimum duration of 1 second for smooth motion
        duration = max(safe_duration, 1.0)
        
        print(f"🛡️  Safe trajectory planning:")
        print(f"   📏 Max displacement: {max_displacement:.3f} rad ({np.degrees(max_displacement):.1f}°)")
        print(f"   🎚️  Max velocity limit: {max_joint_velocity:.3f} rad/s")
        print(f"   ⏱️  Calculated duration: {duration:.1f} seconds")
        
        return self.plan_trajectory(initial_joints, final_joints, duration, num_waypoints, method)
    
    def execute_trajectory_simulation(self, 
                                    trajectory: np.ndarray, 
                                    timestamps: List[float],
                                    show_progress: bool = True) -> None:
        """
        Simulate trajectory execution by printing waypoints.
        
        Args:
            trajectory: Trajectory array from plan_trajectory()
            timestamps: Timestamp array from plan_trajectory()
            show_progress: Whether to show progress information
        """
        
        print(f"\n🎬 Simulating trajectory execution:")
        print(f"   📊 Total waypoints: {len(trajectory)}")
        print(f"   ⏱️  Total duration: {timestamps[-1]:.1f} seconds")
        
        if show_progress:
            # Show key waypoints
            key_indices = [0, len(trajectory)//4, len(trajectory)//2, 3*len(trajectory)//4, -1]
            
            for i in key_indices:
                waypoint = trajectory[i]
                time = timestamps[i]
                progress = (i / (len(trajectory) - 1)) * 100
                
                print(f"\n   📍 Waypoint {i+1} (t={time:.2f}s, {progress:.0f}%):")
                for j, (name, angle) in enumerate(zip(self.joint_names, waypoint)):
                    print(f"      {name}: {angle:.3f} rad ({np.degrees(angle):6.1f}°)")
        else:
            print(f"   🎯 Start: {[f'{x:.3f}' for x in trajectory[0]]}")
            print(f"   🏁 End:   {[f'{x:.3f}' for x in trajectory[-1]]}")

def demo_trajectory_planner():
    """Demonstrate the trajectory planner with example configurations."""
    
    print("🚀 ALOHA-Lite Joint Trajectory Planner Demo")
    print("=" * 60)
    
    # Initialize planner
    planner = JointTrajectoryPlanner()
    
    # Example configurations from ALOHA-Lite
    home_position = [0.0, -1.57, 1.57, -1.57, 0.0, 0.0]
    standoff_position = [0.172, -1.864, 1.459, -1.757, -1.382, 1.58]
    beaker_ready = [0.473, 0.385, 0.947, -1.447, -1.499, 1.837]
    
    print(f"\n📋 Demo configurations:")
    print(f"   🏠 Home: {[f'{x:.3f}' for x in home_position]}")
    print(f"   🛡️  Standoff: {[f'{x:.3f}' for x in standoff_position]}")
    print(f"   🥤 Beaker Ready: {[f'{x:.3f}' for x in beaker_ready]}")
    
    # Demo 1: Home to Standoff
    print(f"\n" + "="*60)
    print(f"📍 Demo 1: Home → Standoff")
    print(f"="*60)
    
    traj1, times1 = planner.plan_trajectory(
        home_position, 
        standoff_position,
        duration=3.0,
        num_waypoints=20,
        method=5
    )
    planner.execute_trajectory_simulation(traj1, times1, show_progress=False)
    
    # Demo 2: Safe trajectory to beaker position
    print(f"\n" + "="*60)
    print(f"📍 Demo 2: Standoff → Beaker Ready (Safe)")
    print(f"="*60)
    
    traj2, times2 = planner.plan_safe_trajectory(
        standoff_position,
        beaker_ready,
        max_joint_velocity=0.3,
        num_waypoints=30
    )
    planner.execute_trajectory_simulation(traj2, times2, show_progress=False)
    
    print(f"\n✅ Demo completed successfully!")
    print(f"💡 Use these trajectories with execute_rules.py for smooth robot motion")

if __name__ == "__main__":
    demo_trajectory_planner()
