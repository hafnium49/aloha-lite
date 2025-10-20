# ALOHA-Lite Codebase Comprehensive Overview

## Executive Summary

**ALOHA-Lite** is an advanced robotics automation system designed for laboratory and manufacturing tasks, with a focus on color mixing, beaker analysis, and multi-arm robot control. It combines modular microservices architecture with machine learning optimization and vision AI, all orchestrated through Docker containers and exposed via REST APIs.

**Repository Size:** 63MB | **Total Files:** 339 Python/TypeScript files | **Language:** Primarily Python 3.8+

---

## 1. Project Type & Purpose

### Core Function
ALOHA-Lite is a **full-stack robot control and laboratory automation platform** built on top of the **Phosphobot SDK**. It enables:

- **Dual-arm SO-101 robot control** via JSON configurations and web APIs
- **Intelligent color mixing** with ML-powered Bayesian optimization
- **Hue-only target optimization** using CIELAB color space mathematics
- **AI-powered vision analysis** with Segment Anything 2 (SAM2) integration
- **Data-driven robot learning** from LeRobot v2 datasets
- **Multi-step laboratory procedures** with precise timing and joint control

### Use Cases
1. **Laboratory automation**: Precise liquid dispensing and color matching in beakers
2. **Robot teleoperation training**: Convert human demonstrations to executable robot code
3. **ML-driven optimization**: Bayesian optimization for finding optimal mixing ratios
4. **Vision-based feedback**: Real-time color analysis with advanced segmentation

---

## 2. Overall Project Structure

```
aloha-lite/ (63MB total)
├── README.md                          # Comprehensive documentation (1000+ lines)
├── pyproject.toml                     # Python package configuration
├── requirements.txt                   # Core Python dependencies
├── environment.yml                    # Conda environment specification
├── docker-compose.yml                 # Multi-service orchestration
├── .env.example                       # Environment template
│
├── CORE SERVICES (5 FastAPI microservices)
│   ├── robot_service/                 # Robot control & dispensing API (FastAPI, port 8000)
│   │   ├── main.py                   # FastAPI service with Prometheus metrics
│   │   ├── execute_rules.py          # Config-based robot execution
│   │   ├── sequential_execute.py     # Multi-step procedure automation
│   │   ├── squeeze_bottle.py         # Bottle operations
│   │   ├── bottle_operations.py      # Advanced bottle handling
│   │   ├── multi_color_dispenser.py  # Multi-color dispensing
│   │   ├── README.md                 # Service documentation
│   │   └── tests/                    # Integration tests
│   │
│   ├── frontend/                      # Web UI & ML optimization (FastAPI, port 3000)
│   │   ├── main.py                   # FastAPI service with ML engine
│   │   ├── index.html                # Web interface (53KB)
│   │   ├── ML_OPTIMIZATION_README.md # ML system documentation
│   │   ├── ground_truth_calibration/ # Calibration matrices
│   │   ├── washing_bottle_calibration/ # Volume calibration data
│   │   └── tests/                    # 19+ ML test suite
│   │
│   ├── vision_bridge/                 # Computer vision service (FastAPI, port 5000)
│   │   ├── main.py                   # FastAPI service with SAM2 integration
│   │   ├── beaker_analysis.py        # Color detection & K-means clustering
│   │   ├── setup_sam2.py             # SAM2 model setup script
│   │   ├── SAM2_SETUP_GUIDE.md       # Vision AI documentation
│   │   └── tests/                    # Vision tests
│   │
│   ├── mcp_server/                    # Claude Desktop integration (FastAPI, port 8900)
│   │   ├── main.py                   # MCP server with Playwright integration
│   │   ├── server.py                 # Entry point
│   │   ├── system_prompt.md          # Claude system instructions (Japanese)
│   │   └── notebooks/                # MCP usage examples
│   │
│   └── phosphobot/                    # Robot control core (Git subtree)
│       ├── phosphobot/               # Core robot module
│       ├── dashboard/                # Web dashboard (React/TypeScript)
│       ├── examples/                 # Usage examples
│       └── README.md                 # Phosphobot documentation
│
├── DATASET & PROCESSING
│   ├── aloha-lite-demo2rule/         # Dataset conversion (Git subtree)
│   │   ├── demo2rules.py             # Demo to rules converter (LeRobot → executable code)
│   │   ├── extract_at_time.py        # Time-based joint extraction
│   │   └── README.md                 # Conversion documentation
│   │
│   └── temp_rules/                    # Configuration & data storage
│       ├── robot_configurations.json  # 43KB config file with dual-arm/single-arm positions
│       ├── sequential_sequences.json  # 17KB multi-step procedure definitions
│       └── *.json                     # Testing & beaker analysis configs
│
├── UTILITIES & DIAGNOSTICS
│   ├── utilities/                     # Development & diagnostic tools
│   │   ├── trajectory_planner.py     # ModernRobotics trajectory planning
│   │   ├── joint_reader.py           # Robot joint position reading
│   │   ├── servo_diagnosis.py        # Servo troubleshooting & calibration
│   │   ├── ground_truth_calibrator.py # Calibration matrix generation
│   │   ├── verify_installation.py    # System health check
│   │   └── tests/                    # Utility tests
│   │
│   ├── examples/                      # Sample code & demonstrations
│   │   ├── trajectory_example.py      # Basic trajectory usage
│   │   ├── trajectory_executor.py     # Advanced trajectory execution
│   │   └── joint_reader_examples.py   # Joint reading examples
│   │
│   └── tests/                         # Top-level integration tests
│       ├── test_robot_service.py      # Robot service tests
│       ├── test_vision_bridge.py      # Vision service tests
│       └── CONDA_SETUP.md             # Environment setup guide
│
├── CONFIGURATION & DEPLOYMENT
│   ├── scripts/                       # Setup & utility scripts
│   │   └── setup-minio.sh            # MinIO configuration
│   ├── docker-compose.yml             # Service orchestration with Traefik
│   ├── setup.sh                       # Installation script
│   ├── push_subtree.sh                # Git subtree management
│   └── requirements-dev.txt           # Development dependencies
│
└── DOCUMENTATION
    ├── COLOR_RATIO_IMPLEMENTATION.md
    ├── error_log.md
    ├── robot_service/README.md        # Robot service deep dive
    ├── frontend/README.md             # Frontend & ML documentation
    ├── vision_bridge/README.md        # Vision service documentation
    ├── mcp_server/README.md           # MCP server documentation
    └── [20+ additional MD files]      # Feature & integration docs
```

