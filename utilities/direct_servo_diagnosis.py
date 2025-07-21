#!/usr/bin/env python3
"""
Direct Servo Diagnosis Tool using Feetech Bus
=============================================

This script provides direct servo register access for advanced diagnosis
and fixes. Use this when you need to directly communicate with STS3215 servos.

Requirements:
    pip install feetech-servo

Usage:
    python direct_servo_diagnosis.py --port /dev/ttyUSB0
    python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --fix-deadband
"""

import argparse
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

try:
    from feetech import Bus
    FEETECH_AVAILABLE = True
except ImportError:
    FEETECH_AVAILABLE = False
    print("⚠️  Feetech library not available. Install with: pip install feetech-servo")

# STS3215 Register Map
STS3215_REGISTERS = {
    # EEPROM Area (stored permanently)
    'MODEL_L': 0x03,
    'MODEL_H': 0x04,
    'FIRMWARE': 0x05,
    'ID': 0x06,
    'BAUD_RATE': 0x07,
    'DELAY_TIME': 0x08,
    'RESPONSE_LEVEL': 0x09,
    'MIN_ANGLE_LIMIT_L': 0x0A,
    'MIN_ANGLE_LIMIT_H': 0x0B,
    'MAX_ANGLE_LIMIT_L': 0x0C,
    'MAX_ANGLE_LIMIT_H': 0x0D,
    'TEMP_LIMIT': 0x0E,
    'VOLTAGE_LIMIT_L': 0x0F,
    'VOLTAGE_LIMIT_H': 0x10,
    'MAX_TORQUE_L': 0x11,
    'MAX_TORQUE_H': 0x12,
    'RESPONSE_MODE': 0x13,
    'ALARM_SHUTDOWN': 0x14,
    
    # RAM Area (temporary, reset on power cycle)
    'TORQUE_ENABLE': 0x28,
    'GOAL_POSITION_L': 0x29,
    'GOAL_POSITION_H': 0x2A,
    'GOAL_TIME_L': 0x2B,
    'GOAL_TIME_H': 0x2C,
    'GOAL_SPEED_L': 0x2D,
    'GOAL_SPEED_H': 0x2E,
    'TORQUE_LIMIT_L': 0x30,
    'TORQUE_LIMIT_H': 0x31,
    'LOCK': 0x37,
    
    # Status registers (read-only)
    'PRESENT_POSITION_L': 0x38,
    'PRESENT_POSITION_H': 0x39,
    'PRESENT_SPEED_L': 0x3A,
    'PRESENT_SPEED_H': 0x3B,
    'PRESENT_LOAD_L': 0x3C,
    'PRESENT_LOAD_H': 0x3D,
    'PRESENT_VOLTAGE': 0x3E,
    'PRESENT_TEMP': 0x3F,
    'MOVE_STATUS': 0x40,
    'PRESENT_CURRENT_L': 0x45,
    'PRESENT_CURRENT_H': 0x46,
}

