# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ALOHA-Lite is a sophisticated robotics platform for bilateral teleoperation and autonomous manipulation. It combines FastAPI microservices, advanced computer vision (SAM2), and machine learning optimization for precise robot control.

## Essential Commands

### Development Server
```bash
# Start all services (requires Docker)
make start

# Start individual services
python -m uvicorn robot_control_service:app --reload --port 8001
python -m uvicorn frontend_ml_service:app --reload --port 8002
python -m uvicorn vision_processing_service:app --reload --port 8003
python mcp_server.py
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_robot_positions.py -v

# Run tests for a specific service
pytest tests/test_frontend_ml_service.py::TestColorOptimization -v
```

### Build and Deploy
```bash
# Build Docker images
docker-compose build

# Deploy with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f [service_name]
```

### Robot Calibration
```bash
# Capture new robot position
python scripts/capture_position.py --name "pick_paper" --arm left

# Validate robot configurations
python scripts/validate_robot_config.py

# Test specific robot procedure
python scripts/test_procedure.py --procedure "pick_paper_bilateral"
```

## Architecture

### Service Architecture
The system consists of 5 interconnected FastAPI services:

1. **robot_control_service** (port 8001): Direct robot hardware control via dynamixel_sdk
2. **frontend_ml_service** (port 8002): ML optimization and color targeting
3. **vision_processing_service** (port 8003): SAM2 integration for object detection
4. **mcp_server.py**: Model Context Protocol for LLM integration
5. **api_gateway** (port 8000): Traefik reverse proxy for service routing

Services communicate via REST APIs with shared authentication tokens.

### Key Architectural Patterns

**Configuration-Driven Execution**: All robot movements defined in JSON configs under `robot_procedures/`. No hardcoded positions in application code.

**ML Optimization Pipeline**:
- Bayesian optimization with Gaussian Process surrogate model
- Hue-only CIELAB color space for robust color matching
- Real-time feedback loop: capture → optimize → predict → validate

**Safety-First Design**:
- Single-arm operation enforcement
- Position validation before execution
- Graceful error handling with detailed logging
- Hardware limits enforced at driver level

### Data Flow
```
LeRobot Dataset → JSON Procedures → Robot Control Service → Hardware
                                  ↓
                        Frontend ML Service → Vision Processing
                                  ↓
                          Optimization Results
```

## Critical Implementation Details

### Robot Position Format
Positions in `robot_procedures/positions/` must include:
```json
{
  "joint_values": [j1, j2, j3, j4, j5, j6],  // 6 joints per arm
  "arm": "left" | "right",
  "capture_details": {
    "real_time_capture": true,
    "timestamp": "ISO-8601"
  }
}
```

### Service Communication
All inter-service calls require:
```python
headers = {"Authorization": f"Bearer {os.getenv('SERVICE_AUTH_TOKEN')}"}
response = requests.post(f"http://{service}:{port}/endpoint", headers=headers, json=data)
```

### ML Optimization Constraints
- Color targets: Hue angle only (0-360°)
- Convergence: <10° hue difference
- Max iterations: 100 (configurable)
- Acquisition function: Expected Improvement (EI)

### Vision Processing Pipeline
1. SAM2 attempts segmentation with point prompts
2. Falls back to color-based detection if confidence <0.8
3. Returns bounding boxes with confidence scores
4. Caches results for 60 seconds

## Environment Configuration

Required environment variables in `.env`:
```
SERVICE_AUTH_TOKEN=your-secret-token
OPENAI_API_KEY=your-api-key  # For MCP server
ROBOT_PORT=/dev/ttyUSB0      # Dynamixel interface
```

## Testing Approach

- Unit tests for individual services in `tests/`
- Integration tests for service communication
- Hardware simulation with mock Dynamixel SDK
- Position validation tests for all robot configs
- ML convergence tests with synthetic data

## Common Development Tasks

### Adding New Robot Position
1. Use `scripts/capture_position.py` to record joint values
2. Position automatically saved to `robot_procedures/positions/`
3. Update procedure JSON to reference new position
4. Run `scripts/validate_robot_config.py` to verify

### Modifying ML Optimization
1. Edit `frontend_ml_service.py::optimize_color_target()`
2. Adjust hyperparameters in `ML_CONFIG`
3. Test with `pytest tests/test_frontend_ml_service.py::TestColorOptimization`
4. Validate convergence metrics

### Debugging Vision Processing
1. Enable debug mode: `DEBUG_VISION=true`
2. Check segmentation masks in `/tmp/vision_debug/`
3. Review confidence scores in service logs
4. Test with `scripts/test_vision_pipeline.py`

## Performance Considerations

- Robot control loop: 50Hz update rate required
- Vision processing: ~200ms per frame with SAM2
- ML optimization: ~5s for convergence (100 iterations)
- Service latency: <50ms inter-service communication
- Memory: SAM2 model requires ~4GB GPU RAM

## Safety Protocols

- Never operate both arms simultaneously
- Validate all positions before execution
- Monitor joint torque limits (defined in hardware config)
- Emergency stop: `Ctrl+C` or hardware E-stop button
- Log all movements for audit trail