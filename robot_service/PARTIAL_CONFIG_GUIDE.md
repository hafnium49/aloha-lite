# Partial Configuration System Guide

## Overview
The enhanced laboratory automation system now supports **partial configurations** that allow selective joint modification while preserving all other joint positions. This enables precise, targeted movements without disrupting the robot's overall pose.

## Key Features

### 🎯 Selective Joint Control
- Modify only specific joints (e.g., just j6 for gripper control)
- Automatically preserve all other joint positions from current state
- No need to specify complete 6-joint configurations for simple adjustments

### 🔄 Automatic Position Merging
- System automatically reads current joint positions
- Merges specified joints with current positions
- Maintains robot stability and continuity

### 📊 Enhanced Execution Engine
The `execute_rules.py` system has been enhanced with:
- `get_current_joint_angles()` - Reads current robot positions
- `merge_joint_configurations()` - Combines partial config with current state
- `prepare_arm_configuration()` - Handles both complete and partial configs
- Backward compatibility with existing complete configurations

## Configuration Types

### Complete Configurations
Traditional 6-joint configurations specifying all joints:
```json
{
  "name": "dispensing_red_to_beaker",
  "left_arm": {
    "j1": 0.318, "j2": -0.196, "j3": 1.010, 
    "j4": -1.046, "j5": -2.012, "j6": 0.457
  },
  "right_arm": {
    "j1": -0.018, "j2": -0.227, "j3": 1.343,
    "j4": -1.174, "j5": -1.646, "j6": 1.494
  }
}
```

### Partial Configurations
Minimal configurations specifying only target joints:
```json
{
  "name": "squeeze_washing_bottle", 
  "description": "Partial configuration to squeeze washing bottle - only modifies right arm j6 to 0.3 while preserving all other joint positions",
  "source": "partial_configuration",
  "right_arm": {
    "j6": 0.3
  }
}
```

## Available Configurations

### Complete Configurations (11 total)
1. `standoff_configuration_stage1` - Safe standoff position
2. `dispensing_water_to_beaker` - Water dispensing position  
3. `ready_to_pick_beaker` - Beaker pickup position
4. `left_arm_only_demo` - Left arm demonstration
5. `right_arm_only_demo` - Right arm demonstration
6. `left_arm_standoff` - Left arm standoff only
7. `right_arm_standoff` - Right arm standoff only
8. `dispensing_yellow_to_beaker` - Yellow solution dispensing
9. `dispensing_blue_to_beaker` - Blue solution dispensing
10. `dispensing_red_to_beaker` - Red solution dispensing
11. `squeeze_washing_bottle` - ⭐ **NEW: Partial configuration**

### Predefined Sequences (10 total)
1. `standoff_to_dispensing` - Move to dispensing position
2. `dispensing_to_standoff` - Return to standoff
3. `full_lab_procedure` - Complete lab workflow
4. `beaker_pickup_sequence` - Beaker handling
5. `complete_beaker_workflow` - Full beaker workflow
6. `single_arm_demo` - Single arm movements
7. `independent_arm_movements` - Independent arm control
8. `right_arm_standoff_to_yellow` - Yellow dispensing sequence
9. `both_arms_standoff_to_red` - Red dispensing sequence
10. `squeeze_demo_sequence` - ⭐ **NEW: Partial config demo**

## Usage Examples

### Execute Single Partial Configuration
```bash
python3 execute_rules.py squeeze_washing_bottle
```

### Execute Sequence with Partial Configuration
```bash
python3 sequential_execute.py squeeze_demo_sequence
```

### Manual Sequence with Partial Config
```bash
python3 sequential_execute.py dispensing_red_to_beaker squeeze_washing_bottle dispensing_red_to_beaker
```

## System Behavior

### Execution Flow for Partial Configurations
1. **Load Configuration**: System detects missing joints in configuration
2. **Read Current State**: Automatically queries robot for current joint positions
3. **Merge Positions**: Combines specified joints with current positions
4. **Execute Movement**: Moves only the specified arm with merged joint values
5. **Preserve Other Arm**: Non-specified arm maintains current position

### Example Execution Log
```
🔄 right_arm: Partial configuration (missing ['j1', 'j2', 'j3', 'j4', 'j5'])
🔄 Merging with current joint positions...
📝 j6 → 0.300 rad

🎯 Moving to: squeeze_washing_bottle
Left arm (ID 3): keeping current position
Right arm (ID 2) joints: ['-0.018', '-0.227', '1.343', '-1.174', '-1.646', '0.300']
✅ Robot 2 joints set to: ['-0.018', '-0.227', '1.343', '-1.174', '-1.646', '0.300'] rad
```

## Benefits

### 🎯 Precision Control
- Modify only what needs to change (e.g., gripper pressure)
- Maintain precise positioning of other joints
- Reduce risk of unwanted movements

### 🛡️ Safety
- Preserve stable poses while making adjustments
- Minimize robot motion for simple operations
- Maintain collision-free positions

### ⚡ Efficiency
- Faster execution for simple adjustments
- Reduced configuration complexity
- Easy integration with existing workflows

## File Organization

```
temp_rules/
├── robot_configurations.json     # All configurations including partial
├── sequential_sequences.json     # Predefined sequences
├── squeeze_washing_bottle.json   # Individual partial config file
└── [other config files...]
```

## Development Notes

### Creating New Partial Configurations
1. Identify the minimal joints that need modification
2. Create configuration with only those joints specified
3. Test execution to verify automatic merging
4. Add to `robot_configurations.json` registry

### System Enhancement Points
- ✅ Automatic current position reading
- ✅ Intelligent configuration merging  
- ✅ Backward compatibility maintained
- ✅ Enhanced logging and debugging
- ✅ Integration with sequential execution

## Validation Results

The partial configuration system has been successfully tested with:
- ✅ Single joint modification (j6 only)
- ✅ Automatic position preservation (j1-j5 unchanged)
- ✅ Sequential execution integration
- ✅ Predefined sequence support
- ✅ Backward compatibility with complete configs
- ✅ Mixed sequences (complete + partial configurations)

This enhancement provides a powerful foundation for precise laboratory automation while maintaining the simplicity and safety of the existing system.
