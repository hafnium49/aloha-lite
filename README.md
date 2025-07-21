# Aloha Lite

This repository provides a comprehensive robotics stack for controlling SO-101 arms with Phosphobot, featuring advanced dataset processing, precise joint extraction, configuration-based robot control, and **smooth trajectory planning** using the ModernRobotics library from PyPI.

## Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd aloha-lite

# Install dependencies (includes modern_robotics from PyPI)
pip install -r requirements.txt

# Or use the automated setup script
./setup.sh

# Verify installation
python3 verify_installation.py
```

### Basic Usage

#### Robot Operations (robot_service/)
```bash
# Execute robot configurations using main service scripts
python3 robot_service/execute_rules.py --config your_config_name

# Execute with smooth trajectory planning
python3 robot_service/execute_rules.py --config your_config_name --duration 5.0 --max-velocity 0.2

# Sequential multi-step procedures
python3 robot_service/sequential_execute.py standoff_to_dispensing

# Bottle operations
python3 robot_service/squeeze_bottle.py --duration 2.0
python3 robot_service/bottle_operations.py --quick-squeeze
```

#### Utilities (utilities/)
```bash
# Verify installation
python3 utilities/verify_installation.py

# Trajectory planning tools
python3 utilities/trajectory_planner.py --config your_config_name

# Joint diagnostics and reading
python3 utilities/joint_reader.py --arm left
python3 utilities/servo_diagnosis.py --joint 3 --fix-deadband

# System analysis
python3 utilities/analyze_quintic.py
```

#### Examples (examples/)
```bash
# Test trajectory planning
python3 examples/trajectory_example.py

# Advanced trajectory execution
python3 examples/trajectory_executor.py --config your_config_name

# Joint reader examples
python3 examples/joint_reader_examples.py
```

## Development Workflow

### Working with the Reorganized Structure

**For Robot Operations:**
- Use scripts in `robot_service/` for actual robot control and operations
- All robot execution scripts are now in this directory
- The FastAPI service (`main.py`) provides web API access to robot functions

**For Development and Diagnostics:**  
- Use tools in `utilities/` for development, testing, and troubleshooting
- Joint diagnostics, trajectory analysis, and system verification tools
- Installation verification and system analysis utilities

**For Learning and Testing:**
- Use code in `examples/` to understand how to use the system
- Sample implementations and demonstrations
- Safe testing environment for new features

**Cross-Directory Dependencies:**
- Import paths are automatically resolved using `sys.path` modifications
- Examples can import from both `utilities/` and `robot_service/` directories  
- Utilities can import from `robot_service/` when needed

## Project Structure

The repository is organized into the following directories:

```
aloha-lite/
├── robot_service/          # Robot control and operation scripts
│   ├── main.py            # FastAPI service for robot operations
│   ├── execute_rules.py   # Configuration-based robot execution
│   ├── sequential_execute.py  # Multi-step procedure automation
│   ├── squeeze_bottle.py  # Bottle squeezing operations
│   ├── bottle_operations.py   # Advanced bottle handling
│   └── *.md              # Related documentation
├── utilities/             # Development and diagnostic tools
│   ├── trajectory_planner.py  # ModernRobotics trajectory planning
│   ├── joint_reader.py    # Joint position reading utility
│   ├── servo_diagnosis.py # Servo troubleshooting tools
│   ├── verify_installation.py  # System verification
│   ├── analyze_quintic.py # Trajectory analysis
│   └── *.md              # Tool documentation
├── examples/              # Sample code and demonstrations
│   ├── trajectory_example.py    # Basic trajectory examples
│   ├── trajectory_executor.py  # Advanced trajectory execution
│   └── joint_reader_examples.py # Joint reading examples
├── frontend/              # Web interface
├── vision_bridge/         # Image processing service
├── phosphobot/           # Robot control system (git subtree)
├── aloha-lite-demo2rule/ # Dataset processing tools
├── temp_rules/           # Configuration files
├── tests/                # Test files
├── scripts/              # Setup and utility scripts
└── docker-compose.yml    # Service orchestration
```

## Features

- **🎯 Smooth Trajectory Planning** - ModernRobotics-based joint trajectory generation with velocity control
- **🤖 Flexible Arm Control** - Support for dual-arm, left-arm-only, or right-arm-only configurations
- **🔧 Four-Arm System Support** - Configurable arm IDs for multi-arm phosphobot setups
- **📊 Advanced Dataset Processing** - LeRobot v2 dataset integration with CSV/Python rule extraction
- **⏱️ Time-Based Configuration Extraction** - Extract precise joint values at specific timestamps
- **JSON Configuration Management** - Comprehensive robot configuration system with metadata
- **Sequential Execution Tools** - Multi-step procedure automation with timing control
- **Single-Arm Operations** - Individual arm control while keeping other arms steady
- **Complete Phosphobot Integration** - Full phosphobot system included as a git subtree
- **Laboratory Automation** - Pre-configured tasks like dispensing water to beakers
- **Enhanced Safety Features** - Collision-aware execution with default no-initialization
- **Flexible Output Formats** - CSV, Python, and JSON configurations for robot rules
- **Intelligent Subtree Management** - Automated push scripts with fallback handling
- **Robust error handling** with structured responses and timeouts
- **Resource cleanup** to prevent memory leaks
- **Health checks** for all services
- **Environment-based configuration** with secrets support
- **Comprehensive logging** throughout the system
- **CORS support** for cross-origin requests
- **Automatic retry mechanisms** and circuit breakers
- **Real-time robot control** via ZMQ messaging
- **Vision capture and analysis** with color checker detection

## Robot Control Features

### Four-Arm System Configuration
The system supports configurable arm IDs for four-arm phosphobot setups:
- **Left arm**: ID 3 (Serial: 5A68011258) - Default
- **Right arm**: ID 2 (Serial: 5A68009540) - Default

### Flexible Configuration Types
- **Dual-arm configurations**: Move both arms simultaneously
- **Left-arm-only configurations**: Move left arm, keep right arm steady
- **Right-arm-only configurations**: Move right arm, keep left arm steady

### Configuration-Based Execution
Execute pre-defined robot configurations safely:

```bash
# Execute dual-arm configurations
python3 robot_service/execute_rules.py --config standoff_configuration_stage1
python3 robot_service/execute_rules.py --config dispensing_water_to_beaker

