# ALOHA-Lite Quick Reference Guide

## Project At a Glance

| Aspect | Details |
|--------|---------|
| **Type** | Advanced robotics platform with ML optimization |
| **Language** | Python 3.8+ (339 files) |
| **Size** | 63MB, 1000+ lines documentation |
| **Architecture** | 5 FastAPI microservices + Phosphobot SDK |
| **Main Purpose** | Color mixing, beaker analysis, multi-arm robot control |
| **Target Robot** | SO-101 dual-arm manipulator (via Phosphobot) |

---

## Quick Start

### Installation
```bash
# Clone and setup
git clone <repo-url> && cd aloha-lite

# Option 1: Conda (recommended)
conda env create -f environment.yml
conda activate aloha-lite

# Option 2: Pip
pip install -r requirements.txt

# Option 3: Automated script
./setup.sh
```

### Running Services
```bash
# Development mode (no hardware/ML/S3 required)
export REQUIRE_MODEL=false REQUIRE_ROBOT=false REQUIRE_S3=false

# Start all services
docker-compose up --build -d

# Or start individually
cd robot_service && uvicorn main:app --port 8000 &
cd frontend && uvicorn main:app --port 3000 &
cd vision_bridge && uvicorn main:app --port 5000 &
```

### Access Points
- **Web UI**: http://localhost:3000
- **Robot API**: http://localhost:8000/docs
- **Vision API**: http://localhost:5000/docs
- **Gateway**: http://localhost:8080
- **MinIO Console**: http://localhost:9001

---

## Directory Structure Quick Map

```
robot_service/        → Robot control & dispensing (port 8000)
frontend/            → Web UI & ML optimization (port 3000)
vision_bridge/       → Computer vision & SAM2 (port 5000)
mcp_server/          → Claude Desktop integration (port 8900)
phosphobot/          → Robot SDK core (subtree)
aloha-lite-demo2rule/ → Dataset conversion (subtree)
utilities/           → Diagnostic & development tools
examples/            → Sample code & demonstrations
tests/               → Integration & unit tests
temp_rules/          → Robot configs & procedures
scripts/             → Deployment & setup
```

---

## Core Features in 30 Seconds

### 1. ML-Enhanced Color Mixing
- Bayesian optimization with Gaussian Process Regression
- Hue-only targeting using CIELAB color space
- Ground truth calibration from robot experiments
- Real-time ratio recommendations with confidence scores

### 2. Advanced Vision Processing
- SAM2 (Segment Anything 2) integration for beaker detection
- K-means clustering for color analysis
- Graceful fallback to circle detection when SAM2 unavailable
- Real-time frame analysis with center-weighted detection

### 3. Flexible Robot Control
- Configuration-based execution (JSON → robot movement)
- Dual-arm, left-arm-only, right-arm-only support
- Trajectory planning via ModernRobotics library
- Sequential procedures for multi-step tasks

### 4. Dataset Processing
- Convert LeRobot v2 demonstrations to executable code
- Time-based joint extraction at specific timestamps
- Multiple output formats (Python, CSV, JSON)
- Direct integration with Phosphobot SDK

---

## Key Commands

### Robot Operations
```bash
# Execute configuration
python3 robot_service/execute_rules.py --config dispensing_water_to_beaker

# Sequential procedure
python3 robot_service/sequential_execute.py standoff_to_dispensing

# List available configs
python3 robot_service/execute_rules.py

# Specify arm IDs (for 4-arm systems)
python3 robot_service/execute_rules.py --config my_config --left-arm-id 3 --right-arm-id 2
```

### Dataset Processing
```bash
# Extract rules from dataset
cd aloha-lite-demo2rule
python3 demo2rules.py --dataset Hafnium49/aloha_lite --episode 1 --out rules.py

# Extract at specific timestamp
python3 extract_at_time.py Hafnium49/aloha_lite 1 4.2

# Generate CSV for analysis
python3 demo2rules.py --dataset ... --episode ... --out file.csv --format csv
```

### Diagnostics
```bash
# Verify installation
python3 utilities/verify_installation.py

# Read joint positions
python3 utilities/joint_reader.py --arm left

# Trajectory planning
python3 utilities/trajectory_planner.py --config your_config

# Servo diagnosis
python3 utilities/servo_diagnosis.py --joint 3 --fix-deadband

# Calibration
python3 utilities/ground_truth_calibrator.py
```

---

## API Quick Reference

### Frontend Service (Port 3000)

```
GET /api/target-color
  Returns random target color for optimization

POST /api/recommend-ratios
  Input: {history: [...]}
  Returns: {red: 1.2, yellow: 0.8, blue: 1.0, confidence: 0.95}

GET /api/hue-visual-data
  Returns polar dial data for visualization

POST /robot/dispense
  Proxy to robot service

POST /vision/analyze-beaker
  Proxy to vision service
```

### Robot Service (Port 8000)

```
POST /robot/dispense
  {color: "red|yellow|blue|mixed", duration: 2.0, color_ratios: {...}}

GET /robot/{cmd_id}/status
  Returns operation status

GET /robot/{cmd_id}/beaker-analysis
  Returns vision analysis results

POST /joints/write?robot_id=0
  Set joint positions

POST /joints/read?robot_id=0
  Read current joint positions
```

### Vision Bridge (Port 5000)

```
POST /analyze-beaker
  {image_data: "base64"} → {dominant_color, delta_e, confidence}

POST /snap
  Capture camera snapshot

POST /color-checker
  Analyze color checker patterns

GET /health
  Service health check
```

---

## Configuration Files

### Robot Configurations (temp_rules/robot_configurations.json)
- 100+ pre-defined robot positions
- Dual-arm and single-arm variants
- Source metadata and usage examples
- Arm ID configuration support

