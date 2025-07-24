#!/usr/bin/env python3
"""
Sequential Robot Configuration Executor

This script executes multiple robot configurations in sequence, allowing for 
complex multi-step robot procedures with proper timing and safety checks.
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
import requests
import re
import base64
from datetime import datetime

def load_robot_arm_config():
    """Load robot arm and camera configuration from JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), "../temp_rules/robot_arm_config.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print(f"⚠️  Robot arm config not found at {config_path}, using defaults")
        return {
            "robot_arms": {
                "left_arm": {"robot_id": 0, "device_id": "5A68011258"},
                "right_arm": {"robot_id": 2, "device_id": "5A68009540"}
            },
            "cameras": {
                "default_camera": {"camera_id": 2, "name": "Primary Camera"},
                "available_cameras": [
                    {"camera_id": 0, "name": "Camera 0"},
                    {"camera_id": 1, "name": "Camera 1"},
                    {"camera_id": 2, "name": "Camera 2"}
                ]
            }
        }
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in robot arm config: {e}")
        return {
            "robot_arms": {
                "left_arm": {"robot_id": 0, "device_id": "5A68011258"},
                "right_arm": {"robot_id": 2, "device_id": "5A68009540"}
            },
            "cameras": {
                "default_camera": {"camera_id": 2, "name": "Primary Camera"},
                "available_cameras": [
                    {"camera_id": 0, "name": "Camera 0"},
                    {"camera_id": 1, "name": "Camera 1"},
                    {"camera_id": 2, "name": "Camera 2"}
                ]
            }
        }

# Load robot arm and camera configuration at module level
ROBOT_ARM_CONFIG = load_robot_arm_config()
LEFT_ARM_ID = ROBOT_ARM_CONFIG["robot_arms"]["left_arm"]["robot_id"]
RIGHT_ARM_ID = ROBOT_ARM_CONFIG["robot_arms"]["right_arm"]["robot_id"]
LEFT_ARM_DEVICE = ROBOT_ARM_CONFIG["robot_arms"]["left_arm"]["device_id"]
RIGHT_ARM_DEVICE = ROBOT_ARM_CONFIG["robot_arms"]["right_arm"]["device_id"]
DEFAULT_CAMERA_ID = ROBOT_ARM_CONFIG["cameras"]["default_camera"]["camera_id"]
AVAILABLE_CAMERA_IDS = [cam["camera_id"] for cam in ROBOT_ARM_CONFIG["cameras"]["available_cameras"]]

# Import the existing functionality from execute_rules.py
sys.path.append(str(Path(__file__).parent))
from execute_rules import PhosphobotJointController, load_configuration, prepare_arm_configuration

# Import squeeze bottle functions
from squeeze_bottle import squeeze_washing_bottle_simple, squeeze_washing_bottle

# Check if ModernRobotics is available for trajectory planning
try:
    import modern_robotics as mr
    TRAJECTORY_AVAILABLE = True
except ImportError:
    TRAJECTORY_AVAILABLE = False