# Execute single-arm configurations
python3 robot_service/execute_rules.py --config ready_to_pick_beaker  # Left arm only
python3 robot_service/execute_rules.py --config left_arm_only_demo    # Left arm only
python3 robot_service/execute_rules.py --config right_arm_only_demo   # Right arm only

# Specify custom arm IDs for four-arm systems
python3 robot_service/execute_rules.py --config ready_to_pick_beaker --left-arm-id 3 --right-arm-id 2

# Enable initialization (use with caution - may cause collisions)
python3 robot_service/execute_rules.py --config standoff_configuration_stage1 --init
```

### Sequential Procedure Execution
Execute multi-step robot procedures with mixed arm configurations:

```bash
# Execute predefined sequences
python3 robot_service/sequential_execute.py standoff_to_dispensing
python3 robot_service/sequential_execute.py full_lab_procedure
python3 robot_service/sequential_execute.py single_arm_demo
python3 robot_service/sequential_execute.py independent_arm_movements

# Manual sequences with custom timing
python3 robot_service/sequential_execute.py left_arm_only_demo ready_to_pick_beaker dispensing_water_to_beaker --pause-between 2.0

# Specify arm IDs for predefined sequences
python3 robot_service/sequential_execute.py beaker_pickup_sequence --left-arm-id 3 --right-arm-id 2

# List available sequences
python3 robot_service/sequential_execute.py --list
```

### Dataset Rule Extraction
Convert LeRobot datasets to executable robot configurations:

```bash
# Extract rules as Python script (default)
python3 aloha-lite-demo2rule/demo2rules.py --dataset Hafnium49/aloha_lite --episode 1 --out rules.py

# Extract rules as CSV file for analysis
python3 aloha-lite-demo2rule/demo2rules.py --dataset Hafnium49/aloha_lite --episode 1 --out rules.csv --format csv
```

### Time-Based Joint Extraction
Extract precise joint configurations at specific timestamps:

```bash
# Extract joint configuration at 4.2 seconds from episode 1
cd aloha-lite-demo2rule
python3 extract_at_time.py Hafnium49/aloha_lite 1 4.2