---

## 3. Technology Stack & Languages

### Backend
- **Python 3.8+** (primary language)
  - FastAPI 0.100+ (5 microservices)
  - Uvicorn (ASGI server)
  - Modern_robotics (trajectory planning via PyPI)
  - SciPy + scikit-learn (ML optimization)
  - OpenCV (vision processing)
  - Pydantic (data validation)
  - Prometheus (metrics)

### Frontend
- **HTML5 + JavaScript** (index.html, 53KB)
- **React/TypeScript** (Phosphobot dashboard)
- Glass-morphism UI design
- Real-time WebSocket updates

### Infrastructure
- **Docker & Docker Compose** (multi-service orchestration)
- **Traefik** (API gateway/load balancer, port 8080)
- **MinIO** (S3-compatible object storage, ports 9000/9001)
- **ZMQ** (robot state publishing)
- **WebSocket** (real-time communication)

### CI/CD & Development
- **pytest** (testing framework)
- **black** (code formatting)
- **flake8** (linting)
- **mypy** (type checking)
- **Git subtrees** (modular repository management)

---

## 4. Build System & Configuration Files

### Package Management
- **pyproject.toml** (modern Python packaging)
  - Main dependencies: numpy, requests, modern_robotics, typeguard
  - Optional groups: frontend, robot, vision, mcp, dev, analysis
  - Defines entry points: aloha-lite, aloha-frontend, aloha-robot-service, etc.
  - Black, mypy, pytest configuration included

### Environment Configuration
- **.env.example**: Template with Phosphobot, S3, and MinIO settings
- **environment.yml**: Conda environment (Python 3.11 + 30+ packages)
- **docker-compose.yml**: 4-service orchestration (Traefik, MinIO, Robot Service, Vision Bridge, Frontend)

### Service Dockerfiles
- Minimal Dockerfiles in robot_service/, frontend/, vision_bridge/, mcp_server/
- Base image strategy: lightweight Python environments
- Mounted volumes for config files

---

## 5. Testing Setup

### Test Framework: pytest

### Test Coverage Areas

#### Unit Tests
```
frontend/tests/
├── test_setup.py                      # Frontend setup validation
├── test_api_endpoints.py              # API endpoint testing
├── test_four_rule_target_generator.py # ML optimization tests
└── test_normalization_10.py           # Color space tests

vision_bridge/tests/
├── test_beaker_analysis.py            # Beaker detection tests
├── test_color_checker.py              # Color checker detection
├── test_sam2_integration.py           # SAM2 model tests
└── test_consolidated_service.py       # Integration tests

utilities/tests/
└── test_ground_truth_calibrator.py    # Calibration tests

robot_service/tests/
├── test_robot_service.py              # Service tests
└── test_complete_system.py            # End-to-end tests
```

