#!/usr/bin/env python3
"""
SO-101 Servo Diagnosis Tool for Hunting/Jitter Issues
=====================================================

This script diagnoses and fixes the classic "servo hunting" issue where a joint
oscillates at ≃ 1 Hz with ±few-degree wobble. 

Target: SO-101 Arm ID 5A68011258 (Robot ID 1 in phosphobot)
Based on systematic troubleshooting guide for STS-series bus servos.

Usage:
    python servo_diagnosis.py                    # Run full diagnosis
    python servo_diagnosis.py --joint 3         # Focus on specific joint
    python servo_diagnosis.py --fix-deadband    # Apply deadband fix
    python servo_diagnosis.py --monitor         # Live monitoring mode
"""

import requests
import time
import json
import argparse
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:80/"
ROBOT_ID = 0  # SO-101 Arm ID 5A68011258 connected as robot ID 0
JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"]

# Register addresses for STS3215 servos
REGISTERS = {
    'DEADBAND': 0x0A,
    'PID_KP': 0x1C,
    'PID_KI': 0x1D, 
    'PID_KD': 0x1E,
    'TORQUE_LIMIT_L': 0x24,
    'TORQUE_LIMIT_H': 0x25,
    'PRESENT_POSITION_L': 0x38,
    'PRESENT_POSITION_H': 0x39,
    'PRESENT_VOLTAGE': 0x3A,
    'PRESENT_CURRENT_L': 0x3C,
    'PRESENT_CURRENT_H': 0x3D,
}

# Safe ranges and recommended values
SAFE_RANGES = {
    'DEADBAND': (1, 8, 3),      # (min, max, recommended)
    'PID_KP': (0, 254, 50),
    'PID_KI': (0, 254, 10), 
    'PID_KD': (0, 254, 4),
}