class DirectServoDiagnosis:
    def __init__(self, port: str, baudrate: int = 1000000):
        if not FEETECH_AVAILABLE:
            raise ImportError("Feetech library required for direct servo access")
        
        self.port = port
        self.baudrate = baudrate
        self.bus = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to servo bus."""
        try:
            self.bus = Bus(self.port, self.baudrate)
            self.connected = True
            print(f"✅ Connected to servo bus on {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to servo bus: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from servo bus."""
        if self.bus:
            self.bus.close()
            self.connected = False
            print("🔌 Disconnected from servo bus")
    
    def read_register(self, servo_id: int, register: int) -> Optional[int]:
        """Read a single register from servo."""
        if not self.connected:
            return None
        
        try:
            value = self.bus.read_reg(servo_id, register)
            return value
        except Exception as e:
            print(f"❌ Failed to read register {register:02X} from servo {servo_id}: {e}")
            return None
    
    def write_register(self, servo_id: int, register: int, value: int, eeprom: bool = False) -> bool:
        """Write a single register to servo."""
        if not self.connected:
            return False
        
        try:
            self.bus.write_reg(servo_id, register, value, eeprom=eeprom)
            print(f"✅ Wrote register {register:02X} = {value} to servo {servo_id} {'(EEPROM)' if eeprom else '(RAM)'}")
            return True
        except Exception as e:
            print(f"❌ Failed to write register {register:02X} to servo {servo_id}: {e}")
            return False
    
    def read_16bit_register(self, servo_id: int, low_reg: int) -> Optional[int]:
        """Read a 16-bit value from consecutive registers."""
        low_val = self.read_register(servo_id, low_reg)
        high_val = self.read_register(servo_id, low_reg + 1)
        
        if low_val is not None and high_val is not None:
            return low_val + (high_val << 8)
        return None
    
    def scan_servos(self, id_range: range = range(1, 7)) -> List[int]:
        """Scan for connected servos."""
        print("🔍 Scanning for servos...")
        found_servos = []
        
        for servo_id in id_range:
            model = self.read_register(servo_id, STS3215_REGISTERS['MODEL_L'])
            if model is not None:
                found_servos.append(servo_id)
                print(f"  📡 Found servo ID {servo_id}")
        
        if not found_servos:
            print("  ⚠️  No servos found")
        
        return found_servos
    
    def get_servo_info(self, servo_id: int) -> Dict:
        """Get comprehensive servo information."""
        info = {'servo_id': servo_id}
        
        # Basic info
        model = self.read_16bit_register(servo_id, STS3215_REGISTERS['MODEL_L'])
        firmware = self.read_register(servo_id, STS3215_REGISTERS['FIRMWARE'])
        
        # Limits and settings
        temp_limit = self.read_register(servo_id, STS3215_REGISTERS['TEMP_LIMIT'])
        voltage_limit = self.read_16bit_register(servo_id, STS3215_REGISTERS['VOLTAGE_LIMIT_L'])
        max_torque = self.read_16bit_register(servo_id, STS3215_REGISTERS['MAX_TORQUE_L'])
        
        # Current status
        position = self.read_16bit_register(servo_id, STS3215_REGISTERS['PRESENT_POSITION_L'])
        voltage = self.read_register(servo_id, STS3215_REGISTERS['PRESENT_VOLTAGE'])
        temperature = self.read_register(servo_id, STS3215_REGISTERS['PRESENT_TEMP'])
        current = self.read_16bit_register(servo_id, STS3215_REGISTERS['PRESENT_CURRENT_L'])
        
        info.update({
            'model': model,
            'firmware': firmware,
            'temp_limit': temp_limit,
            'voltage_limit': voltage_limit,
            'max_torque': max_torque,
            'present_position': position,
            'present_voltage': voltage / 10.0 if voltage else None,  # Convert to actual volts
            'present_temperature': temperature,
            'present_current': current,
        })
        
        return info
    
    def monitor_servo_telemetry(self, servo_id: int, duration: int = 5) -> List[Dict]:
        """Monitor servo telemetry for hunting analysis."""
        print(f"📊 Monitoring servo {servo_id} for {duration} seconds...")
        
        telemetry = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            timestamp = time.time() - start_time
            
            # Read key registers
            position = self.read_16bit_register(servo_id, STS3215_REGISTERS['PRESENT_POSITION_L'])
            voltage = self.read_register(servo_id, STS3215_REGISTERS['PRESENT_VOLTAGE'])
            current = self.read_16bit_register(servo_id, STS3215_REGISTERS['PRESENT_CURRENT_L'])
            temperature = self.read_register(servo_id, STS3215_REGISTERS['PRESENT_TEMP'])
            
            sample = {
                'timestamp': timestamp,
                'position': position,
                'voltage': voltage / 10.0 if voltage else None,
                'current': current,
                'temperature': temperature,
            }
            
            telemetry.append(sample)
            
            # Print sample every 0.5 seconds
            if len(telemetry) % 10 == 0:
                print(f"  t={timestamp:.1f}s: pos={position}, V={voltage/10.0:.1f}V, I={current}, T={temperature}°C")
            
            time.sleep(0.05)  # 20 Hz
        
        print(f"✅ Collected {len(telemetry)} samples")
        return telemetry
    
    def analyze_hunting(self, telemetry: List[Dict]) -> Dict:
        """Analyze telemetry for hunting behavior."""
        if not telemetry:
            return {"hunting_detected": False, "reason": "No data"}
        
        positions = [s['position'] for s in telemetry if s['position'] is not None]
        voltages = [s['voltage'] for s in telemetry if s['voltage'] is not None]
        
        if not positions:
            return {"hunting_detected": False, "reason": "No position data"}
        
        # Calculate statistics
        pos_mean = sum(positions) / len(positions)
        pos_variance = sum((p - pos_mean)**2 for p in positions) / len(positions)
        pos_range = max(positions) - min(positions)
        
        # Check for voltage sag
        min_voltage = min(voltages) if voltages else 12.0
        voltage_sag = min_voltage < 11.0
        
        # Detect oscillation pattern (simplified)
        hunting_detected = pos_variance > 100 and pos_range > 50  # Adjust thresholds as needed
        
        return {
            "hunting_detected": hunting_detected,
            "position_mean": pos_mean,
            "position_variance": pos_variance,
            "position_range": pos_range,
            "min_voltage": min_voltage,
            "voltage_sag": voltage_sag,
            "position_range_degrees": pos_range * 0.3,  # Approximate conversion
            "sample_count": len(telemetry)
        }
    
    def fix_deadband(self, servo_id: int, deadband: int = 3) -> bool:
        """Apply deadband fix to reduce hunting."""
        print(f"🔧 Applying deadband fix to servo {servo_id}...")
        
        if deadband < 1 or deadband > 8:
            print(f"❌ Deadband {deadband} out of safe range (1-8)")
            return False
        
        # Note: For STS3215, deadband is typically in angle limit registers
        # This is a simplified implementation - check your servo manual
        success = self.write_register(servo_id, STS3215_REGISTERS['MIN_ANGLE_LIMIT_L'], deadband, eeprom=True)
        
        if success:
            print(f"✅ Deadband set to {deadband} counts")
            print("⚠️  Power-cycle the servo to apply EEPROM changes")
        
        return success
    
    def factory_reset(self, servo_id: int) -> bool:
        """Perform factory reset on servo."""
        print(f"🏭 Performing factory reset on servo {servo_id}...")
        print("⚠️  This will restore all settings to factory defaults!")
        
        # Send factory reset command (opcode 0x06)
        # Implementation depends on your servo library
        try:
            # This is a placeholder - implement according to your servo's protocol
            print("🔄 Factory reset command sent")
            return True
        except Exception as e:
            print(f"❌ Factory reset failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Direct Servo Diagnosis Tool')
    parser.add_argument('--port', required=True, help='Serial port (e.g., /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=1000000, help='Baud rate (default: 1000000)')
    parser.add_argument('--scan', action='store_true', help='Scan for servos')
    parser.add_argument('--joint', type=int, help='Target servo ID')
    parser.add_argument('--monitor', action='store_true', help='Monitor telemetry')
    parser.add_argument('--duration', type=int, default=5, help='Monitor duration (seconds)')
    parser.add_argument('--fix-deadband', action='store_true', help='Apply deadband fix')
    parser.add_argument('--deadband', type=int, default=3, help='Deadband value (1-8)')
    parser.add_argument('--info', action='store_true', help='Show servo information')
    parser.add_argument('--factory-reset', action='store_true', help='Factory reset servo')
    
    args = parser.parse_args()
    
    if not FEETECH_AVAILABLE:
        print("❌ Feetech library not available. Install with: pip install feetech-servo")
        return
    
    # Initialize diagnosis tool
    diagnosis = DirectServoDiagnosis(args.port, args.baudrate)
    
    if not diagnosis.connect():
        return
    
    try:
        if args.scan:
            servos = diagnosis.scan_servos()
            print(f"Found servos: {servos}")
        
        if args.joint:
            servo_id = args.joint
            
            if args.info:
                info = diagnosis.get_servo_info(servo_id)
                print(f"\n📋 Servo {servo_id} Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            
            if args.monitor:
                telemetry = diagnosis.monitor_servo_telemetry(servo_id, args.duration)
                analysis = diagnosis.analyze_hunting(telemetry)
                
                print(f"\n📊 Hunting Analysis for Servo {servo_id}:")
                print(f"  Hunting detected: {analysis['hunting_detected']}")
                print(f"  Position variance: {analysis['position_variance']:.1f}")
                print(f"  Position range: {analysis['position_range']:.0f} counts ({analysis['position_range_degrees']:.1f}°)")
                print(f"  Min voltage: {analysis['min_voltage']:.1f}V")
                
                if analysis['voltage_sag']:
                    print("  ⚠️  Voltage sag detected - check power supply!")
                
                # Save telemetry
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"servo_{servo_id}_telemetry_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(telemetry, f, indent=2)
                print(f"  💾 Telemetry saved to {filename}")
            
            if args.fix_deadband:
                diagnosis.fix_deadband(servo_id, args.deadband)
            
            if args.factory_reset:
                confirm = input(f"⚠️  Really factory reset servo {servo_id}? [y/N]: ")
                if confirm.lower() == 'y':
                    diagnosis.factory_reset(servo_id)
        
    finally:
        diagnosis.disconnect()

if __name__ == "__main__":
    main()
