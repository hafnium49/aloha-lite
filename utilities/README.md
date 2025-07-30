# ALOHA-Lite Utilities

This directory contains a comprehensive collection of utilities, tools, and scripts for the ALOHA-Lite robotic system. These utilities cover robot diagnostics, calibration, trajectory planning, joint validation, and testing frameworks.

## 📁 Directory Structure

```
utilities/
├── README.md                           # This file - main utilities documentation
├── tests/                              # Test framework and validation
│   ├── README.md                       # Testing framework documentation
│   └── SUMMARY.md                      # Test utilities summary
├── *.py                               # Python utility scripts
└── *.md                               # Documentation files
```

## 🤖 Core Utilities

### Robot Diagnostics & Validation
| Utility | Description | Documentation |
|---------|-------------|---------------|
| `servo_diagnosis.py` | Comprehensive servo motor diagnostic tool | [`SERVO_DIAGNOSIS_GUIDE.md`](SERVO_DIAGNOSIS_GUIDE.md) |
| `direct_servo_diagnosis.py` | Direct servo communication diagnostics | [`SERVO_DIAGNOSIS_GUIDE.md`](SERVO_DIAGNOSIS_GUIDE.md) |
| `joint_reader.py` | Real-time joint position monitoring | [`JOINT_READER_GUIDE.md`](JOINT_READER_GUIDE.md) |
| `joint_validator.py` | Joint configuration validation system | [`JOINT_VALIDATION_README.md`](JOINT_VALIDATION_README.md) |
| `check_joint_limits.py` | Joint limit boundary checking | [`JOINT_VALIDATION_README.md`](JOINT_VALIDATION_README.md) |

### Motion Planning & Control
| Utility | Description | Documentation |
|---------|-------------|---------------|
| `trajectory_planner.py` | Advanced trajectory planning with quintic polynomials | [`TRAJECTORY_PLANNER_README.md`](TRAJECTORY_PLANNER_README.md) |
| `analyze_quintic.py` | Quintic polynomial trajectory analysis | [`TRAJECTORY_PLANNER_README.md`](TRAJECTORY_PLANNER_README.md) |

### Calibration & Ground Truth
| Utility | Description | Documentation |
|---------|-------------|---------------|
| `ground_truth_calibrator.py` | ColorOptimizer ground truth calibration system | [`README_ground_truth_calibrator.md`](README_ground_truth_calibrator.md) |

### System Maintenance
| Utility | Description | Documentation |
|---------|-------------|---------------|
| `verify_installation.py` | System installation verification | [`MODERNROBOTICS_STATUS.md`](MODERNROBOTICS_STATUS.md) |
| `verify_corrections.py` | Installation correction verification | [`MODERNROBOTICS_STATUS.md`](MODERNROBOTICS_STATUS.md) |
| `push_subtree.py` | Git subtree management utility | [`MIGRATION_SUMMARY.md`](MIGRATION_SUMMARY.md) |

### Examples & Templates
| File | Description | Documentation |
|------|-------------|---------------|
| `example_joint_validation.py` | Joint validation usage examples | [`JOINT_VALIDATION_README.md`](JOINT_VALIDATION_README.md) |
| `example_fixed_config.json` | Sample robot configuration file | [`JOINT_VALIDATION_README.md`](JOINT_VALIDATION_README.md) |

## 📚 Documentation Index

### System Status & Migration
- [`MODERNROBOTICS_STATUS.md`](MODERNROBOTICS_STATUS.md) - ModernRobotics library status and installation
- [`MIGRATION_SUMMARY.md`](MIGRATION_SUMMARY.md) - System migration and git subtree management

### Robot Hardware & Diagnostics
- [`SERVO_DIAGNOSIS_GUIDE.md`](SERVO_DIAGNOSIS_GUIDE.md) - Complete servo diagnostic procedures
- [`JOINT_READER_GUIDE.md`](JOINT_READER_GUIDE.md) - Joint position monitoring and logging
- [`JOINT_VALIDATION_README.md`](JOINT_VALIDATION_README.md) - Joint configuration validation system

### Motion Planning & Control
- [`TRAJECTORY_PLANNER_README.md`](TRAJECTORY_PLANNER_README.md) - Advanced trajectory planning documentation

### Calibration & Testing  
- [`README_ground_truth_calibrator.md`](README_ground_truth_calibrator.md) - ColorOptimizer ground truth calibration
- [`tests/README.md`](tests/README.md) - Comprehensive testing framework
- [`tests/SUMMARY.md`](tests/SUMMARY.md) - Test utilities overview

## 🚀 Quick Start Guide

### 1. Robot Diagnostics
```bash
# Run comprehensive servo diagnostics
python utilities/servo_diagnosis.py

# Monitor joint positions in real-time
python utilities/joint_reader.py --monitor

# Validate joint configurations
python utilities/joint_validator.py --config example_fixed_config.json
```

### 2. Motion Planning
```bash
# Plan smooth trajectories between configurations
python utilities/trajectory_planner.py --start config1.json --end config2.json

# Analyze trajectory smoothness
python utilities/analyze_quintic.py --trajectory output_trajectory.json
```

### 3. Calibration
```bash
# Calibrate individual color solutions
python utilities/ground_truth_calibrator.py --solution red

# Calibrate all solutions
python utilities/ground_truth_calibrator.py --all
```

### 4. System Verification
```bash
# Verify system installation
python utilities/verify_installation.py

# Check joint limits
python utilities/check_joint_limits.py --config robot_config.json
```

### 5. Testing
```bash
# Run all utility tests
python utilities/tests/run_tests.py

# Demo ground truth calibrator
python utilities/tests/demo_calibrator.py
```