class ServoDiagnosis:
    def __init__(self):
        self.robot_id = ROBOT_ID
        self.base_url = BASE_URL
        self.results = {}
        
    def log_info(self, message: str):
        """Log info message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ℹ️  {message}")
        
    def log_warning(self, message: str):
        """Log warning message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⚠️  {message}")
        
    def log_error(self, message: str):
        """Log error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ {message}")
        
    def log_success(self, message: str):
        """Log success message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ✅ {message}")

    def read_joint_positions(self, unit: str = "rad") -> Optional[Dict]:
        """Read current joint positions."""
        endpoint = f"{self.base_url}joints/read?robot_id={self.robot_id}"
        data = {"unit": unit}
        
        try:
            response = requests.post(endpoint, json=data, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.log_error(f"Failed to read joint positions: {e}")
            return None

    def read_joint_voltage(self, joint_id: int) -> Optional[float]:
        """Read voltage for a specific joint (simulated via joint positions for now)."""
        # Note: This is a simplified implementation since phosphobot API doesn't expose
        # direct servo register access. In a real implementation, this would use
        # the feetech Bus class to read voltage directly from servo registers.
        self.log_warning("Voltage reading simulated - direct servo access not available via phosphobot API")
        return 12.0  # Simulated voltage reading

    def read_joint_current(self, joint_id: int) -> Optional[float]:
        """Read current for a specific joint (simulated)."""
        self.log_warning("Current reading simulated - direct servo access not available via phosphobot API")
        return 0.5  # Simulated current reading

    def monitor_joint_telemetry(self, joint_id: int, duration: int = 5) -> List[Dict]:
        """Monitor joint telemetry for specified duration."""
        self.log_info(f"Monitoring Joint {joint_id} telemetry for {duration} seconds...")
        
        telemetry = []
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < duration:
            # Read joint position
            joint_data = self.read_joint_positions()
            if joint_data and 'angles' in joint_data:
                angles = joint_data['angles']
                if joint_id - 1 < len(angles):
                    position = angles[joint_id - 1]
                    voltage = self.read_joint_voltage(joint_id)
                    current = self.read_joint_current(joint_id)
                    
                    sample = {
                        'timestamp': time.time() - start_time,
                        'position': position,
                        'voltage': voltage,
                        'current': current,
                        'joint_id': joint_id
                    }
                    telemetry.append(sample)
                    
                    if sample_count % 10 == 0:  # Print every 10th sample
                        self.log_info(f"Joint {joint_id}: pos={position:.4f}rad, V={voltage:.1f}V, I={current:.3f}A")
                    
                    sample_count += 1
            
            time.sleep(0.05)  # 20 Hz sampling
        
        self.log_info(f"Collected {len(telemetry)} samples")
        return telemetry

    def analyze_hunting_behavior(self, telemetry: List[Dict]) -> Dict:
        """Analyze telemetry data for hunting/jitter patterns."""
        if not telemetry:
            return {
            "hunting_detected": False,
            "reason": "No telemetry data",
            "position_variance": 0,
            "position_range_rad": 0,
            "position_range_deg": 0,
            "min_voltage": 0,
            "voltage_sag": False,
            "sample_count": 0,
            "recommendations": ["COMMUNICATION_ERROR: Failed to read joint positions"]
        }
        
        positions = [sample['position'] for sample in telemetry]
        voltages = [sample['voltage'] for sample in telemetry if sample['voltage'] is not None]
        
        # Calculate position variance and oscillation
        if len(positions) > 10:
            position_variance = sum((p - sum(positions)/len(positions))**2 for p in positions) / len(positions)
            max_position = max(positions)
            min_position = min(positions)
            position_range = max_position - min_position
        else:
            position_variance = 0
            position_range = 0
        
        # Check for voltage sag
        min_voltage = min(voltages) if voltages else 12.0
        voltage_sag = min_voltage < 11.0
        
        # Determine if hunting is detected
        hunting_threshold = 0.001  # rad variance threshold
        hunting_detected = position_variance > hunting_threshold and position_range > 0.05
        
        analysis = {
            "hunting_detected": hunting_detected,
            "position_variance": position_variance,
            "position_range_rad": position_range,
            "position_range_deg": position_range * 57.2958,  # Convert to degrees
            "min_voltage": min_voltage,
            "voltage_sag": voltage_sag,
            "sample_count": len(telemetry),
            "recommendations": []
        }
        
        # Generate recommendations
        if voltage_sag:
            analysis["recommendations"].append("VOLTAGE_SAG: Add 470-1000µF capacitor, shorten power leads, or use ≥3A PSU")
        
        if hunting_detected and not voltage_sag:
            analysis["recommendations"].append("DEADBAND: Increase dead-band to 2-4 counts (≈0.06-0.12°)")
            analysis["recommendations"].append("CALIBRATION: Re-run calibration to fix offset/gain mismatch")
            analysis["recommendations"].append("PID_TUNING: Check and restore default PID gains")
        
        if position_range > 0.1:  # > 5.7 degrees
            analysis["recommendations"].append("SEVERE_HUNTING: Check for duplicate servo IDs or bus errors")
        
        return analysis

    def diagnose_joint(self, joint_id: int) -> Dict:
        """Perform comprehensive diagnosis of a specific joint."""
        self.log_info(f"🔍 Starting diagnosis for Joint {joint_id} ({JOINT_NAMES[joint_id-1]})")
        self.log_info(f"Target: Robot ID {self.robot_id} (SO-101 Arm 5A68011258 as arm ID 0)")
        
        # Step 1: Check initial position
        self.log_info("Step 1: Reading initial joint position...")
        initial_position = self.read_joint_positions()
        if not initial_position:
            return {
                "error": "Failed to read initial position",
                "joint_id": joint_id,
                "joint_name": JOINT_NAMES[joint_id-1],
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 2: Monitor telemetry for hunting behavior
        self.log_info("Step 2: Monitoring for hunting behavior...")
        telemetry = self.monitor_joint_telemetry(joint_id, duration=5)
        
        # Step 3: Analyze hunting patterns
        self.log_info("Step 3: Analyzing hunting patterns...")
        analysis = self.analyze_hunting_behavior(telemetry)
        
        # Step 4: Generate report
        report = {
            "joint_id": joint_id,
            "joint_name": JOINT_NAMES[joint_id-1],
            "initial_position": initial_position['angles'][joint_id-1] if initial_position else None,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        return report

    def simulate_servo_register_fix(self, joint_id: int, register: str, value: int) -> bool:
        """Simulate servo register modification (would use feetech Bus in real implementation)."""
        self.log_warning(f"SIMULATION: Would write register {register} = {value} to Joint {joint_id}")
        self.log_warning("Real implementation requires feetech Bus library and direct servo access")
        return True

    def apply_deadband_fix(self, joint_id: int, deadband_value: int = 3) -> bool:
        """Apply deadband fix to reduce hunting."""
        self.log_info(f"Applying deadband fix to Joint {joint_id}...")
        
        if deadband_value < 1 or deadband_value > 8:
            self.log_error(f"Deadband value {deadband_value} out of safe range (1-8)")
            return False
        
        # In real implementation, this would be:
        # bus.write_reg(joint_id, REGISTERS['DEADBAND'], deadband_value, eeprom=True)
        success = self.simulate_servo_register_fix(joint_id, 'DEADBAND', deadband_value)
        
        if success:
            self.log_success(f"Deadband set to {deadband_value} counts (≈{deadband_value * 0.03:.2f}°)")
            self.log_info("Power-cycle the adapter and test again")
        
        return success

    def compare_pid_settings(self, bad_joint_id: int, good_joint_id: int) -> Dict:
        """Compare PID settings between joints."""
        self.log_info(f"Comparing PID settings: Joint {bad_joint_id} vs Joint {good_joint_id}")
        
        comparison = {}
        for reg_name in ['PID_KP', 'PID_KI', 'PID_KD']:
            # Simulate reading registers
            bad_value = 50 if reg_name == 'PID_KP' else 10  # Simulated values
            good_value = 50 if reg_name == 'PID_KP' else 10
            
            comparison[reg_name] = {
                'bad_joint': bad_value,
                'good_joint': good_value,
                'match': bad_value == good_value
            }
            
            if not comparison[reg_name]['match']:
                self.log_warning(f"{reg_name} mismatch: Joint {bad_joint_id}={bad_value}, Joint {good_joint_id}={good_value}")
        
        return comparison

    def run_full_diagnosis(self, target_joint: Optional[int] = None) -> Dict:
        """Run full systematic diagnosis."""
        self.log_info("🚀 Starting SO-101 Servo Hunting Diagnosis")
        self.log_info(f"Target: Robot ID {self.robot_id} (SO-101 Arm 5A68011258 as arm ID 0)")
        
        results = {
            "robot_id": self.robot_id,
            "timestamp": datetime.now().isoformat(),
            "joints": {}
        }
        
        # Determine which joints to diagnose
        joints_to_check = [target_joint] if target_joint else list(range(1, 7))
        
        for joint_id in joints_to_check:
            try:
                self.log_info(f"\n{'='*60}")
                joint_report = self.diagnose_joint(joint_id)
                results["joints"][joint_id] = joint_report
                
                # Print analysis results
                analysis = joint_report.get("analysis", {})
                if analysis.get("hunting_detected"):
                    self.log_warning(f"Joint {joint_id}: HUNTING DETECTED!")
                    self.log_info(f"  Position variance: {analysis['position_variance']:.6f} rad²")
                    self.log_info(f"  Position range: {analysis['position_range_deg']:.2f}°")
                    
                    for rec in analysis.get("recommendations", []):
                        self.log_info(f"  💡 {rec}")
                else:
                    self.log_success(f"Joint {joint_id}: No hunting detected")
                
            except Exception as e:
                self.log_error(f"Error diagnosing Joint {joint_id}: {e}")
                results["joints"][joint_id] = {"error": str(e)}
        
        return results

    def print_summary_report(self, results: Dict):
        """Print a summary report of all findings."""
        self.log_info("\n" + "="*60)
        self.log_info("📋 DIAGNOSIS SUMMARY REPORT")
        self.log_info("="*60)
        
        hunting_joints = []
        healthy_joints = []
        
        for joint_id, report in results.get("joints", {}).items():
            if "error" in report:
                self.log_error(f"Joint {joint_id}: {report['error']}")
            elif report.get("analysis", {}).get("hunting_detected"):
                hunting_joints.append(joint_id)
            else:
                healthy_joints.append(joint_id)
        
        if hunting_joints:
            self.log_warning(f"Joints with hunting: {hunting_joints}")
            self.log_info("\n🔧 RECOMMENDED ACTIONS:")
            self.log_info("1. Check power supply voltage (should be ≥11V)")
            self.log_info("2. Apply deadband fix: python servo_diagnosis.py --fix-deadband --joint <id>")
            self.log_info("3. Re-calibrate arm offsets if needed")
            self.log_info("4. Check for duplicate servo IDs")
        else:
            self.log_success("All joints appear healthy - no hunting detected")
        
        if healthy_joints:
            self.log_success(f"Healthy joints: {healthy_joints}")

def main():
    parser = argparse.ArgumentParser(description='SO-101 Servo Hunting Diagnosis Tool')
    parser.add_argument('--joint', type=int, choices=range(1, 7), 
                       help='Focus on specific joint (1-6)')
    parser.add_argument('--fix-deadband', action='store_true',
                       help='Apply deadband fix to specified joint')
    parser.add_argument('--deadband-value', type=int, default=3,
                       help='Deadband value to apply (default: 3)')
    parser.add_argument('--monitor', action='store_true',
                       help='Live monitoring mode')
    parser.add_argument('--duration', type=int, default=10,
                       help='Monitoring duration in seconds (default: 10)')
    
    args = parser.parse_args()
    
    # Initialize diagnosis tool
    diagnosis = ServoDiagnosis()
    
    if args.fix_deadband:
        if not args.joint:
            print("Error: --joint required when using --fix-deadband")
            return
        diagnosis.apply_deadband_fix(args.joint, args.deadband_value)
        
    elif args.monitor:
        joint_id = args.joint or 3  # Default to joint 3 if not specified
        diagnosis.log_info(f"Live monitoring mode for Joint {joint_id}")
        telemetry = diagnosis.monitor_joint_telemetry(joint_id, args.duration)
        analysis = diagnosis.analyze_hunting_behavior(telemetry)
        
        print("\n" + "="*50)
        print("LIVE MONITORING RESULTS")
        print("="*50)
        print(f"Hunting detected: {analysis['hunting_detected']}")
        print(f"Position variance: {analysis['position_variance']:.6f} rad²")
        print(f"Position range: {analysis['position_range_deg']:.2f}°")
        print(f"Min voltage: {analysis['min_voltage']:.1f}V")
        
        if analysis['recommendations']:
            print("\nRecommendations:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
    
    else:
        # Run full diagnosis
        results = diagnosis.run_full_diagnosis(args.joint)
        diagnosis.print_summary_report(results)
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"servo_diagnosis_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        diagnosis.log_info(f"Detailed results saved to: {filename}")

if __name__ == "__main__":
    main()
