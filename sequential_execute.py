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

# Import the existing functionality from execute_rules.py
sys.path.append(str(Path(__file__).parent))
from execute_rules import PhosphobotJointController, load_configuration, prepare_arm_configuration

class SequentialRobotExecutor:
    """Execute multiple robot configurations in sequence."""
    
    def __init__(self, server_url: str = "http://localhost:80", skip_init: bool = True, 
                 left_arm_id: int = 3, right_arm_id: int = 2):
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
    
    def execute_configuration(self, config_name: str, pause_after: float = 3.0):
        """Execute a single configuration with optional pause.
        
        Enhanced to support:
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
            
            # Move configured arms
            if has_left_arm and left_joints:
                print(f"Left arm (ID {self.left_arm_id}) joints: {[f'{j:.3f}' for j in left_joints]}")
                self.controller.write_joint_positions(self.left_arm_id, left_joints)
                time.sleep(1)
            else:
                print(f"Left arm (ID {self.left_arm_id}): keeping current position")
            
            if has_right_arm and right_joints:
                print(f"Right arm (ID {self.right_arm_id}) joints: {[f'{j:.3f}' for j in right_joints]}")
                self.controller.write_joint_positions(self.right_arm_id, right_joints)
                time.sleep(1)
            else:
                print(f"Right arm (ID {self.right_arm_id}): keeping current position")
            
            # Pause to allow movement completion
            if pause_after > 0:
                print(f"\n⏱️  Pausing {pause_after}s to complete movement...")
                time.sleep(pause_after)
            
            # Read final positions for moved arms
            print("\n📖 Reading final joint positions...")
            if has_left_arm:
                self.controller.read_joint_positions(self.left_arm_id)
            if has_right_arm:
                self.controller.read_joint_positions(self.right_arm_id)
            
            print(f"\n✅ Successfully completed: {config.get('name', config_name)}")
            return True
            
        except Exception as e:
            print(f"❌ Error executing configuration '{config_name}': {e}")
            return False
    
    def execute_sequence(self, config_names: list[str], pause_between: float = 2.0, pause_after_each: float = 3.0):
        """Execute a sequence of configurations."""
        print(f"🤖 Starting sequential execution of {len(config_names)} configurations")
        print("=" * 70)
        
        success_count = 0
        
        try:
            self.initialize()
            
            for i, config_name in enumerate(config_names, 1):
                print(f"\n🔄 Step {i}/{len(config_names)}: {config_name}")
                
                success = self.execute_configuration(config_name, pause_after_each)
                
                if success:
                    success_count += 1
                else:
                    print(f"❌ Failed to execute step {i}, aborting sequence")
                    break
                
                # Pause between configurations (except after the last one)
                if i < len(config_names) and pause_between > 0:
                    print(f"\n⏳ Pausing {pause_between}s before next configuration...")
                    time.sleep(pause_between)
            
            print(f"\n🎉 Sequence completed! {success_count}/{len(config_names)} configurations executed successfully")
            return success_count == len(config_names)
            
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
    parser.add_argument("--left-arm-id", type=int, default=3,
                       help="Left arm robot ID (default: 3 for 5A68011258)")
    parser.add_argument("--right-arm-id", type=int, default=2,
                       help="Right arm robot ID (default: 2 for 5A68009540)")
    
    args = parser.parse_args()
    
    # Determine initialization setting
    skip_init = not args.init
    if args.init:
        print("⚠️  Robot initialization ENABLED - use with caution!")
    else:
        print("✅ Robot initialization DISABLED by default (safer)")
    
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
        pause_after_each=args.pause_after
    )
    
    if success:
        print(f"\n🎉 All configurations executed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Sequence execution failed!")
        sys.exit(1)

# Load predefined sequences from JSON file
def load_predefined_sequences():
    """Load predefined sequences from JSON file."""
    sequences_file = Path("temp_rules/sequential_sequences.json")
    
    if not sequences_file.exists():
        print(f"⚠️  Sequences file not found: {sequences_file}")
        return {}
    
    try:
        with open(sequences_file, 'r') as f:
            data = json.load(f)
        
        # Convert to simple dict format expected by the rest of the code
        sequences = {}
        for name, seq_data in data.get("predefined_sequences", {}).items():
            sequences[name] = seq_data["configurations"]
        
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
        configs = PREDEFINED_SEQUENCES[sequence_name]
        
        # Parse additional arguments for predefined sequences
        parser = argparse.ArgumentParser(description=f"Execute predefined sequence: {sequence_name}")
        parser.add_argument("sequence", help="Predefined sequence name")
        parser.add_argument("--left-arm-id", type=int, default=3,
                           help="Left arm robot ID (default: 3 for 5A68011258)")
        parser.add_argument("--right-arm-id", type=int, default=2,
                           help="Right arm robot ID (default: 2 for 5A68009540)")
        parser.add_argument("--server", default="http://localhost:80",
                           help="Phosphobot server URL")
        
        # Only parse known arguments to avoid conflicts
        args, unknown = parser.parse_known_args()
        
        print(f"🎯 Executing predefined sequence: {sequence_name}")
        print(f"📋 Configurations: {' → '.join(configs)}")
        print(f"🔧 Left arm ID: {args.left_arm_id} (5A68011258)")
        print(f"🔧 Right arm ID: {args.right_arm_id} (5A68009540)")
        
        executor = SequentialRobotExecutor(
            server_url=args.server,
            skip_init=True, 
            left_arm_id=args.left_arm_id, 
            right_arm_id=args.right_arm_id
        )
        success = executor.execute_sequence(configs)
        
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
        for name, configs in PREDEFINED_SEQUENCES.items():
            print(f"  • {name}: {' → '.join(configs)}")
        
        print("\nUsage:")
        print(f"  python3 {sys.argv[0]} standoff_to_dispensing")
        print(f"  python3 {sys.argv[0]} full_lab_procedure")
        print(f"  python3 {sys.argv[0]} beaker_pickup_sequence --left-arm-id 3 --right-arm-id 2")
        print(f"  python3 {sys.argv[0]} config1 config2 config3 [options]")
        print("\nFor full options: python3 sequential_execute.py --help")
        print("\nArm ID defaults: Left arm = 3 (5A68011258), Right arm = 2 (5A68009540)")
        sys.exit(0)
    
    # Run with command line arguments
    main()