# This generates:
# - extracted_Hafnium49_aloha_lite_ep1_t4.2s.json (detailed configuration)
# - config_4_2s.py (executable Python configuration)
```

### Available Configurations

The system includes these pre-configured robot positions:

#### Dual-Arm Configurations:
- **`standoff_configuration_stage1`** - Safe standoff position extracted from dataset stage 1
- **`dispensing_water_to_beaker`** - Laboratory procedure for water dispensing (precise values from demonstration at 4.2s)

#### Single-Arm Configurations:
- **`ready_to_pick_beaker`** - Left arm only beaker-picking position (right arm stays steady)
- **`left_arm_only_demo`** - Demo configuration for left arm movement testing
- **`right_arm_only_demo`** - Demo configuration for right arm movement testing

#### Configuration Structure:
Configurations are stored in `temp_rules/robot_configurations.json` with:
- **Flexible arm specifications** - Support for dual-arm, left-arm-only, or right-arm-only
- **Complete joint specifications** with 6-DOF joint values in radians
- **Source metadata** (dataset, episode, timestamp, extraction method)
- **Phosphobot API usage examples** with exact HTTP calls
- **Python code examples** for execution with phosphobot SkillClient
- **Arm ID configuration** for four-arm phosphobot systems

### Enhanced Subtree Management

Intelligent git subtree operations with automatic fallback:

```bash
# Enhanced automated subtree push (recommended)
./push_subtree.sh "Your commit message"
# or
python3 utilities/push_subtree.py "Your commit message"
```

**New Features:**
- Automatic fallback to force push when regular push fails
- Smart .gitignore handling (temporary modification and restoration)
- Enhanced error handling with automatic cleanup
- Colored output with detailed status reporting
- Handles non-fast-forward push scenarios gracefully

## Architecture

The system consists of:

1. **Robot Service** - FastAPI service for robot operations and control
2. **Vision Bridge** - Image capture and processing service  
3. **Frontend** - Web interface for robot control
4. **Phosphobot Core** - Robot control system (managed separately)
5. **Demo2Rules** - Dataset processing and rule extraction with CSV/Python output
6. **Extract At Time** - Precise joint value extraction at specific timestamps
7. **Utilities** - Development tools, diagnostics, and trajectory planning
8. **Examples** - Sample implementations and demonstrations
9. **MinIO** - S3-compatible object storage for images
10. **Traefik** - API gateway and load balancer

## Running locally

**Note:** Phosphobot service is commented out in docker-compose.yml and should be managed separately.

1. Copy the environment configuration:
```bash
cp .env.example .env
# Edit .env with your specific configuration
```

2. Start the services:
```bash
docker-compose up --build -d
```

Once started you can access:

- `http://localhost:8080/` – web front-end for robot operations
- `http://localhost:8080/robot/docs` – Robot Service Swagger UI  
- `http://localhost:9001/` – MinIO Console
- Phosphobot dashboard: Manage separately as needed
- `http://localhost:8080/robot/docs` – Robot Service Swagger UI
- `http://localhost:9001/metrics` – Robot Service Prometheus metrics
- `http://localhost:9003/metrics` – Vision Bridge Prometheus metrics
- `http://localhost:9001/` – MinIO Console

The system will automatically create the required S3 bucket and handle service dependencies.

## Robot Configuration

The system supports multiple robot types and configurations:

### Environment Configuration
Via the `ROBOT_TYPE` environment variable:
- `simulator` - Virtual robot for testing (default)
- `so100` - SO-100 physical robot
- `so101` - SO-101 physical robot (recommended for dual-arm setups)
- `wx250` - WX-250 robot arm

### Robot Configurations
Advanced JSON-based configurations for precise robot control:

