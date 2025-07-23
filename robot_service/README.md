# Robot Service

A FastAPI-based laboratory automation service for controlling robotic arms in multi-color dispensing, positioning, and analysis tasks. This service implements comprehensive timed laboratory procedures with real-time monitoring and progress tracking.

## Features

### 🤖 Complete Laboratory Automation
- **29-step timed laboratory procedure** with full workflow automation
- **Multi-color dispensing** support (red, yellow, blue)
- **Precise arm positioning** and coordination between left and right arms
- **Automated squeeze bottle operations** with configurable durations
- **Stirring capabilities** with timed execution
- **AI-powered beaker color analysis** 
- **Real-time progress tracking** with step-by-step status updates

### 🎯 Enhanced Trajectory Planning
- **Smooth trajectory generation** with joint 1 receiving 2x waypoint density
- **0.1 second timing configuration** for fast, precise movements
- **ModernRobotics integration** for optimal path planning

### 📊 Monitoring & Observability
- **Prometheus metrics** for request tracking and latency monitoring
- **Comprehensive logging** with structured error handling
- **Real-time status updates** via WebSocket-style monitoring
- **Background task management** with automatic cleanup

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│  Robot Service  │────│   Phosphobot    │
│   (Web UI)      │    │   (FastAPI)     │    │ (ML Inference)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │ Sequential Exec │
                       │ (Trajectory)    │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │ Execute Rules   │
                       │ (Joint Control) │
                       └─────────────────┘
```

## API Endpoints

### Core Dispensing

#### `POST /robot/dispense`
Execute laboratory procedures with multi-color dispensing support.

**Request Body:**
```json
{
  "mix_id": 1,
  "run_id": 1,
  "colour": "red",
  "color_ratios": {
    "red": 40.0,
    "yellow": 35.0,
    "blue": 25.0
  },
  "normalized_percentages": {
    "red": 40.0,
    "yellow": 35.0,
    "blue": 25.0
  },
  "base_duration": 3.0
}
```

**Response:**
```json
{
  "cmd_id": "uuid-string",
  "status": "pending",
  "procedure": "timed_laboratory_procedure",
  "description": "Complete laboratory workflow with positioning, dispensing, squeezing, stirring, waiting, and beaker analysis"
}
```

### Status Monitoring

#### `GET /robot/{cmd_id}/status`
Get real-time status of a laboratory procedure.

**Response:**
```json
{
  "status": "running",
  "request_id": "uuid-string",
  "current_operation": {
    "step": 15,
    "total_steps": 29,
    "description": "dispensing_blue_to_beaker",
    "status": "running"
  },
  "started_at": "2025-07-23 10:30:00",
  "completed_at": null,
  "error_message": null
}
```

### Procedure Information

#### `GET /robot/procedure/info`
Get detailed information about the timed laboratory procedure.

**Response:**
```json
{
  "procedure_name": "timed_laboratory_procedure",
  "description": "Complete laboratory workflow with multi-color dispensing, positioning, stirring, and analysis",
  "total_steps": 29,
  "features": [
    "Multi-color dispensing (red, yellow, blue)",
    "Precise arm positioning and coordination",
    "Automated squeeze bottle operations",
    "Stirring capabilities",
    "Timed delays for process control",
    "AI-powered beaker color analysis",
    "Real-time progress tracking"
  ],
  "sequence_overview": {
    "configurations": 23,
    "special_functions": 6,
    "colors_dispensed": ["red", "yellow", "blue"],
    "squeeze_operations": 3,
    "timing_delays": 2,
    "analysis_steps": 1
  },
  "timing": {
    "pause_between_steps": "0.1 seconds",
    "smooth_trajectory": True,
    "estimated_duration": "3-5 minutes"
  }
}
```

### Vision Integration

#### `GET /robot/{cmd_id}/pose-snapshot`
Capture a snapshot when the robot reaches the target pose.

**Query Parameters:**
- `cam`: Camera ID (default: "top_cam")

## Laboratory Procedure Sequence

The timed laboratory procedure implements a comprehensive 29-step workflow:

### Phase 1: Setup & Red Dispensing (Steps 1-6)
1. `left_arm_serving_standoff` - Initial positioning
2. `left_arm_standoff_with_beaker` - Position for dispensing
3. `dispensing_red_to_beaker` - Red color dispensing
4. `squeeze washing bottle for 1.5 seconds` - Cleaning operation
5. `right_arm_standoff` - Right arm positioning
6. `left_arm_standoff_with_beaker` - Return to dispensing position

### Phase 2: Yellow Dispensing (Steps 7-13)
7. `left_arm_standoff_yellow` - Position for yellow
8. `right_arm_standoff_yellow` - Right arm coordination
9. `dispensing_yellow_to_beaker` - Yellow color dispensing
10. `squeeze washing bottle for 2.5 seconds` - Extended cleaning
11. `right_arm_standoff_yellow` - Coordination
12. `right_arm_standoff` - Reset right arm
13. `left_arm_standoff_yellow` - Maintain yellow position

### Phase 3: Blue Dispensing (Steps 14-19)
14. `left_arm_standoff_blue` - Position for blue
15. `dispensing_blue_to_beaker` - Blue color dispensing
16. `squeeze washing bottle for 1 seconds` - Quick cleaning
17. `right_arm_standoff` - Right arm coordination
18. `left_arm_standoff_blue` - Maintain blue position
19. `left_arm_standoff_yellow` - Transition positioning

### Phase 4: Mixing & Analysis (Steps 20-29)
20. `left_arm_stirer_standoff` - Prepare for stirring
21. `left_arm_stirring` - Active stirring operation
22. `await 10 seconds` - Allow mixing time
23. `analyze beaker color` - AI-powered color analysis
24. `await 3 seconds` - Analysis processing time
25. `left_arm_stirer_standoff` - Exit stirring position
26. `left_arm_standoff_yellow` - Transition
27. `left_arm_standoff_with_beaker` - Final beaker position
28. `left_arm_serving_standoff` - Serving preparation
29. `left_arm_serving_beaker` - Final serving position

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PHOS_URL` | Phosphobot inference service URL | `http://phosphobot` |
| `MODEL_ID` | ML model identifier for inference | Required |
| `TARGET_POSE` | Target joint positions as JSON array | `[0,0,0,0,0,0]` |
| `TOL` | Position tolerance for pose detection | `0.03` |

