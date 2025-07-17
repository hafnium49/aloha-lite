# SO-101 Servo Hunting Diagnosis Guide

## Overview

This toolset provides comprehensive diagnosis for the classic "servo hunting" issue in SO-101 arms where joints oscillate at ~1 Hz with ±few-degree wobble.

**Target**: SO-101 Arm ID 5A68011258 (configured as Robot ID 1 in phosphobot)

## Scripts

### 1. `servo_diagnosis.py` - High-level Phosphobot API Diagnosis
Works through the phosphobot API for basic diagnosis and monitoring.

```bash
# Run full diagnosis on all joints
python servo_diagnosis.py

# Focus on specific joint (e.g., joint 3)
python servo_diagnosis.py --joint 3

# Live monitoring mode for 10 seconds
python servo_diagnosis.py --monitor --joint 3 --duration 10

# Apply simulated deadband fix
python servo_diagnosis.py --fix-deadband --joint 3 --deadband-value 3
```

### 2. `direct_servo_diagnosis.py` - Direct Servo Register Access
Requires `feetech-servo` library for direct servo communication.

```bash
# Install required library first
pip install feetech-servo

# Scan for connected servos
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --scan

# Get detailed servo information
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --info

# Monitor telemetry with direct register access
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --monitor --duration 5

# Apply real deadband fix
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --fix-deadband --deadband 3

# Factory reset (use with caution!)
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --factory-reset
```

## Systematic Troubleshooting Process

### Step 1: Initial Assessment
```bash
# Run basic diagnosis
python servo_diagnosis.py --joint 3

# Check for obvious hunting patterns
python servo_diagnosis.py --monitor --joint 3 --duration 10
```

### Step 2: Voltage Analysis
```bash
# Monitor for voltage sag during movement
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --monitor --duration 5
```

**Look for**:
- Voltage drops below 11V during movement
- Other joints twitching simultaneously
- LED flashing on the servo

**Fixes**:
- Add 470-1000µF electrolytic capacitor near adapter
- Shorten/thicken power leads
- Use ≥3A PSU per arm

### Step 3: Deadband Adjustment
```bash
# Apply deadband fix (most common solution)
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --fix-deadband --deadband 3

# Test after power cycle
python servo_diagnosis.py --monitor --joint 3 --duration 5
```

### Step 4: Calibration Check
```bash
# Re-run calibration (external command)
python -m lerobot.calibrate --robot.type=so101_follower --robot.port=/dev/ttyUSB0
```

### Step 5: PID Comparison
```bash
# Get servo information to compare PID settings
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 3 --info
python direct_servo_diagnosis.py --port /dev/ttyUSB0 --joint 1 --info  # Compare with good joint
```

## Common Root Causes & Solutions

| Symptom | Root Cause | Solution |
|---------|------------|----------|
| Voltage < 11V during movement | Power supply sag | Bigger PSU, capacitor, shorter cables |
| ±1-2 count oscillation | Deadband too narrow | Increase deadband to 2-4 counts |
| Same pose gives different readings | Calibration offset | Re-run calibration |
| Joint feels "soft" | Modified PID/torque | Restore default settings |
| Intermittent timeouts | Bus issues/duplicate ID | Check IDs, replace cables |

## Register Reference

### STS3215 Key Registers
| Register | Address | Purpose | Safe Range | Anti-jitter Value |
|----------|---------|---------|------------|-------------------|
| Deadband | 0x0A | Position deadband | 1-8 counts | **3 counts** |
| PID Kp | 0x1C | Position loop gain | 0-254 | 40-60 |
| PID Ki | 0x1D | Integral gain | 0-254 | 0-20 |
| PID Kd | 0x1E | Derivative gain | 0-254 | 0-8 |
| Torque Limit | 0x24-0x25 | Max torque | 0-1023 | ≥80% |

## Expected Output Examples

### Healthy Joint
```
Joint 3: No hunting detected
  Position variance: 0.000012 rad²
  Position range: 0.05°
  Min voltage: 12.1V
```

### Hunting Joint
```
Joint 3: HUNTING DETECTED!
  Position variance: 0.002156 rad²
  Position range: 2.3°
  Min voltage: 10.8V
  💡 VOLTAGE_SAG: Add 470-1000µF capacitor, shorten power leads
  💡 DEADBAND: Increase dead-band to 2-4 counts
```

## Files Generated
- `servo_diagnosis_YYYYMMDD_HHMMSS.json` - Full diagnosis report
- `servo_X_telemetry_YYYYMMDD_HHMMSS.json` - Detailed telemetry data

## Hardware Requirements
- SO-101 arm connected to phosphobot server
- For direct access: USB-to-TTL adapter connected to servo bus
- Multimeter for voltage verification (recommended)

## Safety Notes
- Always test deadband changes incrementally (start with 2-3 counts)
- Power-cycle after EEPROM changes
- Factory reset only as last resort
- Monitor temperature during extended testing

## Quick Diagnostic Checklist
1. ✅ LED status: Solid = OK, Flashing = Alarm
2. ✅ Voltage: Should stay ≥11V during movement
3. ✅ Position oscillation: <0.1° = OK, >1° = hunting
4. ✅ Other joints: Should not twitch when one moves
5. ✅ Deadband: Try increasing to 3 counts
6. ✅ Calibration: Re-run if offset suspected
