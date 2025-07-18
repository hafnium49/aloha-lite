#!/usr/bin/env python3
"""
ADAPTED from demo2rules.py output
Dataset : Hafnium49/aloha_lite  (episode 1)
SHA‑256 : fc327fe0e0
Using direct phosphobot joint control APIs
Now supports loading configurations from JSON files
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
import requests
import numpy as np
from typing import List, Tuple, Optional

# Import trajectory planning functionality
try:
    import modern_robotics as mr
    TRAJECTORY_AVAILABLE = True
except ImportError:
    print("⚠️  ModernRobotics not available. Install with: pip install modern_robotics")
    TRAJECTORY_AVAILABLE = False

class PhosphobotJointController:
    """Direct joint controller using phosphobot APIs."""
    
    def __init__(self, server_url: str = "http://localhost:80"):
        self.server_url = server_url
        self.session = requests.Session()
        print(f"✅ Initialized phosphobot joint controller")
        print(f"🔗 Server: {server_url}")
    
    def initialize_robot(self, robot_id: int = 0):
        """Initialize robot using the /move/init endpoint."""
        try:
            response = self.session.post(f"{self.server_url}/move/init", json={})
            response.raise_for_status()
            print(f"✅ Robot {robot_id} initialized")
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to initialize robot {robot_id}: {e}")
            return None
    
    def write_joint_positions(self, robot_id: int, angles: list[float], unit: str = "rad"):
        """Write joint positions using the /joints/write API."""
        try:
            payload = {
                "angles": angles,
                "unit": unit
            }
            response = self.session.post(
                f"{self.server_url}/joints/write?robot_id={robot_id}",
                json=payload
            )
            response.raise_for_status()
            print(f"✅ Robot {robot_id} joints set to: {[f'{a:.3f}' for a in angles]} {unit}")
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to set joints for robot {robot_id}: {e}")
            return None
    
    def read_joint_positions(self, robot_id: int, unit: str = "rad"):
        """Read joint positions using the /joints/read API."""
        try:
            payload = {
                "unit": unit
            }
            response = self.session.post(
                f"{self.server_url}/joints/read?robot_id={robot_id}",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            print(f"📖 Robot {robot_id} joints: {[f'{a:.3f}' for a in result.get('angles', [])]}")
            return result
        except requests.RequestException as e:
            print(f"❌ Failed to read joints for robot {robot_id}: {e}")
            return None
    
    def get_current_joint_angles(self, robot_id: int):
        """Get current joint angles as a list."""
        result = self.read_joint_positions(robot_id)
        if result and 'angles' in result:
            return result['angles']
        return None
    
    def execute_smooth_trajectory(self,
                                robot_id: int,
                                target_joints: List[float],
                                duration: Optional[float] = None,
                                max_velocity: float = 0.3,
                                num_waypoints: int = 3,
                                method: int = 5,
                                pause_between_waypoints: float = 0.05) -> bool:
        """
        Execute a smooth trajectory from current position to target position using ModernRobotics.
        
        Args:
            robot_id: Robot arm ID (0 for left arm, 3 for right arm)
            target_joints: Target joint angles [j1, j2, j3, j4, j5, j6] in radians
            duration: Total trajectory time (auto-calculated if None)
            max_velocity: Maximum joint velocity in rad/s for auto duration
            num_waypoints: Number of trajectory waypoints
            method: Time scaling method (3=cubic, 5=quintic)
            pause_between_waypoints: Sleep time between waypoints in seconds
        
        Returns:
            True if successful, False otherwise
        """
        
        if not TRAJECTORY_AVAILABLE:
            print("❌ ModernRobotics not available. Using step-based movement instead.")
            return self.write_joint_positions(robot_id, target_joints) is not None
        
        print(f"\n🎯 Executing smooth trajectory for robot {robot_id}")
        print("=" * 60)
        
        try:
            # Get current joint positions
            print(f"📖 Reading current position...")
            current_joints = self.get_current_joint_angles(robot_id)
            if current_joints is None:
                print(f"❌ Failed to read current joint positions")
                return False
            
            print(f"📍 Current: {[f'{j:.3f}' for j in current_joints]}")
            print(f"🎯 Target:  {[f'{j:.3f}' for j in target_joints]}")
            
            # Plan trajectory
            if duration is None:
                # Calculate safe duration based on velocity limit
                max_displacement = max(abs(f - i) for i, f in zip(current_joints, target_joints))
                # For quintic time scaling, peak velocity = 1.875 * average velocity
                safe_duration = 1.875 * max_displacement / max_velocity
                duration = max(safe_duration, 1.0)  # Minimum 1 second
                
                print(f"🛡️  Auto-calculated duration: {duration:.1f}s (max_vel: {max_velocity:.3f} rad/s)")
            
            # Generate trajectory using ModernRobotics
            theta_start = np.array(current_joints)
            theta_end = np.array(target_joints)
            
            print(f"📈 Generating trajectory...")
            print(f"   ⏱️  Duration: {duration:.1f} seconds")
            print(f"   📍 Waypoints: {num_waypoints}")
            print(f"   📈 Method: {'Quintic' if method == 5 else 'Cubic'} time scaling")
            
            trajectory = mr.JointTrajectory(theta_start, theta_end, duration, num_waypoints, method)
            timestamps = [i * duration / (num_waypoints - 1) for i in range(num_waypoints)]
            
            print(f"✅ Trajectory generated successfully!")
            print(f"   📊 Shape: {trajectory.shape} (waypoints x joints)")
            print(f"   ⏱️  Time step: {duration/(num_waypoints-1):.3f} seconds")
            
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
                self.write_joint_positions(robot_id, waypoint.tolist())
                
                # Brief pause for robot response
                if pause_between_waypoints > 0:
                    time.sleep(pause_between_waypoints)
                
                # Progress update
                progress_interval = max(1, num_waypoints // 5)  # Avoid division by zero
                if i % progress_interval == 0 or i == num_waypoints - 1:
                    progress = (i + 1) / num_waypoints * 100
                    actual_time = time.time() - start_time
                    print(f"   📊 Progress: {progress:3.0f}% (waypoint {i+1}/{num_waypoints}, t={actual_time:.1f}s)")
            
            # Verify final position
            print(f"\n📖 Verifying final position...")
            final_joints = self.get_current_joint_angles(robot_id)
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
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
        print("🔌 Controller disconnected")

def merge_joint_configurations(target_joints: dict, current_joints: list):
    """
    Merge partial joint configuration with current joint positions.
    
    Args:
        target_joints: dict with joint names as keys (j1, j2, etc.) and target angles as values
        current_joints: list of current joint angles [j1, j2, j3, j4, j5, j6]
    
    Returns:
        list: Complete joint configuration with partial updates applied
    """
    # Start with current joint positions
    merged_joints = current_joints.copy() if current_joints else [0.0] * 6
    
    # Ensure we have 6 joints
    while len(merged_joints) < 6:
        merged_joints.append(0.0)
    
    # Update specified joints
    joint_mapping = {'j1': 0, 'j2': 1, 'j3': 2, 'j4': 3, 'j5': 4, 'j6': 5}
    
    for joint_name, target_angle in target_joints.items():
        if joint_name in joint_mapping:
            joint_index = joint_mapping[joint_name]
            merged_joints[joint_index] = target_angle
            print(f"  📝 {joint_name} → {target_angle:.3f} rad")
    
    return merged_joints

def prepare_arm_configuration(arm_config: dict, current_joints: list, arm_name: str):
    """
    Prepare arm configuration, handling partial joint specifications.
    
    Args:
        arm_config: arm configuration from JSON
        current_joints: current joint positions
        arm_name: "left_arm" or "right_arm" for logging
    
    Returns:
        list: Complete joint configuration
    """
    if not arm_config or 'joints' not in arm_config:
        return None
    
    joints_config = arm_config['joints']
    
    # Check if we have a complete configuration (all 6 joints)
    expected_joints = ['j1', 'j2', 'j3', 'j4', 'j5', 'j6']
    missing_joints = [j for j in expected_joints if j not in joints_config]
    
    if not missing_joints:
        # Complete configuration - use as-is
        print(f"  ✅ {arm_name}: Complete configuration (all 6 joints)")
        return list(joints_config.values())
    else:
        # Partial configuration - merge with current positions
        print(f"  🔄 {arm_name}: Partial configuration (missing {missing_joints})")
        print(f"  🔄 Merging with current joint positions...")
        
        if current_joints is None:
            print(f"  ⚠️  Warning: No current joint positions available, using defaults for missing joints")
            current_joints = [0.0] * 6
        
        return merge_joint_configurations(joints_config, current_joints)

def load_configuration(config_name: str, search_dirs: list[str] = None) -> dict:
    """Load configuration from JSON file by name."""
    if search_dirs is None:
        search_dirs = [
            "./temp_rules",
            "./",
            "./aloha-lite-demo2rule",
            "./configs"
        ]
    
    # Try different filename patterns
    possible_filenames = [
        f"{config_name}.json",
        f"{config_name}_config.json",
        f"config_{config_name}.json",
        "robot_configurations.json",
        "configurations.json",
        "configs.json",
        config_name if config_name.endswith('.json') else None
    ]
    possible_filenames = [f for f in possible_filenames if f is not None]
    
    # Search for configurations
    for search_dir in search_dirs:
        search_path = Path(search_dir)
        if not search_path.exists():
            continue
            
        # First try direct filename matches for single-config files
        for filename in possible_filenames:
            config_path = search_path / filename
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    # Check if it's a multi-configuration file
                    if 'configurations' in config_data:
                        if config_name in config_data['configurations']:
                            config = config_data['configurations'][config_name]
                            print(f"✅ Loaded configuration '{config_name}' from: {config_path}")
                            return config
                        continue  # Config name not found in this multi-config file
                    
                    # Check if it's a single configuration file with matching name
                    if config_data.get('name') == config_name:
                        print(f"✅ Loaded configuration by name from: {config_path}")
                        return config_data
                    
                    # If filename matches config_name directly, use it
                    if filename.replace('.json', '') == config_name:
                        print(f"✅ Loaded configuration from: {config_path}")
                        return config_data
                        
                except (json.JSONDecodeError, IOError) as e:
                    print(f"❌ Failed to load {config_path}: {e}")
                    continue
        
        # Search all JSON files for matching 'name' field or multi-config entries
        for json_file in search_path.glob("*.json"):
            if json_file.name in possible_filenames:
                continue  # Already checked above
            try:
                with open(json_file, 'r') as f:
                    config_data = json.load(f)
                
                # Check multi-config structure
                if 'configurations' in config_data and config_name in config_data['configurations']:
                    config = config_data['configurations'][config_name]
                    print(f"✅ Loaded configuration '{config_name}' from: {json_file}")
                    return config
                
                # Check single config by name
                if config_data.get('name') == config_name:
                    print(f"✅ Loaded configuration by name from: {json_file}")
                    return config_data
                    
            except (json.JSONDecodeError, IOError):
                continue
    
    raise FileNotFoundError(f"Configuration '{config_name}' not found in search directories: {search_dirs}")

def execute_configuration_smooth(config_name: str, 
                                skip_init: bool = True, 
                                left_arm_id: int = 0, 
                                right_arm_id: int = 3,
                                use_trajectory: bool = True,
                                trajectory_duration: Optional[float] = None,
                                max_velocity: float = 0.3,
                                num_waypoints: int = 3):
    """Execute a specific configuration using smooth trajectories.
    
    Enhanced to support:
    - Smooth trajectory planning with ModernRobotics
    - Complete and partial joint configurations
    - Single-arm and dual-arm movements  
    - Automatic merging with current joint positions for incomplete configurations
    """
    
    trajectory_status = "🎬 SMOOTH TRAJECTORY" if use_trajectory and TRAJECTORY_AVAILABLE else "📐 STEP-BASED"
    print(f"🤖 Loading and executing configuration: {config_name}")
    print(f"🎯 Execution mode: {trajectory_status}")
    print("=" * 70)
    print(f"🔧 Left arm ID: {left_arm_id} (5A68011258)")
    print(f"🔧 Right arm ID: {right_arm_id} (5A68009540)")
    
    if use_trajectory and TRAJECTORY_AVAILABLE:
        print(f"📊 Trajectory settings:")
        print(f"   ⏱️  Duration: {'Auto' if trajectory_duration is None else f'{trajectory_duration:.1f}s'}")
        print(f"   🎚️  Max velocity: {max_velocity:.3f} rad/s")
        print(f"   📍 Waypoints: {num_waypoints}")
    
    try:
        # Load configuration
        config = load_configuration(config_name)
        
        # Validate configuration structure
        if 'configuration' not in config:
            raise ValueError("Invalid configuration: missing 'configuration' section")
        
        config_data = config['configuration']
        
        # Check which arms are configured
        has_left_arm = 'left_arm' in config_data and config_data['left_arm'] is not None
        has_right_arm = 'right_arm' in config_data and config_data['right_arm'] is not None
        
        if not has_left_arm and not has_right_arm:
            raise ValueError("Invalid configuration: no arm configuration found")
        
        print(f"📋 Configuration: {config.get('name', 'Unknown')}")
        print(f"📝 Description: {config.get('description', 'No description')}")
        print(f"📊 Source: {config.get('source', {}).get('dataset', 'Unknown')}")
        
        # Show which arms will be moved
        if has_left_arm and has_right_arm:
            print("🎯 Mode: Dual-arm movement")
        elif has_left_arm:
            print("🎯 Mode: Left arm only (right arm stays steady)")
        elif has_right_arm:
            print("🎯 Mode: Right arm only (left arm stays steady)")
        
        # Initialize controller
        controller = PhosphobotJointController()
        time.sleep(1)
        
        try:
            # Initialize robots (optional)
            if not skip_init:
                print("\n🔧 Initializing robots...")
                controller.initialize_robot()
                time.sleep(2)
            else:
                print("\n⚠️  Skipping robot initialization to prevent collisions")
            
            # Read current joint positions for partial configuration support
            current_left_joints = None
            current_right_joints = None
            
            if has_left_arm:
                print(f"\n📖 Reading current left arm (ID {left_arm_id}) position...")
                current_left_joints = controller.get_current_joint_angles(left_arm_id)
                
            if has_right_arm:
                print(f"📖 Reading current right arm (ID {right_arm_id}) position...")
                current_right_joints = controller.get_current_joint_angles(right_arm_id)
            
            # Prepare joint configurations (supporting partial configs)
            left_joints = None
            right_joints = None
            
            print(f"\n🔧 Preparing joint configurations...")
            
            if has_left_arm:
                left_joints = prepare_arm_configuration(
                    config_data['left_arm'], 
                    current_left_joints, 
                    "left_arm"
                )
                
            if has_right_arm:
                right_joints = prepare_arm_configuration(
                    config_data['right_arm'], 
                    current_right_joints, 
                    "right_arm"
                )
            
            print(f"\n🎯 Moving to configuration: {config.get('name', config_name)}")
            
            # Move configured arms using smooth trajectories or step-based
            success = True
            
            if has_left_arm and left_joints:
                print(f"\n🦾 Left arm (ID {left_arm_id}) target: {[f'{j:.3f}' for j in left_joints]}")
                if use_trajectory and TRAJECTORY_AVAILABLE:
                    success &= controller.execute_smooth_trajectory(
                        left_arm_id, 
                        left_joints,
                        duration=trajectory_duration,
                        max_velocity=max_velocity,
                        num_waypoints=num_waypoints
                    )
                else:
                    result = controller.write_joint_positions(left_arm_id, left_joints)
                    success &= result is not None
                    time.sleep(1)
            else:
                print(f"Left arm (ID {left_arm_id}): keeping current position")
            
            if has_right_arm and right_joints:
                print(f"\n🦾 Right arm (ID {right_arm_id}) target: {[f'{j:.3f}' for j in right_joints]}")
                if use_trajectory and TRAJECTORY_AVAILABLE:
                    success &= controller.execute_smooth_trajectory(
                        right_arm_id, 
                        right_joints,
                        duration=trajectory_duration,
                        max_velocity=max_velocity,
                        num_waypoints=num_waypoints
                    )
                else:
                    result = controller.write_joint_positions(right_arm_id, right_joints)
                    success &= result is not None
                    time.sleep(1)
            else:
                print(f"Right arm (ID {right_arm_id}): keeping current position")
            
            # Wait for movement completion
            time.sleep(2)
            
            print("\n📖 Reading final joint positions...")
            if has_left_arm:
                controller.read_joint_positions(left_arm_id)
            if has_right_arm:
                controller.read_joint_positions(right_arm_id)
            
            if success:
                print(f"\n🎉 Successfully moved to configuration: {config.get('name', config_name)}")
            else:
                print(f"\n⚠️  Completed with some issues: {config.get('name', config_name)}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during robot execution: {e}")
            return False
        finally:
            controller.close()
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def execute_configuration(config_name: str, skip_init: bool = True, left_arm_id: int = 0, right_arm_id: int = 3):
    """Execute a specific configuration by loading it from JSON.
    
    Enhanced to support:
    - Complete and partial joint configurations
    - Single-arm and dual-arm movements  
    - Automatic merging with current joint positions for incomplete configurations
    """
    
    print(f"🤖 Loading and executing configuration: {config_name}")
    print("=" * 60)
    print(f"🔧 Left arm ID: {left_arm_id} (5A68011258)")
    print(f"🔧 Right arm ID: {right_arm_id} (5A68009540)")
    
    try:
        # Load configuration
        config = load_configuration(config_name)
        
        # Validate configuration structure
        if 'configuration' not in config:
            raise ValueError("Invalid configuration: missing 'configuration' section")
        
        config_data = config['configuration']
        
        # Check which arms are configured
        has_left_arm = 'left_arm' in config_data and config_data['left_arm'] is not None
        has_right_arm = 'right_arm' in config_data and config_data['right_arm'] is not None
        
        if not has_left_arm and not has_right_arm:
            raise ValueError("Invalid configuration: no arm configuration found")
        
        print(f"📋 Configuration: {config.get('name', 'Unknown')}")
        print(f"📝 Description: {config.get('description', 'No description')}")
        print(f"📊 Source: {config.get('source', {}).get('dataset', 'Unknown')}")
        
        # Show which arms will be moved
        if has_left_arm and has_right_arm:
            print("🎯 Mode: Dual-arm movement")
        elif has_left_arm:
            print("🎯 Mode: Left arm only (right arm stays steady)")
        elif has_right_arm:
            print("🎯 Mode: Right arm only (left arm stays steady)")
        
        # Initialize controller
        controller = PhosphobotJointController()
        time.sleep(1)
        
        try:
            # Initialize robots (optional)
            if not skip_init:
                print("\n🔧 Initializing robots...")
                controller.initialize_robot()
                time.sleep(2)
            else:
                print("\n⚠️  Skipping robot initialization to prevent collisions")
            
            # Read current joint positions for partial configuration support
            current_left_joints = None
            current_right_joints = None
            
            if has_left_arm:
                print(f"\n📖 Reading current left arm (ID {left_arm_id}) position...")
                current_left_joints = controller.get_current_joint_angles(left_arm_id)
                
            if has_right_arm:
                print(f"📖 Reading current right arm (ID {right_arm_id}) position...")
                current_right_joints = controller.get_current_joint_angles(right_arm_id)
            
            # Prepare joint configurations (supporting partial configs)
            left_joints = None
            right_joints = None
            
            print(f"\n🔧 Preparing joint configurations...")
            
            if has_left_arm:
                left_joints = prepare_arm_configuration(
                    config_data['left_arm'], 
                    current_left_joints, 
                    "left_arm"
                )
                
            if has_right_arm:
                right_joints = prepare_arm_configuration(
                    config_data['right_arm'], 
                    current_right_joints, 
                    "right_arm"
                )
            
            print(f"\n🎯 Moving to configuration: {config.get('name', config_name)}")
            
            # Move configured arms
            if has_left_arm and left_joints:
                print(f"Left arm (ID {left_arm_id}) joints: {[f'{j:.3f}' for j in left_joints]}")
                controller.write_joint_positions(left_arm_id, left_joints)
                time.sleep(1)
            else:
                print(f"Left arm (ID {left_arm_id}): keeping current position")
            
            if has_right_arm and right_joints:
                print(f"Right arm (ID {right_arm_id}) joints: {[f'{j:.3f}' for j in right_joints]}")
                controller.write_joint_positions(right_arm_id, right_joints)
                time.sleep(1)
            else:
                print(f"Right arm (ID {right_arm_id}): keeping current position")
            
            # Wait for movement completion
            time.sleep(2)
            
            print("\n📖 Reading final joint positions...")
            if has_left_arm:
                controller.read_joint_positions(left_arm_id)
            if has_right_arm:
                controller.read_joint_positions(right_arm_id)
            
            print(f"\n🎉 Successfully moved to configuration: {config.get('name', config_name)}")
            
        except Exception as e:
            print(f"❌ Error during robot execution: {e}")
            return False
        finally:
            controller.close()
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    return True

def execute_learned_sequence():
    """Execute the learned manipulation sequence from the dataset using exact joint positions."""
    
    print("🤖 Starting learned sequence from Hafnium49/aloha_lite episode 1")
    print("================================================================")
    print("🎯 Using EXACT joint positions from the dataset")
    
    # Initialize controller
    controller = PhosphobotJointController()
    
    # Wait for connection
    time.sleep(1)
    
    
    # Exact joint positions from the generated rules
    left_arm_stage_0 = [0.17184780538082123, -1.8642418384552002, 1.459172010421753, -1.7568368911743164, -1.3824541568756104, 0.7871243357658386]
    right_arm_stage_0 = [0.37898579239845276, -1.8044019937515259, 1.4392253160476685, -1.7553025484085083, -1.614141821861267, 1.5803860425949097]
    
    left_arm_stage_1 = [0.17184780538082123, -1.8642418384552002, 1.459172010421753, -1.7568368911743164, -1.3824541568756104, 0.7871243357658386]
    right_arm_stage_1 = [0.37898579239845276, -1.8044019937515259, 1.4131413698196411, -1.7553025484085083, -1.614141821861267, 1.5803860425949097]
    
    try:
        # Initialize robots
        print("\n🔧 Initializing robots...")
        controller.initialize_robot()  # Initialize system
        time.sleep(2)
        
        print("\n🎯 Stage 0: Initial positioning...")
        print("Left arm joints: [0.172, -1.864, 1.459, -1.757, -1.382, 0.787]")
        print("Right arm joints: [0.379, -1.804, 1.439, -1.755, -1.614, 1.580]")
        
        # Move left arm (robot_id=0) to stage 0 position
        controller.write_joint_positions(0, left_arm_stage_0)
        time.sleep(1)
        
        # Move right arm (robot_id=1) to stage 0 position
        controller.write_joint_positions(1, right_arm_stage_0)
        time.sleep(3)
        
        print("\n🎯 Stage 1: Fine adjustment...")
        print("Left arm: maintains position")
        print("Right arm: joint 3 changes from 1.439 → 1.413 (fine manipulation)")
        
        # Move left arm (maintains same position)
        controller.write_joint_positions(0, left_arm_stage_1)
        time.sleep(1)
        
        # Move right arm (slight adjustment in joint 3)
        controller.write_joint_positions(1, right_arm_stage_1)
        time.sleep(3)
        
        print("\n🎯 Stage 2: Final position...")
        print("Both arms maintain their stage 1 positions")
        
        # Final positions (same as stage 1)
        controller.write_joint_positions(0, left_arm_stage_1)
        time.sleep(1)
        controller.write_joint_positions(1, right_arm_stage_1)
        time.sleep(3)
        
        print("\n📖 Reading final joint positions...")
        controller.read_joint_positions(0)
        controller.read_joint_positions(1)
        
        print("\n🎉 Demo finished successfully!")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return False
    finally:
        controller.close()
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute robot configurations from JSON files")
    parser.add_argument("--config", "-c", type=str, 
                       help="Configuration name to load (e.g., 'standoff_configuration_stage1')")
    parser.add_argument("--legacy", action="store_true",
                       help="Run the original learned sequence demo")
    parser.add_argument("--init", action="store_true",
                       help="Enable robot initialization (WARNING: may cause collisions)")
    parser.add_argument("--no-init", action="store_true", 
                       help="Explicitly disable robot initialization (default)")
    parser.add_argument("--left-arm-id", type=int, default=0,
                       help="Left arm robot ID (default: 0 for 5A68011258)")
    parser.add_argument("--right-arm-id", type=int, default=3,
                       help="Right arm robot ID (default: 3 for 5A68009540)")
    
    # Trajectory planning arguments
    parser.add_argument("--smooth", action="store_true",
                       help="Use smooth trajectory planning (requires modern_robotics)")
    parser.add_argument("--step", action="store_true", 
                       help="Use step-based movement (traditional mode)")
    parser.add_argument("--duration", "-d", type=float,
                       help="Trajectory duration in seconds (auto-calculated if not specified)")
    parser.add_argument("--max-velocity", type=float, default=0.3,
                       help="Maximum joint velocity for trajectory planning (default: 0.3 rad/s)")
    parser.add_argument("--waypoints", type=int, default=3,
                       help="Number of trajectory waypoints (default: 3)")
    
    args = parser.parse_args()
    
    # Determine initialization setting
    if args.init:
        skip_init = False
        print("⚠️  Robot initialization ENABLED - use with caution!")
    else:
        skip_init = True
        if not args.no_init:
            print("✅ Robot initialization DISABLED by default (safer)")
    
    # Determine execution mode
    if args.step:
        use_trajectory = False
        print("📐 Using STEP-BASED movement (traditional)")
    elif args.smooth:
        use_trajectory = True
        print("🎬 Using SMOOTH trajectory planning")
    else:
        # Default behavior: use smooth if available, fallback to step-based
        use_trajectory = TRAJECTORY_AVAILABLE
        if TRAJECTORY_AVAILABLE:
            print("🎬 Using SMOOTH trajectory planning (default)")
        else:
            print("📐 Using STEP-BASED movement (ModernRobotics not available)")
    
    if args.config:
        # Execute specific configuration with trajectory option
        success = execute_configuration_smooth(
            args.config, 
            skip_init=skip_init, 
            left_arm_id=args.left_arm_id, 
            right_arm_id=args.right_arm_id,
            use_trajectory=use_trajectory,
            trajectory_duration=args.duration,
            max_velocity=args.max_velocity,
            num_waypoints=args.waypoints
        )
        if success:
            print(f"\n✅ Configuration '{args.config}' executed successfully!")
        else:
            print(f"\n❌ Failed to execute configuration '{args.config}'!")
            sys.exit(1)
    elif args.legacy:
        # Run original demo
        success = execute_learned_sequence()
        if success:
            print("\n✅ Learned sequence executed successfully!")
        else:
            print("\n❌ Failed to execute learned sequence!")
            sys.exit(1)
    else:
        # Default: show help and available configurations
        parser.print_help()
        print("\nAvailable configurations:")
        
        # Look for JSON config files
        search_dirs = ["./temp_rules", "./", "./aloha-lite-demo2rule", "./configs"]
        found_configs = []
        
        for search_dir in search_dirs:
            search_path = Path(search_dir)
            if search_path.exists():
                for json_file in search_path.glob("*.json"):
                    try:
                        with open(json_file, 'r') as f:
                            config_data = json.load(f)
                        
                        # Handle multi-configuration files
                        if 'configurations' in config_data:
                            for config_name, config in config_data['configurations'].items():
                                if 'configuration' in config and 'name' in config:
                                    found_configs.append({
                                        'file': str(json_file),
                                        'name': config['name'],
                                        'description': config.get('description', 'No description')
                                    })
                        # Handle single configuration files
                        elif 'configuration' in config_data and 'name' in config_data:
                            found_configs.append({
                                'file': str(json_file),
                                'name': config_data['name'],
                                'description': config_data.get('description', 'No description')
                            })
                    except:
                        continue
        
        if found_configs:
            print("\n📋 Found configurations:")
            for config in found_configs:
                print(f"  • {config['name']}")
                print(f"    File: {config['file']}")
                print(f"    Description: {config['description']}")
                print()
            
            print("Usage examples:")
            print("  # Basic configuration execution (smooth trajectory by default):")
            print(f"  python3 execute_rules.py --config standoff_configuration_stage1")
            print(f"  python3 execute_rules.py --config dispensing_water_to_beaker")
            print()
            print("  # Trajectory control:")
            print(f"  python3 execute_rules.py --config beaker_ready --smooth  # Force smooth trajectory")
            print(f"  python3 execute_rules.py --config beaker_ready --step   # Force step-based")
            print(f"  python3 execute_rules.py --config beaker_ready --duration 5.0  # Custom duration")
            print(f"  python3 execute_rules.py --config beaker_ready --max-velocity 0.2  # Slower movement")
            print(f"  python3 execute_rules.py --config beaker_ready --waypoints 10  # More waypoints (default: 3)")
            print()
            print("  # Arm-specific controls:")
            print(f"  python3 execute_rules.py --config left_arm_only_demo  # Single arm movement")
            print(f"  python3 execute_rules.py --config right_arm_only_demo  # Single arm movement")
            print(f"  python3 execute_rules.py --config dual_arm_config --left-arm-id 3 --right-arm-id 2")
            print()
            print("  # Safety options:")
            print(f"  python3 execute_rules.py --config standoff_configuration_stage1 --init  # Enable init (risky)")
            print(f"  python3 execute_rules.py --config ready_to_pick_beaker --no-init  # Disable init (safe)")
            print()
            print("  # Legacy mode:")
            print(f"  python3 execute_rules.py --legacy  # Original demo sequence")
        else:
            print("  No configuration files found.")
            print("  Use --legacy to run the original demo.")