#### Integration & API Tests
```
tests/ (top-level)
├── test_robot_service.py              # Full service validation
├── test_vision_bridge.py              # Vision service validation
├── test_mcp_server.py                 # MCP server validation
└── verify_conda_setup.py              # Environment validation
```

### Running Tests
```bash
# All tests
pytest tests/

# Specific category
pytest frontend/tests/
pytest vision_bridge/tests/
pytest utilities/tests/

# With coverage
pytest --cov=frontend --cov=robot_service --cov=vision_bridge
```

### Test Configuration (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["frontend", "robot_service", "vision_bridge", "mcp_server"]
```

---

## 6. Key Architectural Patterns

### 1. Microservices Architecture
Five independent FastAPI services with clear responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    Traefik (Port 8080)                     │
│                   API Gateway & Load Balancer               │
└──────────┬──────────┬──────────┬──────────┬─────────────────┘
           │          │          │          │
    ┌──────▼──┐ ┌────▼───┐ ┌──▼──────┐ ┌─▼──────┐
    │ Frontend│ │ Robot  │ │ Vision  │ │ MCP    │
    │ (3000)  │ │(8000)  │ │ (5000)  │ │(8900)  │
    └──────┬──┘ └────┬───┘ └──┬──────┘ └─┬──────┘
           │         │        │         │
           └─────────┴────────┴─────────┘
                      │
              Phosphobot SDK
              Robot Control Core
```

### 2. Configuration-Based Execution
- JSON-based robot configurations stored in `temp_rules/`
- Dual-arm, left-arm-only, right-arm-only support
- Time-based extraction from demonstration data
- Safe default behavior (no initialization)

### 3. ML Optimization Engine (Frontend Service)
- **Bayesian Optimization** with Gaussian Process Regression
- **Hue-Only Target Optimization** using CIELAB color space
- **Angular distance calculations** for perceptual accuracy
- **Ground truth calibration** integration from robot experiments
- **Adaptive phase scheduling** (4-phase strategy)
- **Real-time recommendations** with confidence scoring

