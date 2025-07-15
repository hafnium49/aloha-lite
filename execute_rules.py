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
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
        print("🔌 Controller disconnected")

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

def execute_configuration(config_name: str, skip_init: bool = True):
    """Execute a specific configuration by loading it from JSON."""
    
    print(f"🤖 Loading and executing configuration: {config_name}")
    print("=" * 60)
    
    try:
        # Load configuration
        config = load_configuration(config_name)
        
        # Validate configuration structure
        if 'configuration' not in config:
            raise ValueError("Invalid configuration: missing 'configuration' section")
        
        config_data = config['configuration']
        
        if 'left_arm' not in config_data or 'right_arm' not in config_data:
            raise ValueError("Invalid configuration: missing arm configuration")
        
        # Extract joint positions
        left_joints = list(config_data['left_arm']['joints'].values())
        right_joints = list(config_data['right_arm']['joints'].values())
        
        print(f"📋 Configuration: {config.get('name', 'Unknown')}")
        print(f"📝 Description: {config.get('description', 'No description')}")
        print(f"📊 Source: {config.get('source', {}).get('dataset', 'Unknown')}")
        
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
            
            print(f"\n🎯 Moving to configuration: {config.get('name', config_name)}")
            print(f"Left arm joints: {[f'{j:.3f}' for j in left_joints]}")
            print(f"Right arm joints: {[f'{j:.3f}' for j in right_joints]}")
            
            # Move left arm (robot_id=0)
            controller.write_joint_positions(0, left_joints)
            time.sleep(1)
            
            # Move right arm (robot_id=1)
            controller.write_joint_positions(1, right_joints)
            time.sleep(3)
            
            print("\n📖 Reading final joint positions...")
            controller.read_joint_positions(0)
            controller.read_joint_positions(1)
            
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
    
    args = parser.parse_args()
    
    # Determine initialization setting
    if args.init:
        skip_init = False
        print("⚠️  Robot initialization ENABLED - use with caution!")
    else:
        skip_init = True
        if not args.no_init:
            print("✅ Robot initialization DISABLED by default (safer)")
    
    if args.config:
        # Execute specific configuration
        success = execute_configuration(args.config, skip_init=skip_init)
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
            print(f"  python3 execute_rules.py --config standoff_configuration_stage1")
            print(f"  python3 execute_rules.py --config dispensing_water_to_beaker")
            print(f"  python3 execute_rules.py --config standoff_configuration_stage1 --init  # Enable init (risky)")
            print(f"  python3 execute_rules.py --legacy")
        else:
            print("  No configuration files found.")
            print("  Use --legacy to run the original demo.")