```json
{
  "configurations": {
    "dispensing_water_to_beaker": {
      "name": "dispensing_water_to_beaker",
      "description": "Configuration for dispensing water - extracted from demonstration at 4.2s",
      "source": {
        "dataset": "Hafnium49/aloha_lite",
        "episode": 1,
        "timestamp": 4.2,
        "frame_index": 126,
        "extraction_method": "time_based"
      },
      "configuration": {
        "left_arm": { "joints": { "j1": 0.227, "j2": 0.746, ... } },
        "right_arm": { "joints": { "j1": 0.219, "j2": 0.198, ... } }
      },
      "usage": {
        "phosphobot_api": {
          "left_arm": "POST /joints/write with body: [0.227, 0.746, ...]",
          "right_arm": "POST /joints/write with body: [0.219, 0.198, ...]"
        }
      }
    }
  }
### Single-Arm Configuration Example
```json
{
  "configurations": {
    "ready_to_pick_beaker": {
      "name": "ready_to_pick_beaker",
      "description": "Ready to pick beaker position (left arm only) - right arm stays steady",
      "source": {
        "dataset": "Hafnium49/example_dataset",
        "episode": 2,
        "timestamp": 1.6,
        "extraction_method": "time_based"
      },
      "configuration": {
        "left_arm": { "joints": { "j1": 0.542, "j2": 0.921, "j3": 0.298, ... } }
        // No right_arm section - keeps current position
      },
      "usage": {
        "phosphobot_api": {
          "left_arm": "POST /joints/write with body: [0.542, 0.921, 0.298, ...]"
        }
      }
    }
  }
}
```

### Dual-Arm Configuration Example
```json
{
  "configurations": {
    "dispensing_water_to_beaker": {
      "name": "dispensing_water_to_beaker",
      "description": "Configuration for dispensing water - extracted from demonstration at 4.2s",
      "source": {
        "dataset": "Hafnium49/aloha_lite",
        "episode": 1,
        "timestamp": 4.2,
        "frame_index": 126,
        "extraction_method": "time_based"
      },
      "configuration": {
        "left_arm": { "joints": { "j1": 0.227, "j2": 0.746, ... } },
        "right_arm": { "joints": { "j1": 0.219, "j2": 0.198, ... } }
      },
      "usage": {
        "phosphobot_api": {
          "left_arm": "POST /joints/write with body: [0.227, 0.746, ...]",
          "right_arm": "POST /joints/write with body: [0.219, 0.198, ...]"
        }
      }
    }
  }
}
```

### Enhanced Safety Features
- **Default no-initialization** - Prevents arm collisions during startup
- **Single-arm control** - Move one arm while keeping the other steady
- **Four-arm system support** - Configurable arm IDs for multi-arm setups
- **Direct joint control** - Move from current position to target
- **Configuration validation** - Ensures valid joint ranges and completeness
- **Error handling** - Graceful failure with automatic cleanup
- **Sequential timing** - Controlled delays between movements in procedures

## Development Workflow

### 1. Dataset Processing
```bash
# Process LeRobot dataset to CSV for analysis
cd aloha-lite-demo2rule
python3 demo2rules.py --dataset Hafnium49/aloha_lite --episode 1 --out episode_1_rules.csv --format csv

# Extract specific timestamp configurations
python3 extract_at_time.py Hafnium49/aloha_lite 1 4.2
python3 extract_at_time.py Hafnium49/example_dataset 2 1.6
```

### 2. Configuration Creation and Management
```bash
# Update configurations with extracted values
# Precise joint values from extracted files can be used to update configurations

# Create single-arm configurations by including only left_arm or right_arm sections
# Create dual-arm configurations by including both left_arm and right_arm sections

# Verify configuration format
python3 -m json.tool temp_rules/robot_configurations.json
```

### 3. Robot Execution and Testing
```bash
# Test dual-arm configurations
python3 execute_rules.py --config standoff_configuration_stage1
python3 execute_rules.py --config dispensing_water_to_beaker

# Test single-arm configurations
python3 execute_rules.py --config ready_to_pick_beaker      # Left arm only
python3 execute_rules.py --config left_arm_only_demo       # Left arm only  
python3 execute_rules.py --config right_arm_only_demo      # Right arm only

# Execute with custom arm IDs for four-arm systems
python3 execute_rules.py --config ready_to_pick_beaker --left-arm-id 3 --right-arm-id 2