class SequentialRobotExecutor:
    """Execute multiple robot configurations in sequence."""
    
    def __init__(self, server_url: str = "http://localhost:80", skip_init: bool = True, 
                 left_arm_id: int = LEFT_ARM_ID, right_arm_id: int = RIGHT_ARM_ID):
        self.server_url = server_url
        self.skip_init = skip_init
        self.left_arm_id = left_arm_id
        self.right_arm_id = right_arm_id
        self.controller = None
        
    def initialize(self):
        """Initialize the robot controller."""
        self.controller = PhosphobotJointController(self.server_url)
        time.sleep(1)
        
        print(f"🔧 Left arm ID: {self.left_arm_id} ({LEFT_ARM_DEVICE})")
        print(f"🔧 Right arm ID: {self.right_arm_id} ({RIGHT_ARM_DEVICE})")
        
        if not self.skip_init:
            print("\n🔧 Initializing robots...")
            self.controller.initialize_robot()
            time.sleep(2)
        else:
            print("\n⚠️  Skipping robot initialization to prevent collisions")
    
    def execute_step(self, step: str, pause_after: float = 3.0, 
                    use_trajectory: bool = True, trajectory_duration: float = None,
                    max_velocity: float = 0.3, num_waypoints: int = None,
                    adaptive_waypoints: bool = True):
        """Execute a single step which can be either a configuration or a special function.
        
        Args:
            step (str): Either a configuration name or a special function call
            pause_after (float): Pause after step execution
            use_trajectory (bool): Use trajectory planning for configurations
            trajectory_duration (float): Optional trajectory duration
            max_velocity (float): Maximum velocity for trajectories
            num_waypoints (int): Number of waypoints
            adaptive_waypoints (bool): Use adaptive waypoint calculation
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        # Check if this is a special function call
        if self._is_special_function(step):
            return self._execute_special_function(step, pause_after)
        else:
            # Execute as a regular configuration
            return self.execute_configuration(
                step, pause_after, use_trajectory, trajectory_duration,
                max_velocity, num_waypoints, adaptive_waypoints
            )
    
    def _is_special_function(self, step: str) -> bool:
        """Check if a step is a special function call."""
        special_patterns = [
            r"squeeze.*bottle.*for.*(\d+\.?\d*)\s*seconds?",
            r"squeeze.*washing.*bottle.*(\d+\.?\d*)",
            r"squeeze.*(\d+\.?\d*)",
            r"await.*(\d+\.?\d*)\s*seconds?",
            r"wait.*(\d+\.?\d*)\s*seconds?",
            r"pause.*(\d+\.?\d*)\s*seconds?",
            r"delay.*(\d+\.?\d*)\s*seconds?",
            r"take.*picture",
            r"capture.*image",
            r"snap.*photo",
            r"take.*photo.*camera.*(\d+)",
            r"capture.*camera.*(\d+)",
            r"analyze.*beaker.*color",
            r"beaker.*analysis",
            r"analyze.*solution.*color",
            r"color.*analysis"
        ]
        
        step_lower = step.lower()
        for pattern in special_patterns:
            if re.search(pattern, step_lower):
                return True
        return False
    
    def _execute_special_function(self, step: str, pause_after: float = 3.0) -> bool:
        """Execute a special function based on the step description."""
        step_lower = step.lower()
        
        # Pattern for squeeze bottle functions
        squeeze_patterns = [
            r"squeeze.*bottle.*for.*(\d+\.?\d*)\s*seconds?",
            r"squeeze.*washing.*bottle.*(\d+\.?\d*)",
            r"squeeze.*(\d+\.?\d*)"
        ]
        
        # Pattern for await/wait/pause/delay functions
        await_patterns = [
            r"await.*(\d+\.?\d*)\s*seconds?",
            r"wait.*(\d+\.?\d*)\s*seconds?",
            r"pause.*(\d+\.?\d*)\s*seconds?",
            r"delay.*(\d+\.?\d*)\s*seconds?"
        ]
        
        # Pattern for camera capture functions
        camera_patterns = [
            r"take.*picture",
            r"capture.*image",
            r"snap.*photo",
            r"take.*photo.*camera.*(\d+)",
            r"capture.*camera.*(\d+)"
        ]
        
        # Pattern for beaker analysis functions
        beaker_analysis_patterns = [
            r"analyze.*beaker.*color",
            r"beaker.*analysis",
            r"analyze.*solution.*color",
            r"color.*analysis"
        ]
        
        # Check for beaker analysis patterns first
        for pattern in beaker_analysis_patterns:
            match = re.search(pattern, step_lower)
            if match:
                print(f"\n🧪 Executing special function: Beaker Color Analysis")
                print("🔬 Capturing image and analyzing beaker solution color...")
                print("=" * 50)
                
                try:
                    success = self._execute_beaker_analysis()
                    
                    if success:
                        print(f"✅ Successfully completed beaker color analysis")
                    else:
                        print(f"❌ Failed to complete beaker color analysis")
                    
                    # Apply additional pause if specified
                    if pause_after > 0:
                        print(f"\n⏱️  Pausing {pause_after}s after beaker analysis...")
                        time.sleep(pause_after)
                    
                    return success
                    
                except Exception as e:
                    print(f"❌ Error executing beaker analysis function: {e}")
                    return False
        
        # Check for camera capture patterns
        for pattern in camera_patterns:
            match = re.search(pattern, step_lower)
            if match:
                # Extract camera ID if specified, otherwise use default from config
                camera_id = DEFAULT_CAMERA_ID  # Default camera from config
                if match.groups():
                    try:
                        camera_id = int(match.group(1))
                    except (ValueError, IndexError):
                        camera_id = DEFAULT_CAMERA_ID
                
                print(f"\n📷 Executing special function: Camera Capture")
                print(f"📹 Camera ID: {camera_id} (from config)")
                print("=" * 50)
                
                try:
                    print(f"📸 Capturing image from camera {camera_id}...")
                    success = self._execute_camera_capture(camera_id)
                    
                    if success:
                        print(f"✅ Successfully captured and saved image from camera {camera_id}")
                    else:
                        print(f"❌ Failed to capture image from camera {camera_id}")
                    
                    # Apply additional pause if specified
                    if pause_after > 0:
                        print(f"\n⏱️  Pausing {pause_after}s after camera capture...")
                        time.sleep(pause_after)
                    
                    return success
                    
                except Exception as e:
                    print(f"❌ Error executing camera capture function: {e}")
                    return False
        
        # Check for await/wait patterns
        for pattern in await_patterns:
            match = re.search(pattern, step_lower)
            if match:
                duration = float(match.group(1))
                print(f"\n⏳ Executing special function: Await/Wait")
                print(f"⏱️  Duration: {duration} seconds")
                print("=" * 50)
                
                try:
                    print(f"⏸️  Robot staying in current position for {duration} seconds...")
                    print("💡 This allows time for external processes, settling, or user observation")
                    
                    # Simple countdown for user feedback
                    if duration >= 5.0:
                        # For longer waits, show countdown every 5 seconds
                        remaining = duration
                        while remaining > 0:
                            if remaining >= 5:
                                print(f"⏳ {remaining:.1f} seconds remaining...")
                                time.sleep(5.0)
                                remaining -= 5.0
                            else:
                                time.sleep(remaining)
                                remaining = 0
                    else:
                        # For shorter waits, just wait
                        time.sleep(duration)
                    
                    print(f"✅ Successfully completed {duration}s await/wait period")
                    
                    # Apply additional pause if specified (usually 0 for await functions)
                    if pause_after > 0:
                        print(f"\n⏱️  Additional pause {pause_after}s after await function...")
                        time.sleep(pause_after)
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error executing await function: {e}")
                    return False
        
        # Check for squeeze bottle patterns
        for pattern in squeeze_patterns:
            match = re.search(pattern, step_lower)
            if match:
                duration = float(match.group(1))
                print(f"\n🧴 Executing special function: Squeeze washing bottle")
                print(f"⏱️  Duration: {duration} seconds")
                print("=" * 50)
                
                try:
                    # Store current joint positions before squeeze operation
                    print("📖 Storing current robot positions before squeeze operation...")
                    current_left_joints = None
                    current_right_joints = None
                    
                    # Ensure controller is available
                    if not self.controller:
                        print("❌ Robot controller not available")
                        return False
                    
                    # Read current positions with retry logic
                    for attempt in range(3):
                        current_left_joints = self.controller.get_current_joint_angles(self.left_arm_id)
                        current_right_joints = self.controller.get_current_joint_angles(self.right_arm_id)
                        
                        if current_left_joints is not None and current_right_joints is not None:
                            break
                        
                        if attempt < 2:
                            print(f"⚠️  Attempt {attempt + 1} failed, retrying position read...")
                            time.sleep(0.5)
                    
                    if current_left_joints is None or current_right_joints is None:
                        print("❌ Failed to read current joint positions after 3 attempts")
                        return False
                    
                    print(f"💾 Stored left arm position: {[f'{j:.3f}' for j in current_left_joints]}")
                    print(f"💾 Stored right arm position: {[f'{j:.3f}' for j in current_right_joints]}")
                    
                    # Execute squeeze operation (only affects right arm j6)
                    print("🤏 Executing squeeze operation...")
                    success = self._execute_squeeze_operation(duration)
                    
                    if not success:
                        print("❌ Failed to execute squeeze operation")
                        # Try to restore positions even if squeeze failed
                        print("🔄 Attempting to restore positions after failed squeeze...")
                        self._restore_joint_positions(current_left_joints, current_right_joints)
                        return False
                    
                    # Restore both arms to their previous positions
                    print("🔄 Restoring robot positions after squeeze operation...")
                    restore_success = self._restore_joint_positions(current_left_joints, current_right_joints)
                    
                    if restore_success:
                        print(f"✅ Successfully completed squeeze bottle function with position restoration")
                    else:
                        print(f"⚠️  Squeeze completed but position restoration had issues")
                    
                    # Apply pause after special function
                    if pause_after > 0:
                        print(f"\n⏱️  Pausing {pause_after}s after special function...")
                        time.sleep(pause_after)
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error executing squeeze bottle function: {e}")
                    return False
        
        print(f"❌ Unknown special function: {step}")
        return False
    
    def _restore_joint_positions(self, left_joints: list, right_joints: list) -> bool:
        """Restore joint positions for both arms with error handling."""
        restore_success = True
        
        try:
            # Restore left arm position
            print(f"🦾 Restoring left arm (ID {self.left_arm_id}) to stored position...")
            result_left = self.controller.write_joint_positions(self.left_arm_id, left_joints)
            if result_left is None:
                print("⚠️  Warning: Failed to restore left arm position")
                restore_success = False
            
            # Restore right arm position (this will release the squeeze)
            print(f"🦾 Restoring right arm (ID {self.right_arm_id}) to stored position...")
            result_right = self.controller.write_joint_positions(self.right_arm_id, right_joints)
            if result_right is None:
                print("⚠️  Warning: Failed to restore right arm position")
                restore_success = False
            
            # Allow time for movement completion
            time.sleep(2.0)
            
            # Verify final positions
            print("📖 Verifying restored positions...")
            final_left = self.controller.get_current_joint_angles(self.left_arm_id)
            final_right = self.controller.get_current_joint_angles(self.right_arm_id)
            
            if final_left and final_right:
                print(f"✅ Final left arm position: {[f'{j:.3f}' for j in final_left]}")
                print(f"✅ Final right arm position: {[f'{j:.3f}' for j in final_right]}")
                
                # Check if positions are reasonably close to target
                left_error = max(abs(f - t) for f, t in zip(final_left, left_joints))
                right_error = max(abs(f - t) for f, t in zip(final_right, right_joints))
                
                if left_error > 0.1:  # 0.1 radians ~ 5.7 degrees
                    print(f"⚠️  Left arm position error: {left_error:.3f} rad")
                    restore_success = False
                
                if right_error > 0.1:
                    print(f"⚠️  Right arm position error: {right_error:.3f} rad")
                    restore_success = False
            else:
                print("❌ Failed to read final positions for verification")
                restore_success = False
            
            return restore_success
            
        except Exception as e:
            print(f"❌ Error during position restoration: {e}")
            return False
    
    def _execute_squeeze_operation(self, duration: float) -> bool:
        """Execute the actual squeeze operation (right arm j6 only)."""
        try:
            # Get current right arm position
            current_right_joints = self.controller.get_current_joint_angles(self.right_arm_id)
            if current_right_joints is None:
                print("❌ Failed to read current right arm position for squeeze operation")
                return False
            
            # Create squeeze position (modify only j6 to 0.3)
            squeeze_joints = current_right_joints.copy()
            squeeze_joints[5] = 0.3  # j6 = 0.3 for squeeze
            
            print(f"🤏 Squeezing: Right arm j6 from {current_right_joints[5]:.3f} to 0.300")
            
            # Execute squeeze
            result = self.controller.write_joint_positions(self.right_arm_id, squeeze_joints)
            if result is None:
                print("❌ Failed to execute squeeze movement")
                return False
            
            # Hold squeeze for specified duration
            print(f"⏸️  Holding squeeze for {duration} seconds...")
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during squeeze operation: {e}")
            return False
    
    def _execute_camera_capture(self, camera_id: int = None) -> bool:
        """Execute camera capture using Phospho API and save to temporary images directory."""
        try:
            # Use configured default camera if not specified
            if camera_id is None:
                camera_id = DEFAULT_CAMERA_ID
            
            # Validate camera ID is in available cameras
            if camera_id not in AVAILABLE_CAMERA_IDS:
                print(f"⚠️  Warning: Camera {camera_id} not in configured available cameras: {AVAILABLE_CAMERA_IDS}")
                print(f"💡 Using default camera {DEFAULT_CAMERA_ID} instead")
                camera_id = DEFAULT_CAMERA_ID
            
            # Create temporary images directory if it doesn't exist
            temp_images_dir = Path(os.path.dirname(__file__)) / "../temporary_images"
            temp_images_dir.mkdir(exist_ok=True)
            
            print(f"📁 Images will be saved to: {temp_images_dir.absolute()}")
            
            # Make API request to capture snapshot from vision bridge
            snapshot_url = f"{self.server_url}/snapshot"
            print(f"🌐 Making API request: POST {snapshot_url}")
            
            # Generate a unique command ID for the snapshot request
            import uuid
            cmd_id = str(uuid.uuid4())
            
            # Use the correct camera ID format for vision bridge
            cam_id = f"camera_{camera_id}" if isinstance(camera_id, int) else camera_id
            snapshot_data = {
                "cmd_id": cmd_id,
                "cam_id": cam_id
            }
            
            response = requests.post(snapshot_url, json=snapshot_data, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ API request failed with status {response.status_code}: {response.text}")
                return False
            
            snapshot_response = response.json()
            print(f"📋 Snapshot response received for camera {cam_id}")
            
            # Extract base64 image from the snapshot response
            if 'image' not in snapshot_response:
                print(f"❌ No image data in snapshot response")
                print(f"💡 Response keys: {list(snapshot_response.keys())}")
                return False
            
            base64_image = snapshot_response['image']
            
            if base64_image is None:
                print(f"❌ Camera {camera_id} returned None (camera might be unavailable)")
                return False
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"camera_{camera_id}_{timestamp}.jpg"
            filepath = temp_images_dir / filename
            
            # Decode base64 and save image
            print(f"💾 Decoding and saving image to: {filename}")
            image_data = base64.b64decode(base64_image)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Verify file was saved successfully
            if filepath.exists():
                file_size = filepath.stat().st_size
                print(f"✅ Image saved successfully: {filename} ({file_size} bytes)")
                return True
            else:
                print(f"❌ Failed to save image file: {filename}")
                return False
            
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - camera capture took too long")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during camera capture: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response from camera API: {e}")
            return False
        except base64.binascii.Error as e:
            print(f"❌ Failed to decode base64 image data: {e}")
            return False
        except OSError as e:
            print(f"❌ File system error while saving image: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during camera capture: {e}")
            return False
    
    def _execute_beaker_analysis(self, camera_id: int = None) -> bool:
        """Execute beaker color analysis by capturing an image and analyzing it using the vision bridge API."""
        try:
            # Use configured default camera if not specified
            if camera_id is None:
                camera_id = DEFAULT_CAMERA_ID
            
            print(f"📸 Step 1: Capturing image from camera {camera_id}...")
            
            # First capture an image using the existing camera capture function
            capture_success = self._execute_camera_capture(camera_id)
            if not capture_success:
                print("❌ Failed to capture image for beaker analysis")
                return False
            
            # Find the most recent image file
            temp_images_dir = Path(os.path.dirname(__file__)) / "../temporary_images"
            if not temp_images_dir.exists():
                print("❌ Temporary images directory not found")
                return False
            
            # Get the most recent image file for the specified camera
            image_files = list(temp_images_dir.glob(f"camera_{camera_id}_*.jpg"))
            if not image_files:
                print(f"❌ No image files found for camera {camera_id}")
                return False
            
            # Sort by modification time and get the most recent
            latest_image = max(image_files, key=lambda p: p.stat().st_mtime)
            print(f"🖼️  Using image: {latest_image.name}")
            
            print(f"\n🔬 Step 2: Analyzing beaker color using vision bridge API...")
            
            # Make API request to vision bridge for beaker analysis
            vision_bridge_url = "http://localhost:8000/analyze-beaker"
            print(f"🌐 Making API request: POST {vision_bridge_url}")
            
            # Prepare the image file for upload
            with open(latest_image, 'rb') as image_file:
                files = {'file': (latest_image.name, image_file, 'image/jpeg')}
                
                response = requests.post(vision_bridge_url, files=files, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Vision bridge API request failed with status {response.status_code}: {response.text}")
                return False
            
            # Parse the analysis results
            analysis_data = response.json()
            
            print(f"\n📊 Step 3: Beaker Analysis Results")
            print("=" * 50)
            
            # Extract and display key results
            dominant_color = analysis_data.get('dominant_color', {})
            beaker_circle = analysis_data.get('beaker_circle', {})
            clusters = analysis_data.get('clusters', [])
            stats = analysis_data.get('analysis_stats', {})
            
            # Display dominant color
            rgb = dominant_color.get('rgb', [0, 0, 0])
            hex_color = dominant_color.get('hex', '#000000')
            print(f"🎨 Dominant Solution Color: {hex_color}")
            print(f"   RGB: ({rgb[0]}, {rgb[1]}, {rgb[2]})")
            
            # Display beaker detection info
            x = beaker_circle.get('x', 0)
            y = beaker_circle.get('y', 0)
            radius = beaker_circle.get('radius', 0)
            print(f"\n🥤 Beaker Detection:")
            print(f"   Position: ({x}, {y})")
            print(f"   Radius: {radius} pixels")
            
            # Display analysis statistics
            total_pixels = stats.get('total_pixels_analyzed', 0)
            num_clusters = stats.get('num_clusters', 0)
            print(f"\n📈 Analysis Statistics:")
            print(f"   Pixels analyzed: {total_pixels:,}")
            print(f"   Color clusters found: {num_clusters}")
            
            # Display top 3 color clusters
            print(f"\n🌈 Top Color Clusters:")
            for i, cluster in enumerate(clusters[:3]):
                cluster_rgb = cluster.get('rgb', [0, 0, 0])
                cluster_hex = cluster.get('hex', '#000000')
                pixel_count = cluster.get('pixel_count', 0)
                saturation = cluster.get('saturation', 0)
                print(f"   {i+1}. {cluster_hex} - RGB({cluster_rgb[0]}, {cluster_rgb[1]}, {cluster_rgb[2]}) - {pixel_count:,} pixels (sat: {saturation:.1f})")
            
            # Save analysis results to a JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_filename = f"beaker_analysis_{camera_id}_{timestamp}.json"
            results_filepath = temp_images_dir / results_filename
            
            with open(results_filepath, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            print(f"\n💾 Analysis results saved to: {results_filename}")
            
            # Provide color interpretation
            print(f"\n🧪 Color Interpretation:")
            if hex_color.lower() in ['#ff0000', '#dc143c', '#b22222'] or (rgb[0] > 150 and rgb[1] < 100 and rgb[2] < 100):
                print("   🔴 Red solution detected - likely contains red dye or indicator")
            elif hex_color.lower() in ['#ffff00', '#ffd700', '#daa520'] or (rgb[0] > 200 and rgb[1] > 200 and rgb[2] < 100):
                print("   🟡 Yellow solution detected - likely contains yellow dye or indicator")
            elif hex_color.lower() in ['#0000ff', '#1e90ff', '#4169e1'] or (rgb[0] < 100 and rgb[1] < 100 and rgb[2] > 150):
                print("   🔵 Blue solution detected - likely contains blue dye or indicator")
            elif rgb[0] < 50 and rgb[1] < 50 and rgb[2] < 50:
                print("   ⚫ Dark/black solution detected")
            elif rgb[0] > 200 and rgb[1] > 200 and rgb[2] > 200:
                print("   ⚪ Clear/transparent solution detected")
            else:
                print(f"   🎨 Custom color solution detected: {hex_color}")
            
            print("=" * 50)
            return True
            
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - beaker analysis took too long")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during beaker analysis: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response from vision bridge API: {e}")
            return False
        except FileNotFoundError as e:
            print(f"❌ Image file not found: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during beaker analysis: {e}")
            return False
    
    def execute_configuration(self, config_name: str, pause_after: float = 3.0,
                             use_trajectory: bool = True, trajectory_duration: float = None,
                             max_velocity: float = 0.3, num_waypoints: int = None,
                             adaptive_waypoints: bool = True):
        """Execute a single configuration with optional pause.
        
        Enhanced to support:
        - Smooth trajectory planning with ModernRobotics
        - Adaptive waypoint calculation based on joint displacement magnitude
        - Complete and partial joint configurations
        - Single-arm and dual-arm movements  
        - Automatic merging with current joint positions for incomplete configurations
        """
        print(f"\n🎯 Executing configuration: {config_name}")
        print("=" * 50)
        
        try:
            # Load configuration
            config = load_configuration(config_name)
            
            # Validate configuration structure
            if 'configuration' not in config:
                raise ValueError(f"Invalid configuration '{config_name}': missing 'configuration' section")
            
            config_data = config['configuration']
            
            # Check which arms are configured
            has_left_arm = 'left_arm' in config_data and config_data['left_arm'] is not None
            has_right_arm = 'right_arm' in config_data and config_data['right_arm'] is not None
            
            if not has_left_arm and not has_right_arm:
                raise ValueError(f"Invalid configuration '{config_name}': no arm configuration found")
            
            print(f"📋 Configuration: {config.get('name', 'Unknown')}")
            print(f"📝 Description: {config.get('description', 'No description')}")
            print(f"📊 Source: {config.get('source', {}).get('dataset', config.get('source', {}).get('type', 'Unknown'))}")
            
            # Show which arms will be moved
            if has_left_arm and has_right_arm:
                print("🎯 Mode: Dual-arm movement")
            elif has_left_arm:
                print("🎯 Mode: Left arm only (right arm stays steady)")
            elif has_right_arm:
                print("🎯 Mode: Right arm only (left arm stays steady)")
            
            # Read current joint positions for partial configuration support
            current_left_joints = None
            current_right_joints = None
            
            if has_left_arm:
                current_left_joints = self.controller.get_current_joint_angles(self.left_arm_id)
                if current_left_joints is None:
                    print(f"⚠️  Warning: Failed to read left arm current position")
                
            if has_right_arm:
                current_right_joints = self.controller.get_current_joint_angles(self.right_arm_id)
                if current_right_joints is None:
                    print(f"⚠️  Warning: Failed to read right arm current position")
            
            # Prepare joint configurations (supporting partial configs)
            left_joints = None
            right_joints = None
            
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
            
            print(f"\n🎯 Moving to: {config.get('name', config_name)}")
            
            # Determine execution mode
            trajectory_status = "🎬 SMOOTH TRAJECTORY" if use_trajectory and TRAJECTORY_AVAILABLE else "📐 STEP-BASED"
            print(f"🎯 Execution mode: {trajectory_status}")
            
            success = True
            
            # Move configured arms
            if has_left_arm and left_joints:
                print(f"\n🦾 Left arm (ID {self.left_arm_id}) target: {[f'{j:.3f}' for j in left_joints]}")
                if use_trajectory and TRAJECTORY_AVAILABLE:
                    success &= self.controller.execute_smooth_trajectory(
                        self.left_arm_id, 
                        left_joints,
                        duration=trajectory_duration,
                        max_velocity=max_velocity,
                        num_waypoints=num_waypoints,
                        adaptive_waypoints=adaptive_waypoints
                    )
                else:
                    result = self.controller.write_joint_positions(self.left_arm_id, left_joints)
                    success &= result is not None
                    time.sleep(1)
            else:
                print(f"Left arm (ID {self.left_arm_id}): keeping current position")
            
            if has_right_arm and right_joints:
                print(f"\n🦾 Right arm (ID {self.right_arm_id}) target: {[f'{j:.3f}' for j in right_joints]}")
                if use_trajectory and TRAJECTORY_AVAILABLE:
                    success &= self.controller.execute_smooth_trajectory(
                        self.right_arm_id, 
                        right_joints,
                        duration=trajectory_duration,
                        max_velocity=max_velocity,
                        num_waypoints=num_waypoints,
                        adaptive_waypoints=adaptive_waypoints
                    )
                else:
                    result = self.controller.write_joint_positions(self.right_arm_id, right_joints)
                    success &= result is not None
                    time.sleep(1)
            else:
                print(f"Right arm (ID {self.right_arm_id}): keeping current position")
            
            # Pause to allow movement completion (shorter for smooth trajectories)
            if pause_after > 0:
                pause_time = pause_after if not (use_trajectory and TRAJECTORY_AVAILABLE) else max(1.0, pause_after * 0.5)
                print(f"\n⏱️  Pausing {pause_time}s to complete movement...")
                time.sleep(pause_time)
            
            # Read final positions for moved arms
            print("\n📖 Reading final joint positions...")
            if has_left_arm:
                self.controller.read_joint_positions(self.left_arm_id)
            if has_right_arm:
                self.controller.read_joint_positions(self.right_arm_id)
            
            if success:
                print(f"\n✅ Successfully completed: {config.get('name', config_name)}")
            else:
                print(f"\n⚠️  Completed with errors: {config.get('name', config_name)}")
            return success
            
        except Exception as e:
            print(f"❌ Error executing configuration '{config_name}': {e}")
            return False
    
    def execute_sequence(self, steps: list[str], pause_between: float = 2.0, pause_after_each: float = 3.0,
                        use_trajectory: bool = True, trajectory_duration: float = None,
                        max_velocity: float = 0.3, num_waypoints: int = None,
                        adaptive_waypoints: bool = True):
        """Execute a sequence of steps (configurations and/or special functions)."""
        print(f"🤖 Starting sequential execution of {len(steps)} steps")
        
        # Show trajectory settings
        trajectory_status = "🎬 SMOOTH TRAJECTORY" if use_trajectory and TRAJECTORY_AVAILABLE else "📐 STEP-BASED"
        print(f"🎯 Execution mode: {trajectory_status}")
        print("=" * 70)
        print(f"🔧 Left arm ID: {self.left_arm_id} (5A68011258)")
        print(f"🔧 Right arm ID: {self.right_arm_id} (5A68009540)")
        if use_trajectory and TRAJECTORY_AVAILABLE:
            print(f"📊 Trajectory settings:")
            print(f"   ⏱️  Duration: {'Auto' if trajectory_duration is None else f'{trajectory_duration}s'}")
            print(f"   🎚️  Max velocity: {max_velocity:.3f} rad/s")
            print(f"   📍 Waypoints: {'Auto-adaptive' if num_waypoints is None and adaptive_waypoints else num_waypoints or 'Auto-adaptive'}")
        print("=" * 70)
        
        success_count = 0
        
        try:
            self.initialize()
            
            for i, step in enumerate(steps, 1):
                print(f"\n🔄 Step {i}/{len(steps)}: {step}")
                
                success = self.execute_step(
                    step, 
                    pause_after_each,
                    use_trajectory=use_trajectory,
                    trajectory_duration=trajectory_duration,
                    max_velocity=max_velocity,
                    num_waypoints=num_waypoints,
                    adaptive_waypoints=adaptive_waypoints
                )
                
                if success:
                    success_count += 1
                else:
                    print(f"❌ Failed to execute step {i}, aborting sequence")
                    break
                
                # Pause between steps (except after the last one)
                if i < len(steps) and pause_between > 0:
                    print(f"\n⏳ Pausing {pause_between}s before next step...")
                    time.sleep(pause_between)
            
            print(f"\n🎉 Sequence completed! {success_count}/{len(steps)} steps executed successfully")
            return success_count == len(steps)
            
        except Exception as e:
            print(f"❌ Error during sequence execution: {e}")
            return False
        finally:
            if self.controller:
                self.controller.close()

def main():
    parser = argparse.ArgumentParser(description="Execute robot configurations sequentially")
    parser.add_argument("configs", nargs="+", 
                       help="Configuration names to execute in sequence")
    parser.add_argument("--pause-between", type=float, default=2.0,
                       help="Pause between configurations (seconds)")
    parser.add_argument("--pause-after", type=float, default=3.0,
                       help="Pause after each configuration movement (seconds)")
    parser.add_argument("--init", action="store_true",
                       help="Enable robot initialization (WARNING: may cause collisions)")
    parser.add_argument("--server", default="http://localhost:80",
                       help="Phosphobot server URL")
    parser.add_argument("--left-arm-id", type=int, default=LEFT_ARM_ID,
                       help=f"Left arm robot ID (default: {LEFT_ARM_ID} for {LEFT_ARM_DEVICE})")
    parser.add_argument("--right-arm-id", type=int, default=RIGHT_ARM_ID,
                       help=f"Right arm robot ID (default: {RIGHT_ARM_ID} for {RIGHT_ARM_DEVICE})")
    
    # Trajectory planning arguments
    parser.add_argument("--smooth", action="store_true",
                       help="Use smooth trajectory planning with ModernRobotics")
    parser.add_argument("--step", action="store_true", 
                       help="Use step-based movement (default behavior)")
    parser.add_argument("--duration", "-d", type=float,
                       help="Trajectory duration in seconds (auto-calculated if not specified)")
    parser.add_argument("--max-velocity", type=float, default=0.3,
                       help="Maximum joint velocity for trajectory planning (default: 0.3 rad/s)")
    parser.add_argument("--waypoints", type=int,
                       help="Number of trajectory waypoints (auto-calculated if not specified)")
    parser.add_argument("--no-adaptive-waypoints", action="store_true",
                       help="Disable adaptive waypoint calculation based on joint displacement")
    
    args = parser.parse_args()
    
    # Determine initialization setting
    skip_init = not args.init
    if args.init:
        print("⚠️  Robot initialization ENABLED - use with caution!")
    else:
        print("✅ Robot initialization DISABLED by default (safer)")
    
    # Determine execution mode
    if args.step:
        use_trajectory = False
        print("📐 Using STEP-BASED movement (traditional)")
    elif args.smooth:
        use_trajectory = True
        print("🎬 Using SMOOTH trajectory planning")
    else:
        # Default behavior: use step-based movement (more predictable)
        use_trajectory = False
        print("📐 Using STEP-BASED movement (default)")
        if TRAJECTORY_AVAILABLE:
            print("� Tip: Use --smooth for smooth trajectory planning")
    
    # Execute sequence
    executor = SequentialRobotExecutor(
        args.server, 
        skip_init, 
        left_arm_id=args.left_arm_id, 
        right_arm_id=args.right_arm_id
    )
    success = executor.execute_sequence(
        args.configs, 
        pause_between=args.pause_between,
        pause_after_each=args.pause_after,
        use_trajectory=use_trajectory,
        trajectory_duration=args.duration,
        max_velocity=args.max_velocity,
        num_waypoints=args.waypoints,
        adaptive_waypoints=not args.no_adaptive_waypoints
    )
    
    if success:
        print(f"\n🎉 All configurations executed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Sequence execution failed!")
        sys.exit(1)

# Load predefined sequences from JSON file
def load_predefined_sequences(sequences_file_path: str = None):
    """Load predefined sequences from JSON file with execution options support."""
    if sequences_file_path is None:
        sequences_file = Path(os.path.dirname(__file__)) / "../temp_rules/sequential_sequences.json"
    else:
        sequences_file = Path(sequences_file_path)
    
    if not sequences_file.exists():
        print(f"⚠️  Sequences file not found: {sequences_file}")
        return {}
    
    try:
        with open(sequences_file, 'r') as f:
            data = json.load(f)
        
        # Return the full sequence data including execution_options
        sequences = {}
        for name, seq_data in data.get("predefined_sequences", {}).items():
            sequences[name] = {
                "configurations": seq_data["configurations"],
                "execution_options": seq_data.get("execution_options", {}),
                "description": seq_data.get("description", "")
            }
        
        return sequences
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error loading sequences file: {e}")
        return {}

# Load sequences from JSON file
PREDEFINED_SEQUENCES = load_predefined_sequences()

if __name__ == "__main__":
    # Check for --sequences-file parameter first
    sequences_file_path = None
    if "--sequences-file" in sys.argv:
        try:
            idx = sys.argv.index("--sequences-file")
            if idx + 1 < len(sys.argv):
                sequences_file_path = sys.argv[idx + 1]
                # Remove the parameter from sys.argv to avoid conflicts
                sys.argv.pop(idx)  # Remove --sequences-file
                sys.argv.pop(idx)  # Remove the file path
                print(f"📁 Using custom sequences file: {sequences_file_path}")
        except (ValueError, IndexError):
            print("❌ Error: --sequences-file requires a file path")
            sys.exit(1)
    
    # Load sequences from custom file if specified
    if sequences_file_path:
        PREDEFINED_SEQUENCES = load_predefined_sequences(sequences_file_path)
    
    # Check for predefined sequences
    if len(sys.argv) > 1 and sys.argv[1] in PREDEFINED_SEQUENCES:
        sequence_name = sys.argv[1]
        sequence_data = PREDEFINED_SEQUENCES[sequence_name]
        configs = sequence_data["configurations"]
        execution_options = sequence_data.get("execution_options", {})
        
        # Parse additional arguments for predefined sequences
        parser = argparse.ArgumentParser(description=f"Execute predefined sequence: {sequence_name}")
        parser.add_argument("sequence", help="Predefined sequence name")
        parser.add_argument("--sequences-file", type=str,
                           help="Custom sequences JSON file path (default: ../temp_rules/sequential_sequences.json)")
        parser.add_argument("--left-arm-id", type=int, default=LEFT_ARM_ID,
                           help=f"Left arm robot ID (default: {LEFT_ARM_ID} for {LEFT_ARM_DEVICE})")
        parser.add_argument("--right-arm-id", type=int, default=RIGHT_ARM_ID,
                           help=f"Right arm robot ID (default: {RIGHT_ARM_ID} for {RIGHT_ARM_DEVICE})")
        parser.add_argument("--server", default="http://localhost:80",
                           help="Phosphobot server URL")
        parser.add_argument("--smooth", action="store_true",
                           help="Use smooth trajectory planning with ModernRobotics")
        parser.add_argument("--step", action="store_true", 
                           help="Use step-based movement (default behavior)")
        parser.add_argument("--pause-between", type=float, default=2.0,
                           help="Pause between configurations (seconds)")
        parser.add_argument("--pause-after", type=float, default=3.0,
                           help="Pause after each configuration movement (seconds)")
        parser.add_argument("--duration", "-d", type=float,
                           help="Trajectory duration in seconds (auto-calculated if not specified)")
        parser.add_argument("--max-velocity", type=float, default=0.3,
                           help="Maximum joint velocity for trajectory planning (default: 0.3 rad/s)")
        parser.add_argument("--waypoints", type=int,
                           help="Number of trajectory waypoints (auto-calculated if not specified)")
        parser.add_argument("--no-adaptive-waypoints", action="store_true",
                           help="Disable adaptive waypoint calculation based on joint displacement")
        
        # Only parse known arguments to avoid conflicts
        args, unknown = parser.parse_known_args()
        
        # Apply execution options from sequence definition (can be overridden by command line)
        use_trajectory_from_options = execution_options.get("smooth", False)
        
        # Determine execution mode (command line overrides sequence options)
        if args.step:
            use_trajectory = False
            print("📐 Using STEP-BASED movement (command line override)")
        elif args.smooth:
            use_trajectory = True
            print("🎬 Using SMOOTH trajectory planning (command line override)")
        elif use_trajectory_from_options:
            use_trajectory = True
            print("🎬 Using SMOOTH trajectory planning (from sequence execution_options)")
        else:
            # Default behavior: use step-based movement (more predictable)
            use_trajectory = False
            print("📐 Using STEP-BASED movement (default)")
            if TRAJECTORY_AVAILABLE:
                print("💡 Tip: Use --smooth for smooth trajectory planning")
        
        print(f"🎯 Executing predefined sequence: {sequence_name}")
        if sequence_data.get("description"):
            print(f"📝 Description: {sequence_data['description']}")
        print(f"📋 Configurations: {' → '.join(configs)}")
        if execution_options:
            print(f"⚙️  Execution options: {execution_options}")
        print(f"🔧 Left arm ID: {args.left_arm_id} (5A68011258)")
        print(f"🔧 Right arm ID: {args.right_arm_id} (5A68009540)")
        
        # Get timing parameters from execution_options or command line (command line takes precedence)
        pause_between = execution_options.get("pause_between", args.pause_between)
        pause_after = execution_options.get("pause_after", args.pause_after)
        
        # Show timing configuration
        if execution_options.get("pause_between") is not None or execution_options.get("pause_after") is not None:
            print(f"⏱️  Timing from sequence config: pause_between={pause_between}s, pause_after={pause_after}s")
        
        executor = SequentialRobotExecutor(
            server_url=args.server,
            skip_init=True, 
            left_arm_id=args.left_arm_id, 
            right_arm_id=args.right_arm_id
        )
        success = executor.execute_sequence(
            configs,
            pause_between=pause_between,
            pause_after_each=pause_after,
            use_trajectory=use_trajectory,
            trajectory_duration=args.duration,
            max_velocity=args.max_velocity,
            num_waypoints=args.waypoints,
            adaptive_waypoints=not args.no_adaptive_waypoints
        )
        
        if success:
            print(f"\n🎉 Predefined sequence '{sequence_name}' completed successfully!")
        else:
            print(f"\n❌ Predefined sequence '{sequence_name}' failed!")
        sys.exit(0 if success else 1)
    
    # Show available predefined sequences
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]):
        print("🤖 Sequential Robot Configuration Executor")
        print("=" * 50)
        print("\nPredefined sequences:")
        for name, seq_data in PREDEFINED_SEQUENCES.items():
            configs = seq_data["configurations"]
            description = seq_data.get("description", "")
            execution_options = seq_data.get("execution_options", {})
            
            print(f"  • {name}: {' → '.join(configs)}")
            if description:
                print(f"    Description: {description}")
            if execution_options:
                print(f"    Options: {execution_options}")
        
        print("\nUsage:")
        print(f"  python3 {sys.argv[0]} standoff_to_dispensing")
        print(f"  python3 {sys.argv[0]} full_lab_procedure")
        print(f"  python3 {sys.argv[0]} multi_color_dispensing_workflow")
        print(f"  python3 {sys.argv[0]} beaker_pickup_sequence --left-arm-id 0 --right-arm-id 2")
        print(f"  python3 {sys.argv[0]} config1 config2 config3 [options]")
        print("\nFor full options: python3 sequential_execute.py --help")
        print("\nArm ID defaults: Left arm = 0 (5A68011258), Right arm = 2 (5A68009540)")
        print("Trajectory mode: Smooth with adaptive waypoints (default)")
        sys.exit(0)
    
    # Run with command line arguments
    main()