## 🔧 Utility Categories

### 🔍 Diagnostic Tools
Perfect for troubleshooting robot hardware issues:
- **Servo Diagnosis**: Comprehensive motor health checking
- **Joint Monitoring**: Real-time position tracking
- **System Verification**: Installation and configuration validation

### 🎯 Motion Control
Advanced trajectory planning and motion analysis:
- **Trajectory Planning**: Quintic polynomial-based smooth motion
- **Joint Validation**: Configuration boundary checking
- **Motion Analysis**: Trajectory smoothness and feasibility

### 🎨 Calibration Systems
ColorOptimizer ground truth preparation:
- **Solution Calibration**: Automated color measurement workflows
- **Ground Truth Generation**: Structured calibration data storage
- **Multi-Solution Support**: Red, yellow, and blue solution handling

### 🧪 Testing Framework
Comprehensive validation without hardware dependencies:
- **Mock Testing**: Robot-free utility validation
- **Interactive Demos**: Functionality demonstrations
- **Coverage Testing**: Complete utility test coverage

## 📋 Usage Patterns

### Development Workflow
1. **Validate System**: Use `verify_installation.py` to check setup
2. **Diagnose Hardware**: Run `servo_diagnosis.py` for health checks
3. **Plan Motion**: Use `trajectory_planner.py` for smooth movements
4. **Validate Configs**: Check limits with `joint_validator.py`
5. **Test Changes**: Run utility tests with `tests/run_tests.py`

### Calibration Workflow  
1. **Prepare Sequences**: Ensure calibration sequences are defined
2. **Run Calibration**: Use `ground_truth_calibrator.py` for each solution
3. **Validate Results**: Check generated ground truth files
4. **Test Integration**: Verify calibration with ColorOptimizer

### Troubleshooting Workflow
1. **System Check**: Run `verify_installation.py`
2. **Hardware Diagnosis**: Use `servo_diagnosis.py` and `joint_reader.py`
3. **Configuration Validation**: Check with `joint_validator.py`
4. **Analyze Logs**: Review diagnostic output files

## 🛠️ Installation Requirements

### Core Dependencies
```bash
# For robot control utilities
pip install modernrobotics numpy scipy

# For calibration utilities  
pip install fastapi uvicorn scikit-learn

# For testing framework
pip install unittest mock tempfile
```

### Optional Dependencies
```bash
# For advanced trajectory analysis
pip install matplotlib seaborn

# For enhanced diagnostics
pip install pandas tabulate
```

## 📊 Utility Status

| Category | Utilities | Status | Test Coverage |
|----------|-----------|--------|---------------|
| Diagnostics | 4 utilities | ✅ Stable | 🧪 Full mock testing |
| Motion Planning | 2 utilities | ✅ Stable | 🧪 Algorithm testing |
| Calibration | 1 utility | ✅ Stable | 🧪 22/22 tests passing |
| System Tools | 3 utilities | ✅ Stable | 🧪 Installation testing |
| Testing | 5 test files | ✅ Complete | 🧪 Self-validating |

## 🔗 Integration Points

### With Main System
- **Robot Service**: Utilities integrate with `robot_service/main.py`
- **Vision Bridge**: Calibration works with `vision_bridge/main.py` 
- **Frontend**: Ground truth data supports `frontend/main.py` ColorOptimizer

### With Configuration System
- **Sequential Sequences**: Calibration uses `temp_rules/sequential_sequences.json`
- **Robot Configs**: Validation works with robot configuration files
- **Ground Truth**: Calibration outputs to `frontend/ground_truth_calibration/`

## 🎯 Best Practices

### Before Using Utilities
1. **Read Documentation**: Check relevant `.md` files for detailed usage
2. **Verify Installation**: Run `verify_installation.py` first
3. **Test in Safe Mode**: Use test utilities before hardware operations
4. **Backup Configurations**: Save working configs before modifications

### During Development
1. **Use Validation**: Run `joint_validator.py` before deployment
2. **Monitor Hardware**: Use `joint_reader.py` during operations  
3. **Test Thoroughly**: Run utility tests after changes
4. **Document Changes**: Update relevant documentation files

### For Production
1. **Calibrate Regularly**: Use ground truth calibrator for accuracy
2. **Monitor Health**: Schedule regular servo diagnostics
3. **Validate Trajectories**: Check motion plans before execution
4. **Maintain Logs**: Keep diagnostic outputs for troubleshooting

## 🤝 Contributing

When adding new utilities:

1. **Create the utility**: Follow existing naming conventions
2. **Write documentation**: Create or update relevant `.md` files
3. **Add tests**: Include comprehensive test coverage
4. **Update README**: Add your utility to the appropriate table
5. **Provide examples**: Include usage examples in documentation

## 🆘 Support & Troubleshooting

### Common Issues
- **Import Errors**: Check `verify_installation.py` output
- **Hardware Connection**: Use `servo_diagnosis.py` for diagnostics
- **Configuration Issues**: Validate with `joint_validator.py`
- **Motion Problems**: Analyze with `trajectory_planner.py`

### Getting Help
1. **Check Documentation**: Relevant `.md` files have detailed guides
2. **Run Diagnostics**: Use appropriate diagnostic utilities
3. **Review Test Output**: Check `tests/` for validation results
4. **Analyze Logs**: Review generated diagnostic files

---

This utilities collection provides a comprehensive toolkit for ALOHA-Lite development, maintenance, and operation. Each utility is designed to work independently while integrating seamlessly with the overall system architecture. 🤖✨