# Execute sequential procedures with mixed configurations
python3 sequential_execute.py single_arm_demo              # Left → Right → Dual
python3 sequential_execute.py independent_arm_movements    # Independent arm control
python3 sequential_execute.py beaker_pickup_sequence       # Standoff → Ready to pick

# Move to standoff position for safety
python3 execute_rules.py --config standoff_configuration_stage1
```

### 4. Enhanced Subtree Management
```bash
# Push changes to subtree with automatic fallback
./push_subtree.sh "Add new laboratory procedure with precise joint values"

# The script automatically handles:
# - .gitignore temporary modification
# - Regular push with fallback to force push
# - Proper cleanup and restoration
```

## Available Predefined Sequences

The system includes these automated multi-step procedures:

### Dual-Arm Sequences:
- **`standoff_to_dispensing`** - Move from standoff to dispensing configuration
- **`dispensing_to_standoff`** - Return from dispensing to standoff configuration  
- **`full_lab_procedure`** - Complete lab workflow: standoff → dispensing → standoff

### Mixed Arm Sequences:
- **`beaker_pickup_sequence`** - Standoff → ready to pick beaker (left arm only)
- **`complete_beaker_workflow`** - Standoff → ready to pick → dispensing → standoff
- **`single_arm_demo`** - Left arm demo → right arm demo → dual-arm configuration
- **`independent_arm_movements`** - Demonstrates independent control of each arm

## Architecture

The system consists of:

1. **Phosphobot Core** - Robot control system with ZMQ state publishing and four-arm support
2. **Robot Service** - FastAPI service for dispense operations  
3. **Vision Bridge** - Image capture and processing service
4. **Frontend** - Web interface for robot control
5. **Demo2Rules** - Dataset processing and rule extraction with CSV/Python output
6. **Extract At Time** - Precise joint value extraction at specific timestamps
7. **Execute Rules** - Configuration-based robot execution with flexible arm control
8. **Sequential Execute** - Multi-step procedure automation with single/dual-arm support
9. **Enhanced Subtree Management** - Intelligent git subtree operations
10. **MinIO** - S3-compatible object storage for images
11. **Traefik** - API gateway and load balancer

### Key Components:

#### Robot Control Layer:
- **Four-arm phosphobot support** with configurable arm IDs
- **Flexible configuration system** supporting dual-arm and single-arm operations
- **Safety-first execution** with default no-initialization
- **Sequential automation** with precise timing control

#### Dataset Processing Layer:
- **LeRobot v2 integration** for dataset analysis
- **Time-based extraction** for precise joint value capture
- **Multiple output formats** (CSV, Python, JSON)
- **Automatic format detection** and intelligent processing

#### Configuration Management:
- **JSON-based configurations** with complete metadata
- **Single-arm support** (left-arm-only, right-arm-only)
- **Dual-arm support** with synchronized movements
- **Source tracking** and usage examples

## Production Deployment

For production use:

1. **Update credentials** in `.env` file with secure values
2. **Configure robot type** appropriate for your hardware
3. **Configure arm IDs** for your four-arm phosphobot setup
4. **Configure CORS** origins in the FastAPI applications
5. **Set up proper SSL/TLS** termination
6. **Configure monitoring** and alerting for the Prometheus metrics
7. **Set up log aggregation** for centralized logging
8. **Use external database** instead of in-memory storage for tasks
9. **Validate robot configurations** before deployment
10. **Test single-arm safety** in controlled environment

## Git Subtree Management

The repository includes two git subtrees:

### Phosphobot Subtree
The phosphobot repository is included as a git subtree:

```bash
# Pull latest changes from phosphobot
git subtree pull --prefix=phosphobot https://github.com/hafnium49/phosphobot.git main --squash

# Push changes back to phosphobot (if you have write access)
git subtree push --prefix=phosphobot https://github.com/hafnium49/phosphobot.git main
```

### Aloha-Lite-Demo2Rule Subtree
The demo2rule processing system:

```bash
# Automated subtree push (recommended)
./push_subtree.sh "Your commit message"

# Alternative Python version
python3 push_subtree.py "Your commit message" 

