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
                 left_arm_id: int = 0, right_arm_id: int = 2):
        self.server_url = server_url
        self.skip_init = skip_init
        self.left_arm_id = left_arm_id
        self.right_arm_id = right_arm_id
        self.controller = None
        
    def initialize(self):
        """Initialize the robot controller."""
        self.controller = PhosphobotJointController(self.server_url)
        time.sleep(1)
        
        print(f"🔧 Left arm ID: {self.left_arm_id} (5A68011258)")
        print(f"🔧 Right arm ID: {self.right_arm_id} (5A68009540)")
        
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
            r"squeeze.*(\d+\.?\d*)"
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
                print("❌ Failed to read current right arm position")
                return False
            
            # Create squeeze position (modify only j6 to 0.3)
            squeeze_joints = current_right_joints.copy()
            squeeze_joints[5] = 0.3  # j6 = 0.3 for squeeze
            
            print(f"🤏 Squeezing: Right arm j6 from {current_right_joints[5]:.3f} to 0.300")
            
            # Execute squeeze
            result = self.controller.write_joint_positions(self.right_arm_id, squeeze_joints)
            if result is None:
                print("❌ Failed to execute squeeze")
                return False
            
            # Hold squeeze for specified duration
            print(f"⏸️  Holding squeeze for {duration} seconds...")
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during squeeze operation: {e}")
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
                
            if has_right_arm:
                current_right_joints = self.controller.get_current_joint_angles(self.right_arm_id)
            
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
    parser.add_argument("--left-arm-id", type=int, default=0,
                       help="Left arm robot ID (default: 0 for 5A68011258)")
    parser.add_argument("--right-arm-id", type=int, default=2,
                       help="Right arm robot ID (default: 2 for 5A68009540)")
    
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
def load_predefined_sequences():
    """Load predefined sequences from JSON file with execution options support."""
    sequences_file = Path("temp_rules/sequential_sequences.json")
    
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
    # Check for predefined sequences
    if len(sys.argv) > 1 and sys.argv[1] in PREDEFINED_SEQUENCES:
        sequence_name = sys.argv[1]
        sequence_data = PREDEFINED_SEQUENCES[sequence_name]
        configs = sequence_data["configurations"]
        execution_options = sequence_data.get("execution_options", {})
        
        # Parse additional arguments for predefined sequences
        parser = argparse.ArgumentParser(description=f"Execute predefined sequence: {sequence_name}")
        parser.add_argument("sequence", help="Predefined sequence name")
        parser.add_argument("--left-arm-id", type=int, default=0,
                           help="Left arm robot ID (default: 0 for 5A68011258)")
        parser.add_argument("--right-arm-id", type=int, default=2,
                           help="Right arm robot ID (default: 2 for 5A68009540)")
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
        
        executor = SequentialRobotExecutor(
            server_url=args.server,
            skip_init=True, 
            left_arm_id=args.left_arm_id, 
            right_arm_id=args.right_arm_id
        )
        success = executor.execute_sequence(
            configs,
            pause_between=args.pause_between,
            pause_after_each=args.pause_after,
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
