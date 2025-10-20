# ALOHA-Lite Documentation Index

Welcome to ALOHA-Lite! This index helps you navigate the comprehensive documentation for this advanced robotics platform.

---

## Start Here

### For New Users
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (11 KB)
   - Project overview at a glance
   - Quick start guide
   - Common commands and APIs
   - Troubleshooting quick fixes
   - **Read this first!**

2. **[README.md](README.md)** (45 KB)
   - Comprehensive project documentation
   - Installation and setup
   - Feature overview
   - Architecture explanation
   - Common use cases

### For Developers
3. **[CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md)** (24 KB)
   - Project structure and organization
   - Technology stack details
   - Build system and configuration
   - Testing setup and framework
   - Key architectural patterns
   - Dependency management

4. **[ARCHITECTURE_DETAILS.md](ARCHITECTURE_DETAILS.md)** (31 KB)
   - System architecture diagrams
   - Data flow patterns
   - Service communication details
   - ML optimization system deep dive
   - Vision processing pipeline
   - Performance characteristics
   - Error handling & safety
   - Development considerations

---

## Service-Specific Documentation

### Robot Service
- **Location**: `robot_service/README.md` (24 KB)
- **Port**: 8000
- **Purpose**: Robot control, trajectory planning, configuration execution
- **Key Files**:
  - `main.py` - FastAPI service with Prometheus metrics
  - `execute_rules.py` - Configuration-based robot execution
  - `sequential_execute.py` - Multi-step automation

### Frontend Service
- **Location**: `frontend/README.md` (40 KB)
- **Port**: 3000
- **Purpose**: Web UI, ML optimization engine, service proxy
- **Key Files**:
  - `main.py` - ML engine with Bayesian optimization
  - `index.html` - Web interface (53 KB)
  - **Additional Docs**:
    - `ML_OPTIMIZATION_README.md` - ML system details
    - `USER_MANUAL_JA.md` - Japanese user manual

### Vision Bridge Service
- **Location**: `vision_bridge/README.md` (13 KB)
- **Port**: 5000
- **Purpose**: Computer vision, beaker analysis, SAM2 integration
- **Key Files**:
  - `main.py` - Vision service with SAM2 support
  - `beaker_analysis.py` - Color detection algorithms
  - **Additional Docs**:
    - `SAM2_SETUP_GUIDE.md` - Vision AI setup instructions

### MCP Server
- **Location**: `mcp_server/README.md` (8 KB)
- **Port**: 8900
- **Purpose**: Claude Desktop integration, Playwright automation
- **Key Files**:
  - `main.py` - MCP server with Playwright bridge
  - `system_prompt.md` - Claude system instructions

---

## Feature Documentation

### Color Mixing & Optimization
- **[COLOR_RATIO_IMPLEMENTATION.md](COLOR_RATIO_IMPLEMENTATION.md)** (5 KB)
  - Color mixing system details
  - Ratio calculations

- **[frontend/ML_OPTIMIZATION_README.md](frontend/ML_OPTIMIZATION_README.md)** (7 KB)
  - Bayesian optimization engine
  - Hue-only target optimization
  - CIELAB color space mathematics
  - Ground truth calibration

### Vision & Analysis
- **[vision_bridge/SAM2_SETUP_GUIDE.md](vision_bridge/SAM2_SETUP_GUIDE.md)** (14 KB)
  - Segment Anything 2 setup
  - Model installation
  - Integration details

### Robot Control & Trajectories
- **[utilities/TRAJECTORY_PLANNER_README.md](utilities/TRAJECTORY_PLANNER_README.md)** (5 KB)
  - ModernRobotics library usage
  - Trajectory planning

- **[utilities/JOINT_READER_GUIDE.md](utilities/JOINT_READER_GUIDE.md)** (5 KB)
  - Joint position reading
  - Diagnostics

- **[utilities/SERVO_DIAGNOSIS_GUIDE.md](utilities/SERVO_DIAGNOSIS_GUIDE.md)** (5 KB)
  - Servo troubleshooting
  - Calibration guide