# Manual subtree operations
git subtree pull --prefix=aloha-lite-demo2rule https://github.com/hafnium49/aloha-lite-demo2rule.git main --squash
git subtree push --prefix=aloha-lite-demo2rule https://github.com/hafnium49/aloha-lite-demo2rule.git main
```

The automated scripts handle .gitignore management and provide colored output with error handling.

## Project Structure

```
aloha-lite/
├── README.md                      # This file
├── docker-compose.yml             # Service orchestration
├── execute_rules.py               # Configuration-based robot execution
├── push_subtree.sh               # Automated subtree push (bash)
├── push_subtree.py               # Automated subtree push (python)
├── frontend/                     # Web interface
├── robot_service/                # FastAPI robot control
├── vision_bridge/                # Image processing
├── phosphobot/                   # Robot control system (subtree)
├── aloha-lite-demo2rule/         # Dataset processing (subtree)
└── temp_rules/                   # Generated configurations
    ├── robot_configurations.json # Robot position definitions
    └── rules_episode_1.csv       # Extracted dataset rules
```

## API Endpoints

### Robot Control
- `POST /joints/write?robot_id={0|1}` - Set joint positions
- `POST /joints/read?robot_id={0|1}` - Read current joint positions  
- `POST /move/init` - Initialize robot system

### Vision Processing
- `POST /color-checker` - Analyze color checker in images
- `GET /health` - Service health check

### Web Interface
- `GET /` - Main robot control dashboard
- `GET /docs` - API documentation (Swagger UI)

## Testing and Validation

### Color Checker Detection
To verify the color checker detection:

```bash
python vision_bridge/tests/test_color_checker.py
```

### Robot Configuration Testing
Test robot configurations safely:

```bash
# List all available configurations
python3 execute_rules.py

# Test specific configurations
python3 execute_rules.py --config standoff_configuration_stage1
python3 execute_rules.py --config dispensing_water_to_beaker

# Validate JSON configuration files
python3 -m json.tool temp_rules/robot_configurations.json
```

### Dataset Processing Testing
Validate dataset rule extraction:

```bash
cd aloha-lite-demo2rule
python3 tests/test_demo2rules.py  # If available
```

## Common Use Cases

### Laboratory Automation
```bash
# 1. Move to standoff position
python3 execute_rules.py --config standoff_configuration_stage1

# 2. Execute laboratory procedure
python3 execute_rules.py --config dispensing_water_to_beaker

# 3. Return to standoff
python3 execute_rules.py --config standoff_configuration_stage1
```

### Dataset-to-Robot Pipeline
```bash
# 1. Extract rules from dataset
python3 aloha-lite-demo2rule/demo2rules.py --dataset Hafnium49/aloha_lite --episode 1 --out new_task.csv

# 2. Convert CSV to configuration (manual step)
# Edit temp_rules/robot_configurations.json

# 3. Execute new configuration
python3 execute_rules.py --config new_task_configuration
```

### Development and Deployment
```bash
# 1. Start development environment
docker-compose up --build -d

# 2. Test robot configurations
python3 execute_rules.py --config test_configuration

# 3. Push changes to subtree
./push_subtree.sh "Add new laboratory procedures"

# 4. Deploy to production
# Update .env with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Robot Collision Issues
- **Problem**: Arms crash into each other during initialization
- **Solution**: Use default behavior (no `--init` flag) or `--no-init` explicitly

### Configuration Not Found
- **Problem**: `Configuration 'name' not found`
- **Solution**: Check configuration name matches JSON exactly, verify file exists in search directories

### Dataset Processing Errors
- **Problem**: Failed to download or process dataset
- **Solution**: Check internet connection, verify dataset repository access, ensure sufficient disk space

### Git Subtree Issues
- **Problem**: Subtree push/pull conflicts
- **Solution**: Use automated scripts (`./push_subtree.sh`) which handle .gitignore conflicts automatically

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-laboratory-procedure`
3. **Add configurations** to `temp_rules/robot_configurations.json`
4. **Test thoroughly**: `python3 execute_rules.py --config your_config`
5. **Update documentation** in README.md
6. **Push subtree changes**: `./push_subtree.sh "Add new procedure"`
7. **Submit pull request**

## License

This project is licensed under the MIT License - see the LICENSE file for details.
