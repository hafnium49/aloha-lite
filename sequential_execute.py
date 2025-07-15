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
from execute_rules import PhosphobotJointController, load_configuration

class SequentialRobotExecutor:
    """Execute multiple robot configurations in sequence."""
    
    def __init__(self, server_url: str = "http://localhost:80", skip_init: bool = True):
        self.server_url = server_url
        self.skip_init = skip_init
        self.controller = None
        
    def initialize(self):
        """Initialize the robot controller."""
        self.controller = PhosphobotJointController(self.server_url)
        time.sleep(1)
        
        if not self.skip_init:
            print("\n🔧 Initializing robots...")
            self.controller.initialize_robot()
            time.sleep(2)
        else:
            print("\n⚠️  Skipping robot initialization to prevent collisions")
    
    def execute_configuration(self, config_name: str, pause_after: float = 3.0):
        """Execute a single configuration with optional pause."""
        print(f"\n🎯 Executing configuration: {config_name}")
        print("=" * 50)
        
        try:
            # Load configuration
            config = load_configuration(config_name)
            
            # Validate configuration structure
            if 'configuration' not in config:
                raise ValueError(f"Invalid configuration '{config_name}': missing 'configuration' section")
            
            config_data = config['configuration']
            
            if 'left_arm' not in config_data or 'right_arm' not in config_data:
                raise ValueError(f"Invalid configuration '{config_name}': missing arm configuration")
            
            # Extract joint positions
            left_joints = list(config_data['left_arm']['joints'].values())
            right_joints = list(config_data['right_arm']['joints'].values())
            
            print(f"📋 Configuration: {config.get('name', 'Unknown')}")
            print(f"📝 Description: {config.get('description', 'No description')}")
            print(f"📊 Source: {config.get('source', {}).get('dataset', config.get('source', {}).get('type', 'Unknown'))}")
            
            print(f"\n🎯 Moving to: {config.get('name', config_name)}")
            print(f"Left arm joints: {[f'{j:.3f}' for j in left_joints]}")
            print(f"Right arm joints: {[f'{j:.3f}' for j in right_joints]}")
            
            # Move left arm (robot_id=0)
            self.controller.write_joint_positions(0, left_joints)
            time.sleep(1)
            
            # Move right arm (robot_id=1)
            self.controller.write_joint_positions(1, right_joints)
            
            # Pause to allow movement completion
            if pause_after > 0:
                print(f"\n⏱️  Pausing {pause_after}s to complete movement...")
                time.sleep(pause_after)
            
            # Read final positions
            print("\n📖 Reading final joint positions...")
            self.controller.read_joint_positions(0)
            self.controller.read_joint_positions(1)
            
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
    
    args = parser.parse_args()
    
    # Determine initialization setting
    skip_init = not args.init
    if args.init:
        print("⚠️  Robot initialization ENABLED - use with caution!")
    else:
        print("✅ Robot initialization DISABLED by default (safer)")
    
    # Execute sequence
    executor = SequentialRobotExecutor(args.server, skip_init)
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

# Predefined sequences for common tasks
PREDEFINED_SEQUENCES = {
    "standoff_to_dispensing": [
        "standoff_configuration_stage1",
        "dispensing_water_to_beaker"
    ],
    "dispensing_to_standoff": [
        "dispensing_water_to_beaker",
        "standoff_configuration_stage1"
    ],
    "full_lab_procedure": [
        "standoff_configuration_stage1",
        "dispensing_water_to_beaker",
        "standoff_configuration_stage1"
    ]
}

if __name__ == "__main__":
    # Check for predefined sequences
    if len(sys.argv) > 1 and sys.argv[1] in PREDEFINED_SEQUENCES:
        sequence_name = sys.argv[1]
        configs = PREDEFINED_SEQUENCES[sequence_name]
        
        print(f"🎯 Executing predefined sequence: {sequence_name}")
        print(f"📋 Configurations: {' → '.join(configs)}")
        
        executor = SequentialRobotExecutor(skip_init=True)
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
        print(f"  python3 {sys.argv[0]} config1 config2 config3 [options]")
        print("\nFor full options: python3 sequential_execute.py --help")
        sys.exit(0)
    
    # Run with command line arguments
    main()