### 4. Vision Processing Pipeline
- **Circle detection** (traditional CV fallback)
- **SAM2 integration** (Meta's Segment Anything Model 2.1)
- **K-means clustering** for color analysis
- **Center-weighted detection** for beaker positioning
- **Graceful fallback** when SAM2 unavailable

### 5. Operational Workflow
1. **Dataset to Config**: LeRobot → demo2rules.py → JSON configuration
2. **Configuration Execution**: JSON config → execute_rules.py → robot movement
3. **Sequential Procedures**: Multi-step workflows with timing control
4. **Real-time Feedback**: Vision analysis → Color recommendations → Adjustment

### 6. State Management
- **ZMQ publishing**: Robot state broadcasted in real-time
- **JSON-based config persistence**: Reproducible configurations
- **Prometheus metrics**: Performance monitoring (ports 9001, 9003)
- **Background task tracking**: Async operation management

---

## 7. Documentation Structure

### Primary Documentation
1. **README.md** (45KB)
   - Quick start, installation, basic usage
   - Architecture overview and API endpoints
   - Production deployment guide
   - 1000+ lines of comprehensive coverage

2. **Service-Specific READMEs**
   - robot_service/README.md (24KB)
   - frontend/README.md (40KB)
   - vision_bridge/README.md (13KB)
   - mcp_server/README.md (8KB)
   - phosphobot/README.md (7KB)

### Feature Documentation
- COLOR_RATIO_IMPLEMENTATION.md - Color mixing system
- ML_OPTIMIZATION_README.md - Bayesian optimization & hue targeting
- SAM2_SETUP_GUIDE.md - Vision AI setup
- TRAJECTORY_PLANNER_README.md - Joint trajectory planning
- JOINT_READER_GUIDE.md - Joint diagnostics
- SERVO_DIAGNOSIS_GUIDE.md - Servo troubleshooting
- MIGRATION_SUMMARY.md (multiple)
- ENHANCED_FEATURES.md

### Configuration Guides
- PARTIAL_CONFIG_GUIDE.md
- CONDA_SETUP.md
- LEFT_ARM_STANDOFF_WITH_BEAKER.md
- BOTTLE_OPERATIONS_UPDATE.md
- SQUEEZE_BOTTLE_REFACTOR.md

### Special Documentation
- **mcp_server/system_prompt.md** (Japanese instructions for Claude Desktop)
- **frontend/USER_MANUAL_JA.md** (Japanese user manual)
- **WINDOWS_TROUBLESHOOTING.md** (Windows-specific setup)

---

## 8. Key Dependencies & External Integrations

### Core Dependencies
```
numpy>=1.20.0                    # Numerical computing
requests>=2.25.0                 # HTTP client
modern_robotics>=1.0.0           # Trajectory planning
typeguard                        # Type checking

# FastAPI Services
fastapi>=0.100.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0

# ML & Data Science
scipy>=1.7.0
scikit-learn>=1.0.0
numpy>=1.20.0

# Vision
opencv-python>=4.5.0
pillow>=8.0.0
torch                            # For SAM2

# Infrastructure
prometheus-client                # Metrics
pyzmq                           # ZMQ messaging
boto3                           # S3 client
```

### External Services
1. **Phosphobot SDK** - Robot control (HTTP/ZMQ)
2. **Hugging Face Hub** - LeRobot dataset hosting
3. **MinIO** - S3-compatible storage (local or cloud)
4. **Traefik** - API gateway
5. **Segment Anything 2** - AI vision model
6. **Meta's SAM2** - Advanced segmentation

### Optional Dependencies
- SAM2 models (downloadable, ~100MB+)
- Ground truth calibration matrices
- LeRobot demonstration datasets

---

## 9. Development Workflow & Patterns

### Configuration Management
1. **Extract from demonstration**: `demo2rules.py` from LeRobot dataset
2. **Store in JSON**: Add to `temp_rules/robot_configurations.json`
3. **Execute configuration**: `execute_rules.py --config name`
4. **Sequential procedures**: Chain multiple configs with timing

### Robot Control Flow
```
User Request
    ↓
Frontend Service (Port 3000)
    ├─ ML Optimization (Bayesian GPR)
    ├─ Hue-only target calculation
    └─ Proxy to Robot Service
         ↓
    Robot Service (Port 8000)
         ├─ Load configuration
         ├─ Trajectory planning (ModernRobotics)
         └─ Execute via Phosphobot SDK
              ↓
    Phosphobot Core
         ├─ ZMQ state publishing
         └─ Direct joint control
    ↓
Vision Bridge (Port 5000)
    ├─ Capture camera snapshot
    ├─ SAM2 segmentation (optional)
    ├─ Color analysis (K-means)
    └─ Return results to Frontend
    ↓
Frontend displays results + ML recommendations
```

### Development Environment
- **Conda environment**: Python 3.11 with 30+ packages
- **Local development**: Set `REQUIRE_MODEL=false`, `REQUIRE_ROBOT=false`, `REQUIRE_S3=false`
- **Production mode**: Full dependencies with GPU support
- **Docker Compose**: Full stack in containers for testing

---

## 10. Version Control & Subtrees

### Git Subtrees
```
phosphobot/              → github.com/hafnium49/phosphobot
aloha-lite-demo2rule/    → github.com/hafnium49/aloha-lite-demo2rule
```

### Subtree Management Scripts
- `push_subtree.sh` - Bash script with automatic fallback
- `utilities/push_subtree.py` - Python alternative
- Features: .gitignore handling, colored output, error recovery

### Recent Commits
- f2e2147: Right arm joint values update
- db4d215: Pick paper workflow with bilateral manipulation
- cf6c7da: Right arm standoff paper position
- 88579a7: Left arm pick paper position
- 4d39d8b: Left arm grip paper position

---

## 11. Notable Features & Innovations

### ML-Enhanced Color Optimization
- **Hue-only targeting**: CIELAB color space with angular distance
- **Bayesian optimization**: Gaussian Process learns optimal ratios
- **Ground truth calibration**: Real robot-generated matrices
- **Volume splitting**: Automatic division of >4mL into ≤4mL segments
- **Adaptive scheduling**: 4-phase strategy based on configuration

### Advanced Vision Processing
- **SAM2 integration**: Meta's Segment Anything Model 2.1
- **Hybrid analysis**: Circle detection + AI segmentation
- **K-means clustering**: Color analysis with center-weighted detection
- **Graceful fallback**: Works without SAM2 models

### Robot Control Features
- **Dual-arm support**: Synchronized two-arm movements
- **Single-arm safety**: Move one arm while keeping other steady
- **Four-arm configuration**: Configurable arm IDs
- **Trajectory planning**: ModernRobotics library integration
- **Sequential procedures**: Multi-step automation with timing

### Laboratory Automation
- **29-step procedures**: Timed liquid dispensing workflows
- **Beaker analysis**: Real-time color detection and feedback
- **Multi-color dispensing**: Configurable color ratios
- **Safety-first defaults**: No initialization by default

---

## 12. Deployment & Operations

### Docker Compose Stack (Production)
```yaml
Services:
- Traefik (API gateway, port 8080)
- MinIO (S3 storage, ports 9000/9001)
- Robot Service (port 8000)
- Vision Bridge (port 5000)
- Frontend (port 3000)
- MCP Server (port 8900, optional)
```

### Service Health Checks
```bash
curl http://localhost:3000/status              # Frontend health
curl http://localhost:8000/health              # Robot service
curl http://localhost:5000/health              # Vision service
curl http://localhost:8900/health              # MCP server
curl http://localhost:8080/                    # Gateway status
```

### Environment Variables
```
ROBOT_TYPE=simulator|so100|so101|wx250
PHOS_URL=http://phosphobot
MODEL_ID=phospho-app/so101_dispense_v1-groot
S3_ENDPOINT=http://minio:9000
REQUIRE_MODEL=true|false
REQUIRE_ROBOT=true|false
REQUIRE_S3=true|false
```

### Performance Metrics
- **Hue accuracy**: <10° angular distance
- **Color accuracy**: <5.0 Delta-E
- **Convergence**: 5-8 iterations (white-locked), 7-12 (learnable)
- **Real-time performance**: <1s ML recommendations

---

## 13. Common Use Patterns

### Laboratory Automation
```bash
# 1. Move to standoff
python3 execute_rules.py --config standoff_configuration_stage1

# 2. Execute procedure
python3 execute_rules.py --config dispensing_water_to_beaker

# 3. Return to standoff
python3 execute_rules.py --config standoff_configuration_stage1
```

### Dataset to Robot
```bash
# Extract rules
cd aloha-lite-demo2rule
python3 demo2rules.py --dataset Hafnium49/aloha_lite --episode 1

# Execute
cd ..
python3 execute_rules.py --config new_configuration
```

### ML Color Optimization
```bash
# Frontend provides:
# 1. Target color generation
# 2. ML ratio recommendations
# 3. Hue-based visualization
# 4. Real-time optimization loop
```

---

## 14. File Organization Insights

### Large Files
- `robot_service/main.py` (38KB) - Robot API and control logic
- `frontend/main.py` (73KB) - ML optimization and proxy logic
- `vision_bridge/main.py` (40KB) - Vision processing and SAM2
- `mcp_server/main.py` (21KB) - Playwright integration
- `frontend/index.html` (53KB) - Complete web interface
- `robot_service/execute_rules.py` (47KB) - Configuration execution
- `robot_service/sequential_execute.py` (59KB) - Multi-step automation
- `temp_rules/robot_configurations.json` (43KB) - 100+ configurations
- `temp_rules/sequential_sequences.json` (17KB) - 10+ procedures

### Configuration Files
- JSON: Robot positions, sequences, calibration data
- YAML: Docker compose, environment specifications
- MD: 30+ documentation files

### Python Modules
- Service main files (FastAPI)
- Domain logic (trajectory, calibration, analysis)
- Utilities (diagnostics, verification, conversion)
- Tests (integration, unit, API)

---

## 15. Integration Points & APIs

### Internal Communication
- **HTTP**: FastAPI service-to-service (proxy pattern)
- **ZMQ**: Robot state publishing (real-time)
- **WebSocket**: MCP client-server, live updates

### External APIs (via Phosphobot)
- `/joints/write` - Set joint positions
- `/joints/read` - Read current positions
- `/move/init` - Robot initialization
- Skill-based execution (if ML inference enabled)

### Frontend Exposed APIs
- `GET /api/target-color` - Random target generation
- `POST /api/recommend-ratios` - ML recommendations
- `GET /api/hue-visual-data` - Visualization data
- `POST /robot/dispense` - Proxy to robot service
- `POST /vision/analyze-beaker` - Proxy to vision service

---

## Summary

ALOHA-Lite is a **sophisticated, production-ready robotics platform** combining:
- **Modern microservices architecture** with FastAPI
- **Advanced ML** (Bayesian optimization, hue-targeting)
- **State-of-the-art vision AI** (SAM2 integration)
- **Safe robot control** (configuration-based, single-arm support)
- **Comprehensive documentation** (30+ guides)
- **Test coverage** (19+ ML tests, integration tests, unit tests)
- **Real-world deployment** (Docker, Prometheus, S3 storage)

The project demonstrates best practices in robotics software engineering, with clear separation of concerns, extensive configuration management, and rigorous focus on safety and reproducibility.