## Dependencies

### Core Services
- **FastAPI**: Web framework and API server
- **Phosphobot**: ML inference service for motion planning
- **Vision-Bridge**: Camera capture and image processing
- **ZMQ**: Real-time state communication

### Execution Modules
- **sequential_execute.py**: Configuration execution with enhanced timing
- **execute_rules.py**: Joint control with 2x waypoint density for joint 1
- **squeeze_bottle.py**: Automated squeeze operations

### Configuration Files
- **dispensing_red_to_beaker.json**: Red dispensing configuration
- **dispensing_yellow_to_beaker.json**: Yellow dispensing configuration  
- **dispensing_blue_to_beaker.json**: Blue dispensing configuration
- **temp_rules/sequential_sequences.json**: Complete procedure definitions

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
export MODEL_ID="your-model-id"
export PHOS_URL="http://phosphobot:8080"
export TARGET_POSE="[0,0,0,0,0,0]"
```

### 3. Start the Service
```bash
python main.py
```

### 4. Docker Deployment
```bash
docker build -t robot-service .
docker run -p 8000:8000 robot-service
```

## Monitoring

### Prometheus Metrics
- **robot_requests_total**: Total number of dispense requests
- **robot_request_latency_seconds**: Request processing latency

### Health Checks
The service exposes metrics on port 9001 for Prometheus scraping.

### Logging
Structured logging provides detailed execution tracking:
```
INFO: Starting timed laboratory procedure for cmd_id=abc-123
INFO: Step 1/29: left_arm_serving_standoff
INFO: ✅ Completed step 1/29: left_arm_serving_standoff
INFO: Step 2/29: left_arm_standoff_with_beaker
...
INFO: 🎉 Timed laboratory procedure completed successfully
```

## Error Handling

### Timeout Management
- **Configuration timeout**: 60 seconds per step
- **Squeeze timeout**: Duration + 10 second buffer
- **Overall timeout**: Configurable per procedure

### Failure Recovery
- **Step-level errors**: Logged with specific error context
- **Task cleanup**: Automatic cleanup of old completed tasks
- **State recovery**: ZMQ state listener for real-time updates

### Common Error Codes
- **400**: Invalid color ratios or request parameters
- **404**: Command ID not found
- **408**: Timeout waiting for target pose
- **500**: Internal execution errors
- **502**: Phosphobot or Vision-Bridge service errors
- **504**: Service timeout errors

## Configuration

### Timing Parameters
The service supports flexible timing configuration:
- **Default pause between steps**: 0.1 seconds
- **Smooth trajectory**: Enabled for all movements
- **Joint 1 enhancement**: 2x waypoint density for smoother base rotation

### Color Ratios
Color ratios are normalized and used to adjust squeeze durations:
```python
# Example: 40% red, 35% yellow, 25% blue
color_ratios = {
    "red": 40.0,
    "yellow": 35.0, 
    "blue": 25.0
}
```

### Base Duration Scaling
Base duration affects squeeze timing calculations:
- **Minimum duration**: 0.5 seconds per color
- **Maximum duration**: 10.0 seconds per color
- **Proportional scaling**: Based on color ratio percentages

## Development

### Adding New Procedures
1. Define sequence in `temp_rules/sequential_sequences.json`
2. Add execution logic in `execute_multi_color_dispensing_task()`
3. Update procedure info endpoint
4. Add tests for new functionality

### Extending Color Support
1. Add new color to `CONFIG_MAP`
2. Create dispensing configuration JSON
3. Update validation patterns
4. Test with new color ratios

### Performance Optimization
- **Parallel execution**: Special functions can run concurrently
- **Trajectory caching**: Enhanced waypoint calculation with joint 1 optimization
- **Memory management**: Automatic task cleanup prevents memory leaks

## Troubleshooting

### Common Issues

#### Robot Not Responding
```bash
# Check ZMQ connection
curl http://localhost:8000/robot/procedure/info

# Verify Phosphobot connectivity
curl $PHOS_URL/health
```

#### Slow Execution
- Verify 0.1 second timing is configured
- Check joint 1 waypoint enhancement is active
- Monitor Prometheus metrics for bottlenecks

#### Color Analysis Failures
- Ensure Vision-Bridge service is running
- Check camera permissions and configuration
- Verify beaker is properly positioned

### Debug Commands
```bash
# Test individual configurations
python sequential_execute.py "left_arm_standoff_with_beaker" --smooth

# Test squeeze operations
python squeeze_bottle.py --duration 2.0

# Monitor real-time status
curl http://localhost:8000/robot/{cmd_id}/status
```

## License

This project is part of the ALOHA-Lite laboratory automation system.