### Sequential Procedures (temp_rules/sequential_sequences.json)
- Multi-step automation workflows
- Timing control between steps
- Mixed arm configuration support
- 10+ predefined sequences

### Environment (.env)
```
ROBOT_TYPE=simulator|so100|so101|wx250
PHOS_URL=http://phosphobot
MODEL_ID=phospho-app/so101_dispense_v1-groot
S3_ENDPOINT=http://minio:9000
REQUIRE_MODEL=true|false
REQUIRE_ROBOT=true|false
REQUIRE_S3=true|false
```

---

## Development Workflow

### Adding New Robot Configurations
1. Extract from dataset: `demo2rules.py --dataset ... --episode ...`
2. Get precise joints at timestamp: `extract_at_time.py ... timestamp`
3. Add to `temp_rules/robot_configurations.json`
4. Test: `execute_rules.py --config your_config`

### Working with ML Optimization
- ML engine runs in Frontend service
- Bayesian GPR learns from color mixing experiments
- Hue-only optimization for perceptually accurate matching
- Real-time recommendations with confidence scoring

### Testing
```bash
pytest tests/                              # All tests
pytest frontend/tests/ -v                  # Frontend tests
pytest vision_bridge/tests/ -v             # Vision tests
pytest --cov=frontend --cov=robot_service  # Coverage report
```

---

## Troubleshooting Quick Fixes

### Service won't start
```bash
# Check logs
docker-compose logs robot_service
# Verify environment variables
env | grep -E "REQUIRE_|ROBOT_|MODEL_|S3_"
# Try development mode
export REQUIRE_MODEL=false REQUIRE_ROBOT=false REQUIRE_S3=false
```

### Robot not responding
```bash
# Check Phosphobot connection
curl http://localhost:80/health
# Verify robot type
echo $ROBOT_TYPE
# Check joint positions
python3 utilities/joint_reader.py --arm left
```

### Vision service errors
- **SAM2 not found**: Optional - system falls back to circle detection
- **S3 connection failed**: Use `REQUIRE_S3=false` for development
- **Camera unavailable**: Vision returns placeholder results

### Configuration issues
- **Config not found**: `execute_rules.py` lists available configs
- **Joint validation fails**: Check `utilities/check_joint_limits.py`
- **Trajectory planning fails**: Validate with `utilities/trajectory_planner.py`

---

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| ML recommendation latency | <100ms | ~80ms |
| Vision analysis (SAM2) | - | 300-400ms |
| Vision analysis (fallback) | - | 50-70ms |
| Hue accuracy | <10° | <8° typically |
| Color accuracy | <5.0 ΔE | <4.0 typically |
| Convergence iterations | 5-12 | 5-8 (locked), 7-12 (learnable) |
| Robot move latency | <50ms | ~30ms |

---

## Important Files

### Documentation
- **README.md** (45KB) - Comprehensive guide
- **CODEBASE_OVERVIEW.md** - Project structure overview
- **ARCHITECTURE_DETAILS.md** - Deep dive into architecture
- **robot_service/README.md** - Robot service specifics
- **frontend/README.md** - Frontend & ML documentation
- **vision_bridge/SAM2_SETUP_GUIDE.md** - Vision AI setup

### Configuration
- **pyproject.toml** - Package metadata & dependencies
- **environment.yml** - Conda environment specification
- **docker-compose.yml** - Service orchestration
- **.env.example** - Environment template

### Source
- **robot_service/main.py** (38KB) - Robot API
- **frontend/main.py** (73KB) - ML & proxy
- **vision_bridge/main.py** (40KB) - Vision processing
- **mcp_server/main.py** (21KB) - Claude integration

---

## Key Concepts

### Hue-Only Optimization
Matches target hue (0-360°) instead of full RGB, using CIELAB color space angular distance. Achieves <10° accuracy in 5-8 iterations, matching human color perception.

### Ground Truth Calibration
Real robot-generated 4×3 calibration matrix (RGBA channels) that defines how each pigment absorbs light. Used to constrain and improve ML recommendations.

### Volume Splitting
Automatic division of dispensing volumes >4mL into equal ≤4mL segments (e.g., 5mL → 2×2.5mL) to stay within calibrated range and maintain accuracy.

### Configuration-Based Execution
Robot movements defined as JSON configs with joint values, source metadata, and arm types. Enables reproducible, reusable automation without hardware knowledge.

### SAM2 Fallback
Vision system uses Meta's Segment Anything 2 for advanced beaker detection when available, gracefully falls back to traditional circle detection (Hough) when not.

---

## Getting Help

### Documentation
- Service READMEs in each directory
- Feature-specific .md files in temp_rules/
- System prompt in mcp_server/system_prompt.md
- Examples in examples/ and phosphobot/examples/

### Debugging
1. Check logs: `docker-compose logs <service>`
2. Verify health: `curl http://localhost:3000/status`
3. Test APIs: `curl http://localhost:8000/docs`
4. Run diagnostics: `python3 utilities/verify_installation.py`

### Contributing
1. Fork repository
2. Create feature branch
3. Add configs to temp_rules/
4. Test with `execute_rules.py`
5. Update documentation
6. Submit PR

---

## Production Checklist

- [ ] Secure credentials in .env
- [ ] Configure SSL/TLS on Traefik
- [ ] Verify S3 storage and backups
- [ ] Calibrate robot hardware
- [ ] Download SAM2 models
- [ ] Load calibration matrices
- [ ] Enable monitoring (Prometheus)
- [ ] Configure alerting
- [ ] Test failover scenarios
- [ ] Document for ops team

---

Generated: 2025-10-20
ALOHA-Lite Repository Overview