### Dataset Processing
- **[aloha-lite-demo2rule/README.md](aloha-lite-demo2rule/README.md)** (varies)
  - LeRobot dataset conversion
  - Rule generation
  - Time-based extraction

### Laboratory Automation
- **[robot_service/README.md](robot_service/README.md)** (24 KB)
  - Bottle operations
  - Multi-color dispensing
  - Laboratory procedures

---

## Configuration & Setup

### Environment Setup
- **[tests/CONDA_SETUP.md](tests/CONDA_SETUP.md)** (5 KB)
  - Conda environment setup
  - Package management

### Configuration Guides
- **[robot_service/PARTIAL_CONFIG_GUIDE.md](robot_service/PARTIAL_CONFIG_GUIDE.md)** (6 KB)
  - Partial arm configurations
  - Single-arm setup

- **[robot_service/LEFT_ARM_STANDOFF_WITH_BEAKER.md](robot_service/LEFT_ARM_STANDOFF_WITH_BEAKER.md)** (6 KB)
  - Specific arm positioning

### Troubleshooting
- **[mcp_server/WINDOWS_TROUBLESHOOTING.md](mcp_server/WINDOWS_TROUBLESHOOTING.md)** (5 KB)
  - Windows-specific setup issues

---

## Advanced Topics

### Updates & Refactoring
- **[robot_service/BOTTLE_OPERATIONS_UPDATE.md](robot_service/BOTTLE_OPERATIONS_UPDATE.md)** (6 KB)
  - Bottle handling improvements

- **[robot_service/SQUEEZE_BOTTLE_REFACTOR.md](robot_service/SQUEEZE_BOTTLE_REFACTOR.md)** (6 KB)
  - Volume splitting system
  - Squeeze operation details

### Integration
- **[robot_service/EXECUTE_RULES_TRAJECTORY_INTEGRATION.md](robot_service/EXECUTE_RULES_TRAJECTORY_INTEGRATION.md)** (6 KB)
  - Trajectory integration with configuration execution

### ML Features
- **[mcp_server/ENHANCED_FEATURES.md](mcp_server/ENHANCED_FEATURES.md)** (4 KB)
  - Enhanced MCP capabilities

---

## Test Documentation

### Test Frameworks
- **Location**: Multiple test directories
- **Framework**: pytest
- **Coverage Areas**:
  - `frontend/tests/` - ML optimization tests (19+ tests)
  - `vision_bridge/tests/` - Vision processing tests
  - `utilities/tests/` - Utility tests
  - `robot_service/tests/` - Robot service tests
  - `tests/` - Integration tests

### Test Results
- **[vision_bridge/tests/README.md](vision_bridge/tests/README.md)** (varies)
  - Vision test documentation

- **[utilities/tests/README.md](utilities/tests/README.md)** (varies)
  - Utility test documentation

---

## Key Configuration Files

### JSON Configuration
```
temp_rules/robot_configurations.json    # 43 KB - 100+ robot positions
temp_rules/sequential_sequences.json    # 17 KB - Multi-step procedures
temp_rules/*.json                       # Other configs and test data
```

### Package & Build
```
pyproject.toml              # Modern Python packaging
requirements.txt            # Core dependencies
environment.yml             # Conda environment
docker-compose.yml          # Service orchestration
Dockerfile (multiple)       # Service containers
```

### Environment
```
.env.example                # Environment template
```

---

## Frequently Needed Information

### Quick Commands

**Robot Operations**
```bash
python3 robot_service/execute_rules.py --config dispensing_water_to_beaker
python3 robot_service/sequential_execute.py standoff_to_dispensing
```

**Dataset Processing**
```bash
cd aloha-lite-demo2rule
python3 demo2rules.py --dataset Hafnium49/aloha_lite --episode 1 --out rules.py
python3 extract_at_time.py Hafnium49/aloha_lite 1 4.2
```

