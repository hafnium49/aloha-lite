#!/usr/bin/env python3
"""
ADAPTED from demo2rules.py output
Dataset : Hafnium49/aloha_lite  (episode 1)
SHA‑256 : fc327fe0e0
Using direct phosphobot joint control APIs
"""

import sys
import os
import time
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
    success = execute_learned_sequence()
    if success:
        print("\n✅ Learned sequence executed successfully!")
    else:
        print("\n❌ Failed to execute learned sequence!")
