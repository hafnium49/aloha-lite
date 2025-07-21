#!/usr/bin/env python3
"""
Trajectory Execution Integration for ALOHA-Lite Robot Arms
Combines trajectory_planner.py with execute_rules.py for smooth robot motion
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

# Import our trajectory planner
from trajectory_planner import JointTrajectoryPlanner

# Import execute_rules functionality
from execute_rules import PhosphobotJointController

class TrajectoryExecutor:
    """
    Executes smooth trajectories on ALOHA-Lite robot arms using ModernRobotics trajectory planning.
    """
    
    def __init__(self, server_url: str = "http://localhost:80"):
        """Initialize trajectory executor with robot controller and trajectory planner."""
        self.controller = PhosphobotJointController(server_url)
        self.planner = JointTrajectoryPlanner()
        print("🎬 Trajectory Executor initialized")
    
    def execute_smooth_trajectory(self,
                                robot_id: int,
                                target_joints: List[float],
                                duration: Optional[float] = None,
                                max_velocity: float = 0.3,
                                num_waypoints: int = 30,
                                method: int = 5,
                                pause_between_waypoints: float = 0.1) -> bool:
        """
        Execute a smooth trajectory from current position to target position.
        
        Args:
            robot_id: Robot arm ID (2 for right arm, 3 for left arm)
            target_joints: Target joint angles [j1, j2, j3, j4, j5, j6] in radians
            duration: Total trajectory time (auto-calculated if None)
            max_velocity: Maximum joint velocity in rad/s for auto duration
            num_waypoints: Number of trajectory waypoints
            method: Time scaling method (3=cubic, 5=quintic)
            pause_between_waypoints: Sleep time between waypoints in seconds
        
        Returns:
            True if successful, False otherwise
        """
        
        print(f"\n🎯 Executing smooth trajectory for robot {robot_id}")
        print("=" * 60)
        
        try:
            # Get current joint positions
            print(f"📖 Reading current position...")
            current_joints = self.controller.get_current_joint_angles(robot_id)
            if current_joints is None:
                print(f"❌ Failed to read current joint positions")
                return False
            
            print(f"📍 Current: {[f'{j:.3f}' for j in current_joints]}")
            print(f"🎯 Target:  {[f'{j:.3f}' for j in target_joints]}")
            
            # Plan trajectory
            if duration is None:
                trajectory, timestamps = self.planner.plan_safe_trajectory(
                    current_joints, target_joints, max_velocity, num_waypoints, method
                )
            else:
                trajectory, timestamps = self.planner.plan_trajectory(
                    current_joints, target_joints, duration, num_waypoints, method
                )
            
            # Execute trajectory
            print(f"\n🎬 Executing trajectory...")
            start_time = time.time()
            
            for i, (waypoint, target_time) in enumerate(zip(trajectory, timestamps)):
                # Calculate sleep time to maintain timing
                elapsed_time = time.time() - start_time
                sleep_time = max(0, target_time - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # Send waypoint to robot
                self.controller.write_joint_positions(robot_id, waypoint.tolist())
                
                # Brief pause for robot response (optional)
                if pause_between_waypoints > 0:
                    time.sleep(pause_between_waypoints)
                
                # Progress update
                if i % (num_waypoints // 5) == 0 or i == num_waypoints - 1:
                    progress = (i + 1) / num_waypoints * 100
                    actual_time = time.time() - start_time
                    print(f"   📊 Progress: {progress:3.0f}% (waypoint {i+1}/{num_waypoints}, t={actual_time:.1f}s)")
            
            # Verify final position
            print(f"\n📖 Verifying final position...")
            final_joints = self.controller.get_current_joint_angles(robot_id)
            if final_joints:
                max_error = max(abs(final - target) for final, target in zip(final_joints, target_joints))
                max_error_deg = np.degrees(max_error)
                print(f"✅ Trajectory completed!")
                print(f"   📏 Max error: {max_error:.4f} rad ({max_error_deg:.2f}°)")
                return True
            
        except Exception as e:
            print(f"❌ Trajectory execution failed: {e}")
            return False
        
        return False
    
    def execute_trajectory_from_config(self,
                                     config_name: str,
                                     left_arm_id: int = 3,
                                     right_arm_id: int = 2,
                                     **trajectory_kwargs) -> bool:
        """
        Load a configuration and execute smooth trajectories to reach it.
        
        Args:
            config_name: Configuration name to load
            left_arm_id: Left arm robot ID
            right_arm_id: Right arm robot ID
            **trajectory_kwargs: Additional arguments for trajectory execution
        
        Returns:
            True if successful, False otherwise
        """
        
        print(f"\n🤖 Executing smooth trajectory to configuration: {config_name}")
        print("=" * 70)
        
        try:
            # Import configuration loading from execute_rules
            from execute_rules import load_configuration, prepare_arm_configuration
            
            # Load configuration
            config = load_configuration(config_name)
            config_data = config['configuration']
            
            # Check which arms are configured
            has_left_arm = 'left_arm' in config_data and config_data['left_arm'] is not None
            has_right_arm = 'right_arm' in config_data and config_data['right_arm'] is not None
            
            print(f"📋 Configuration: {config.get('name', 'Unknown')}")
            print(f"📝 Description: {config.get('description', 'No description')}")
            
            success = True
            
            # Execute trajectories for configured arms
            if has_left_arm:
                print(f"\n🦾 Planning left arm trajectory...")
                current_left_joints = self.controller.get_current_joint_angles(left_arm_id)
                if current_left_joints:
                    left_joints = prepare_arm_configuration(
                        config_data['left_arm'], current_left_joints, "left_arm"
                    )
                    if left_joints:
                        success &= self.execute_smooth_trajectory(
                            left_arm_id, left_joints, **trajectory_kwargs
                        )
            
            if has_right_arm:
                print(f"\n🦾 Planning right arm trajectory...")
                current_right_joints = self.controller.get_current_joint_angles(right_arm_id)
                if current_right_joints:
                    right_joints = prepare_arm_configuration(
                        config_data['right_arm'], current_right_joints, "right_arm"
                    )
                    if right_joints:
                        success &= self.execute_smooth_trajectory(
                            right_arm_id, right_joints, **trajectory_kwargs
                        )
            
            return success
            
        except Exception as e:
            print(f"❌ Configuration execution failed: {e}")
            return False
    
    def close(self):
        """Clean up resources."""
        self.controller.close()

def main():
    """Main function with command-line interface."""
    
    parser = argparse.ArgumentParser(description="Execute smooth robot trajectories using ModernRobotics")
    parser.add_argument("--config", "-c", type=str,
                       help="Configuration name to execute with smooth trajectory")
    parser.add_argument("--target", "-t", type=str,
                       help="Target joint angles as comma-separated values (j1,j2,j3,j4,j5,j6)")
    parser.add_argument("--robot-id", type=int, default=2,
                       help="Robot ID for direct joint target (default: 2)")
    parser.add_argument("--duration", "-d", type=float,
                       help="Trajectory duration in seconds (auto-calculated if not specified)")
    parser.add_argument("--max-velocity", type=float, default=0.3,
                       help="Maximum joint velocity for auto duration calculation (default: 0.3 rad/s)")
    parser.add_argument("--waypoints", type=int, default=30,
                       help="Number of trajectory waypoints (default: 30)")
    parser.add_argument("--method", type=int, choices=[3, 5], default=5,
                       help="Time scaling method: 3=cubic, 5=quintic (default: 5)")
    parser.add_argument("--pause", type=float, default=0.1,
                       help="Pause between waypoints in seconds (default: 0.1)")
    parser.add_argument("--left-arm-id", type=int, default=3,
                       help="Left arm robot ID (default: 3)")
    parser.add_argument("--right-arm-id", type=int, default=2,
                       help="Right arm robot ID (default: 2)")
    
    args = parser.parse_args()
    
    # Initialize executor
    executor = TrajectoryExecutor()
    
    try:
        if args.config:
            # Execute configuration with smooth trajectory
            trajectory_kwargs = {
                'duration': args.duration,
                'max_velocity': args.max_velocity,
                'num_waypoints': args.waypoints,
                'method': args.method,
                'pause_between_waypoints': args.pause
            }
            
            success = executor.execute_trajectory_from_config(
                args.config,
                left_arm_id=args.left_arm_id,
                right_arm_id=args.right_arm_id,
                **trajectory_kwargs
            )
            
            if success:
                print(f"\n🎉 Smooth trajectory to '{args.config}' completed successfully!")
            else:
                print(f"\n❌ Failed to execute smooth trajectory to '{args.config}'")
                sys.exit(1)
                
        elif args.target:
            # Execute direct joint target
            try:
                target_joints = [float(x.strip()) for x in args.target.split(',')]
                if len(target_joints) != 6:
                    raise ValueError(f"Expected 6 joint values, got {len(target_joints)}")
                
                success = executor.execute_smooth_trajectory(
                    args.robot_id,
                    target_joints,
                    duration=args.duration,
                    max_velocity=args.max_velocity,
                    num_waypoints=args.waypoints,
                    method=args.method,
                    pause_between_waypoints=args.pause
                )
                
                if success:
                    print(f"\n🎉 Smooth trajectory completed successfully!")
                else:
                    print(f"\n❌ Failed to execute smooth trajectory")
                    sys.exit(1)
                    
            except ValueError as e:
                print(f"❌ Invalid target joints: {e}")
                print("   Format: --target j1,j2,j3,j4,j5,j6")
                print("   Example: --target 0.0,-1.57,1.57,-1.57,0.0,0.0")
                sys.exit(1)
        else:
            # Show help and examples
            parser.print_help()
            print(f"\nExamples:")
            print(f"  # Execute configuration with smooth trajectory:")
            print(f"  python3 trajectory_executor.py --config left_arm_standoff_with_beaker")
            print(f"  ")
            print(f"  # Move specific robot to joint target:")
            print(f"  python3 trajectory_executor.py --target 0.0,-1.57,1.57,-1.57,0.0,0.0 --robot-id 2")
            print(f"  ")
            print(f"  # Custom trajectory parameters:")
            print(f"  python3 trajectory_executor.py --config beaker_ready --duration 5.0 --waypoints 50")
            print(f"  python3 trajectory_executor.py --target 0.5,0.0,1.0,-1.0,0.5,0.3 --max-velocity 0.2")
            
    finally:
        executor.close()

if __name__ == "__main__":
    main()