**Diagnostics**
```bash
python3 utilities/verify_installation.py
python3 utilities/joint_reader.py --arm left
python3 utilities/servo_diagnosis.py --joint 3
```

### API Endpoints
- **Frontend**: http://localhost:3000
- **Robot API Docs**: http://localhost:8000/docs
- **Vision API Docs**: http://localhost:5000/docs
- **MinIO Console**: http://localhost:9001
- **Gateway**: http://localhost:8080

### File Sizes
- Repository: 63 MB total
- Python/TypeScript files: 339
- Documentation: 30+ MD files
- Robot configs: 100+ positions

---

## Migration & History

### Previous Versions
- **[frontend/MIGRATION_SUMMARY.md](frontend/MIGRATION_SUMMARY.md)** (3 KB)
  - Frontend migration details

- **[frontend/FRONTEND_REORGANIZATION.md](frontend/FRONTEND_REORGANIZATION.md)** (4 KB)
  - Frontend reorganization history

- **[frontend/VIDEO_REMOVAL_SUMMARY.md](frontend/VIDEO_REMOVAL_SUMMARY.md)** (4 KB)
  - Video removal and optimization

---

## External Resources

### Phosphobot (Robot SDK)
- **Location**: `phosphobot/` (Git subtree)
- **Repository**: github.com/hafnium49/phosphobot
- **Documentation**: `phosphobot/README.md` (7 KB)
- **Dashboard**: React/TypeScript web interface

### Demo2Rule (Dataset Conversion)
- **Location**: `aloha-lite-demo2rule/` (Git subtree)
- **Repository**: github.com/hafnium49/aloha-lite-demo2rule
- **Documentation**: `aloha-lite-demo2rule/README.md`

### Sample Code
- **Location**: `examples/` and `phosphobot/examples/`
- **Types**:
  - Trajectory examples
  - Joint reader examples
  - Voice command examples
  - Hand tracking examples

---

## Error Logs & Debugging

### Error Tracking
- **[error_log.md](error_log.md)** (72 KB)
  - Historical error log with solutions

### Diagnostics Tools
- `utilities/verify_installation.py` - System verification
- `utilities/servo_diagnosis.py` - Servo troubleshooting
- `utilities/joint_reader.py` - Joint diagnostics
- `utilities/trajectory_planner.py` - Trajectory validation

---

## Documentation Standards

### File Organization
- Service docs: Service directory READMEs
- Feature docs: Root-level .md files
- Config docs: Feature-specific guides
- Troubleshooting: WINDOWS_TROUBLESHOOTING.md, error_log.md

### Content Standards
- Clear examples with code blocks
- Markdown formatting with headers
- Links to related documentation
- Updated timestamps where applicable

---

## Quick Navigation

### By Role

**New to ALOHA-Lite?**
→ Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**System Administrator?**
→ Read [README.md](README.md) "Running Locally" and "Production Deployment"

**Software Developer?**
→ See [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md) and [ARCHITECTURE_DETAILS.md](ARCHITECTURE_DETAILS.md)

**ML Engineer?**
→ Check [frontend/ML_OPTIMIZATION_README.md](frontend/ML_OPTIMIZATION_README.md)

**Roboticist?**
→ Review [robot_service/README.md](robot_service/README.md) and [utilities/TRAJECTORY_PLANNER_README.md](utilities/TRAJECTORY_PLANNER_README.md)

**Operations/Support?**
→ See troubleshooting sections and [error_log.md](error_log.md)

---

## Last Updated
Generated: 2025-10-20
Repository: ALOHA-Lite
Version: 3.1 (Washing Bottle Volume Splitting System)

---

## Contributing to Documentation

To improve documentation:
1. Check existing files for related content
2. Update relevant .md files
3. Update this index if adding new documentation
4. Follow Markdown formatting standards
5. Include code examples where helpful
6. Link to related documentation
7. Update timestamps in documents

---

Need help? Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) troubleshooting section or review [error_log.md](error_log.md).
