# ALOHA-Lite Architecture Deep Dive

## System Architecture Overview

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TRAEFIK Gateway (8080)                      │
│                      Load Balancer & Router                         │
└────┬───────────────┬──────────────┬──────────────┬──────────────────┘
     │               │              │              │
     │               │              │              │
  PORT 3000       PORT 8000      PORT 5000     PORT 8900
     │               │              │              │
     ▼               ▼              ▼              ▼
┌──────────┐  ┌────────────┐  ┌─────────────┐  ┌──────────┐
│ FRONTEND │  │   ROBOT    │  │   VISION    │  │   MCP    │
│ SERVICE  │  │  SERVICE   │  │  BRIDGE     │  │  SERVER  │
│ (FastAPI)│  │ (FastAPI)  │  │ (FastAPI)   │  │(FastAPI) │
│          │  │            │  │             │  │          │
│ Port 80  │  │ Port 80    │  │ Port 80     │  │ Port 80  │
│ (local)  │  │ (local)    │  │ (local)     │  │ (local)  │
└────┬─────┘  └──────┬─────┘  └──────┬──────┘  └────┬─────┘
     │               │              │              │
     │      HTTP Proxy Pattern      │              │
     └───────────┬──────────────────┘              │
                 │                                │
                 │ Internal Service               │ WebSocket
                 │ Communication                  │ to Claude
                 │                                │
         ┌───────▼─────────────┐           ┌─────▼──────┐
         │   PHOSPHOBOT SDK    │           │  Playwright│
         │  Robot Control Core │           │    MCP     │
         │                     │           │            │
         │ ├─ ZMQ Pub/Sub      │           │ Manages    │
         │ ├─ HTTP API         │           │ Browser    │
         │ ├─ Skill Execution  │           │ Sessions   │
         │ └─ Joint Control    │           │            │
         └─────┬─────┬─────────┘           └────────────┘
               │     │
               │     └─────► Physical Robot Hardware
               │            (SO-101 Dual-Arm)
               │
         ┌─────▼──────────────┐
         │  Camera/Sensors    │
         │  (Vision Input)    │
         └────────────────────┘


External Storage & Services:
┌──────────────────────────────────────────────────────────┐
│  MinIO (S3-Compatible)  │  Hugging Face Hub (Datasets)  │
│  Port 9000 (API)        │  LeRobot v2 Demonstrations    │
│  Port 9001 (Console)    │  Calibration Data             │
└──────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Color Mixing Optimization Flow

```
┌─────────────────────┐
│  User Input:        │
│  - Target Color     │
│  - Constraints      │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  FRONTEND SERVICE (Port 3000)            │
│  ┌──────────────────────────────────┐   │
│  │ ML Optimization Engine           │   │
│  │                                  │   │
│  │ 1. Target Color Processing       │   │
│  │    - RGB to CIELAB conversion    │   │
│  │    - Hue angle calculation       │   │
│  │                                  │   │
│  │ 2. Bayesian Optimization         │   │
│  │    - Gaussian Process Regression │   │
│  │    - Expected Improvement metric │   │
│  │    - Adaptive phase scheduling   │   │
│  │                                  │   │
│  │ 3. Ground Truth Integration      │   │
│  │    - Load calibration matrix     │   │
│  │    - Constraint validation       │   │
│  │                                  │   │
│  │ 4. Volume Splitting Logic        │   │
│  │    - If volume > 4mL             │   │
│  │    - Split into ≤4mL segments    │   │
│  │                                  │   │
│  │ OUTPUT: Ratio recommendations    │   │
│  │         with confidence scores   │   │
│  └──────────────────────────────────┘   │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  ROBOT SERVICE (Port 8000)       │
│                                  │
│  1. Load Configuration           │
│  2. Execute Dispensing           │
│  3. Generate Squeeze Plan        │
│  4. Transmit to Phosphobot       │
│  5. Monitor Execution            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  PHOSPHOBOT SDK                  │
│  - Joint coordination            │
│  - Servo control                 │
│  - State publishing (ZMQ)        │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  ROBOT HARDWARE                  │
│  - SO-101 Dual Arm               │
│  - Servo Motors                  │
│  - Gripper Control               │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  CAMERA CAPTURE                  │
│  - Real-time video               │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  VISION BRIDGE (Port 5000)               │
│  ┌────────────────────────────────────┐ │
│  │ 1. Image Processing                │ │
│  │    - Resize & normalization        │ │
│  │                                    │ │
│  │ 2. SAM2 Segmentation (optional)    │ │
│  │    - Beaker region detection       │ │
│  │    - Mask generation               │ │
│  │                                    │ │
│  │ 3. Color Analysis                  │ │
│  │    - K-means clustering            │ │
│  │    - Dominant color extraction     │ │
│  │    - Center-weighted detection     │ │
│  │                                    │ │
│  │ 4. Metrics Calculation             │ │
│  │    - Delta-E (full color match)    │ │
│  │    - Angular distance (hue match)  │ │
│  │                                    │ │
│  │ OUTPUT: Color analysis results     │ │
│  └────────────────────────────────────┘ │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  FRONTEND UI                     │
│  - Display results               │
│  - Update visualization          │
│  - Next iteration recommendation │
└──────────────────────────────────┘
```

### 2. Dataset to Robot Pipeline

```
┌──────────────────────┐
│  LeRobot Dataset     │
│  (Hugging Face)      │
│  - Parquet files     │
│  - Joint positions   │
│  - Action/obs data   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  DEMO2RULES CONVERTER                │
│  (aloha-lite-demo2rule/demo2rules.py)│
│                                      │
│  1. Download dataset from HF         │
│  2. Parse LeRobot format             │
│  3. Extract joint trajectories       │
│  4. Generate executable rules        │
│                                      │
│  Output formats:                     │
│  - durable_rules Python script       │
│  - CSV for analysis                  │
│  - JSON configuration                │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  EXTRACT_AT_TIME                     │
│  (Time-based joint extractor)        │
│                                      │
│  Input: dataset, episode, timestamp  │
│  Output: precise joint values at t   │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  JSON CONFIGURATION                  │
│  (temp_rules/robot_configurations    │
│   .json)                             │
│                                      │
│  Stores:                             │
│  - Joint values (j1-j6)             │
│  - Source metadata                   │
│  - Arm type (dual/single)            │
│  - Timing information                │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  EXECUTE_RULES                       │
│  (Configuration execution)           │
│                                      │
│  1. Load configuration               │
│  2. Validate joint ranges            │
│  3. Plan trajectory (ModernRobotics) │
│  4. Execute via Phosphobot           │
│  5. Monitor completion               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  ROBOT EXECUTION                     │
│  - Arm movement                      │
│  - Task completion                   │
│  - Data collection (optional)        │
└──────────────────────────────────────┘
```

---

## Service Communication Patterns

### Request/Response Pattern (HTTP)

```
Frontend Client
    │
    ├─► GET /api/target-color
    │   └─ Returns: {rgb, hue_angle, success: true}
    │
    ├─► POST /api/recommend-ratios
    │   └─ Returns: {red: 1.2, yellow: 0.8, blue: 1.0, confidence: 0.95}
    │
    ├─► POST /robot/dispense
    │   Request: {
    │       color: "red" | "yellow" | "blue" | "mixed",
    │       duration: 2.0,
    │       color_ratios: {red: 1.2, yellow: 0.8, blue: 1.0}
    │   }
    │   Response: {
    │       cmd_id: "uuid",
    │       status: "accepted"
    │   }
    │
    ├─► GET /robot/{cmd_id}/status
    │   └─ Returns: {status: "running" | "complete" | "failed"}
    │
    └─► POST /vision/analyze-beaker
        Request: {image_data: "base64"}
        Response: {
            dominant_color: {r: 150, g: 100, b: 50},
            delta_e: 4.2,
            angular_distance: 8.5,
            confidence: 0.92
        }
```

### Real-time Updates (ZMQ Pub/Sub)

```
Phosphobot Service
    │
    ├─ Publishes robot state every 10ms
    │   {
    │       timestamp: 1234567890.123,
    │       joint_angles: [j1, j2, j3, j4, j5, j6],
    │       gripper_state: {open: 0-1},
    │       end_effector_pose: [x, y, z, rx, ry, rz]
    │   }
    │
    └─ Subscribers:
        - Robot Service (monitoring)
        - Frontend (real-time display)
        - Vision Bridge (synchronization)
```

---

## Data Models & Structures

### Robot Configuration JSON

```json
{
  "configurations": {
    "dispensing_water_to_beaker": {
      "name": "dispensing_water_to_beaker",
      "description": "Dual-arm water dispensing",
      "source": {
        "dataset": "Hafnium49/aloha_lite",
        "episode": 1,
        "timestamp": 4.2,
        "frame_index": 126,
        "extraction_method": "time_based"
      },
      "configuration": {
        "left_arm": {
          "joints": {
            "j1": 0.227, "j2": 0.746, "j3": 0.123,
            "j4": -1.234, "j5": 0.456, "j6": 2.789
          }
        },
        "right_arm": {
          "joints": {
            "j1": 0.219, "j2": 0.198, "j3": -0.456,
            "j4": 1.234, "j5": -0.789, "j6": 0.123
          }
        }
      },
      "usage": {
        "phosphobot_api": {
          "left_arm": "POST /joints/write with body: [0.227, ...]",
          "right_arm": "POST /joints/write with body: [0.219, ...]"
        }
      }
    },
    "ready_to_pick_beaker": {
      "name": "ready_to_pick_beaker",
      "description": "Left arm only (right arm stays steady)",
      "configuration": {
        "left_arm": {
          "joints": {"j1": 0.542, "j2": 0.921, ...}
        }
        // No right_arm section - arm doesn't move
      }
    }
  }
}
```

### Sequential Procedure JSON

```json
{
  "sequences": {
    "standoff_to_dispensing": {
      "steps": [
        {
          "config": "standoff_configuration_stage1",
          "pause_after": 1.0,
          "description": "Move to safe standoff position"
        },
        {
          "config": "dispensing_water_to_beaker",
          "pause_after": 2.0,
          "description": "Execute dispensing operation"
        }
      ],
      "total_duration_est": 3.0
    }
  }
}
```

### Optimization History

```json
{
  "optimization_history": [
    {
      "attempt": 1,
      "ratios": {"red": 1.0, "yellow": 1.0, "blue": 1.0},
      "measured_color": {"r": 255, "g": 128, "b": 0},
      "target_color": {"r": 220, "g": 120, "b": 20},
      "delta_e": 15.3,
      "angular_distance": 3.2,
      "confidence": 0.5,
      "timestamp": "2025-10-20T14:30:45Z"
    },
    {
      "attempt": 2,
      "ratios": {"red": 0.95, "yellow": 1.1, "blue": 0.85},
      "measured_color": {"r": 230, "g": 130, "b": 15},
      "target_color": {"r": 220, "g": 120, "b": 20},
      "delta_e": 8.5,
      "angular_distance": 1.8,
      "confidence": 0.85,
      "timestamp": "2025-10-20T14:31:15Z"
    }
  ]
}
```

---

## ML Optimization System Details

### Bayesian Optimization Process

```
Step 1: Initialization
├─ Load ground truth calibration matrix (4×3: RGBA channels)
├─ Set prior bounds (red: 0-2.5, yellow: 0-2.5, blue: 0-2.5)
└─ Convert target RGB to CIELAB color space

Step 2: First Observation
├─ Make initial dispense with moderate ratios (1.0, 1.0, 1.0)
├─ Capture and analyze color
├─ Calculate Delta-E (full color match) or angular distance (hue match)
└─ Record observation point

Step 3: Fit Gaussian Process
├─ Fit GPR model to observed (ratio → color error) mapping
├─ Learn correlations between ratio parameters
└─ Estimate uncertainty at unexplored regions

Step 4: Expected Improvement
├─ Calculate EI metric across entire parameter space
├─ Balance exploration (high uncertainty) vs exploitation (low error)
├─ Select next candidate ratios with highest EI

Step 5: Repeat
├─ Dispense with new ratios
├─ Measure color
├─ Update GPR model
└─ Continue until error < threshold or max iterations

Adaptive Phase Strategy:
- Phase 1 (iter 1-3): Exploration - sample diverse regions
- Phase 2 (iter 4-6): Refinement - narrow search space
- Phase 3 (iter 7-10): Exploitation - converge on optimum
- Phase 4 (iter 11+): Final polish - sub-degree accuracy
```

### Hue-Only Optimization

```
Standard RGB Optimization:
- Minimizes: sqrt((R_meas - R_target)² + (G_meas - G_target)² + (B_meas - B_target)²)
- Problem: Weight to wrong dimensions, perceptually inaccurate

CIELAB Color Space Optimization:
- Convert RGB → CIELAB (L*, a*, b*)
- Calculate hue angle: h = atan2(b*, a*) → range [0, 360°)
- Angular distance: min(|h_meas - h_target|, 360 - |h_meas - h_target|)
- Optimization cost: angular_distance (in degrees)

Advantages:
✓ Perceptually uniform color space
✓ Angular wraparound handling (red at 0° = red at 360°)
✓ Hue-only accuracy < 10° achievable in 5-8 iterations
✓ Matches human color perception better than RGB distance
```

---

## Vision Processing Pipeline

### SAM2 Integration Flow

```
Input Image
    │
    ▼
┌─────────────────────────────────────┐
│  Preprocessing                      │
├─ Resize to 1024×1024 (if needed)   │
├─ Normalize pixel values [0, 1]     │
└─ Convert to torch tensor            │
    │
    ▼
┌─────────────────────────────────────┐
│  SAM2 Prompt Generation             │
├─ Center point: (image.width/2,     │
│                image.height/2)     │
├─ Box bounds: (margin 20%)          │
└─ Create prompt with both            │
    │
    ▼
┌─────────────────────────────────────┐
│  SAM2 Inference                     │
├─ Generate masks for center region   │
├─ Confidence score for each mask     │
└─ Filter masks by confidence > 0.8   │
    │
    ▼
┌─────────────────────────────────────┐
│  Mask Selection                     │
├─ Pick largest mask (beaker bottom)  │
├─ Apply morphological operations     │
└─ Fill small holes                   │
    │
    ▼
┌─────────────────────────────────────┐
│  Color Extraction                   │
├─ Extract masked region pixels       │
├─ K-means clustering (k=5 colors)    │
├─ Get cluster centroids in RGB       │
└─ Identify dominant color            │
    │
    ▼
Output:
├─ Mask image (binary)
├─ Dominant RGB color
├─ Color distribution (5 clusters)
└─ Confidence score
```

### Fallback Chain (When SAM2 Unavailable)

```
SAM2 Available?
    │
    ├─ YES: Use SAM2 segmentation
    │       └─ High accuracy, slow (200-500ms)
    │
    └─ NO: Fall back to circle detection
            │
            ├─ Hough circle detection
            ├─ Find concentric circles
            ├─ Extract beaker region
            │
            ├─ K-means clustering in region
            ├─ Extract dominant colors
            │
            └─ Return results
                 (Lower accuracy, fast - 50-100ms)
```

---

## Performance Characteristics

### Latency Breakdown (Typical Request)

```
Client Request → Frontend
├─ HTTP routing: 1ms
├─ Auth/validation: 2ms
└─ Cache lookup: 1ms

ML Optimization
├─ Target color generation: 5ms
├─ Bayesian GPR fit: 50ms (first iteration)
├─ EI calculation: 20ms
├─ Ratio recommendation: 2ms
└─ Subtotal: ~80ms (first) or ~40ms (subsequent)

Proxy to Robot Service
├─ HTTP serialization: 2ms
├─ Network transfer: 5ms
├─ Robot processing: 50ms
└─ Subtotal: ~60ms

Robot Execution
├─ Phosphobot SDK: 10ms
├─ Hardware command: 20ms
└─ Subtotal: ~30ms

Vision Analysis (Async)
├─ Image capture: 30ms
├─ Preprocessing: 20ms
├─ SAM2 inference: 300ms (GPU) or fallback 50ms
├─ Color analysis: 20ms
└─ Subtotal: ~370ms (SAM2) or ~70ms (fallback)

Total User-Perceived Latency: ~80-100ms
Background Vision: 300-400ms (SAM2) or 70ms (fallback)
```

### Throughput

```
Dispense Operations: 10-20 per minute (depends on duration)
Color Recommendations: 100-200 per second (no robot)
Vision Analysis: 2-3 per second (with SAM2), 10+ (fallback)
Concurrent Operations: Limited by robot hardware (sequential by default)
```

---

## Error Handling & Safety

### Error Cascade Prevention

```
Frontend ML Error
    ├─ Invalid input RGB?
    │  └─ Return error response
    ├─ ML inference fails?
    │  └─ Return last known good result
    └─ Recommendation out of bounds?
       └─ Clip to valid range

Robot Service Error
    ├─ Configuration not found?
    │  └─ List available configs
    ├─ Joint limits exceeded?
    │  └─ Reject & suggest alternatives
    ├─ Trajectory planning fails?
    │  └─ Revert to direct joint control
    └─ Phosphobot unreachable?
       └─ Return error, suggest reboot

Vision Service Error
    ├─ Camera unavailable?
    │  └─ Return placeholder results
    ├─ SAM2 model fails?
    │  └─ Fallback to circle detection
    └─ S3 upload fails?
       └─ Keep in memory, retry later

MCP Server Error
    ├─ Playwright MCP down?
    │  └─ Attempt restart (max 3×)
    ├─ WebSocket connection lost?
    │  └─ Reconnect with exponential backoff
    └─ Command timeout?
       └─ Abort, report to Claude

All Errors
├─ Log with full context
├─ Return JSON response with error_code
├─ Never expose internal paths/credentials
└─ Graceful degradation where possible
```

### Safety Interlocks

```
Before Robot Movement:
✓ Configuration validation (joint ranges OK?)
✓ Collision checking (if available)
✓ Speed limits enforced (velocity <= max)
✓ Timeout protection (each move has max duration)
✓ E-stop ready (manual override always possible)

During Robot Movement:
✓ Real-time state monitoring (ZMQ updates)
✓ Watchdog timer (fail-safe if no update >100ms)
✓ Current limiting (servo protection)
✓ Temperature monitoring (if available)

Safety Defaults:
✓ No initialization by default (prevents collision)
✓ Safe home position after errors
✓ Single-arm safety (other arm stays steady)
✓ Volume limits (max 4mL per squeeze by default)
```

---

## Development Considerations

### Local Development Setup

```bash
# Development mode (no external dependencies)
export REQUIRE_MODEL=false
export REQUIRE_ROBOT=false
export REQUIRE_S3=false
export ROBOT_TYPE=simulator

# Start services
cd robot_service && \
  REQUIRE_MODEL=false REQUIRE_ROBOT=false \
  uvicorn main:app --reload --port 8000

cd frontend && \
  REQUIRE_MODEL=false \
  uvicorn main:app --reload --port 3000

cd vision_bridge && \
  REQUIRE_S3=false \
  uvicorn main:app --reload --port 5000

# All services now available:
# Frontend: http://localhost:3000
# Robot API: http://localhost:8000/docs
# Vision API: http://localhost:5000/docs
```

### Testing Strategy

```
Unit Tests:
├─ ML algorithms (Bayesian GPR, hue calculation)
├─ Color space conversions (RGB ↔ CIELAB)
├─ Trajectory planning (ModernRobotics)
└─ Configuration validation

Integration Tests:
├─ Service-to-service communication
├─ End-to-end color mixing workflow
├─ Dataset to robot pipeline
└─ Vision analysis with mock images

End-to-End Tests:
├─ Full workflow with robot simulator
├─ Error recovery paths
├─ Concurrent operation safety
└─ Performance benchmarks

Coverage Goal: >80% for services, >90% for ML components
```

---

## Monitoring & Observability

### Prometheus Metrics

```
Robot Service (9001):
├─ robot_requests_total (Counter)
├─ robot_request_latency_seconds (Histogram)
├─ robot_errors_total (Counter)
├─ robot_config_load_failures (Counter)
└─ robot_trajectory_planning_time_seconds (Histogram)

Vision Service (9003):
├─ vision_analysis_latency_seconds (Histogram)
├─ vision_sam2_available (Gauge)
├─ vision_fallback_used_total (Counter)
└─ vision_s3_errors_total (Counter)

ML Optimization:
├─ optimization_iterations (Counter)
├─ optimization_convergence_time (Histogram)
├─ ml_model_inference_time (Histogram)
└─ ml_confidence_scores (Histogram)
```

### Logging Strategy

```
Log Levels:
DEBUG   - Parameter values, intermediate calculations
INFO    - Operation start/completion, state changes
WARNING - Recoverable errors, fallbacks used
ERROR   - Non-recoverable errors, retries exhausted
CRITICAL- System failure, immediate action required

Log Format:
[timestamp] [service:component] [level] message
2025-10-20 14:30:45.123 [robot_service:main] INFO Starting dispense operation: cmd_id=abc123
2025-10-20 14:30:46.450 [vision_bridge:beaker] ERROR SAM2 inference failed, falling back to circle detection
```

---

## Deployment Checklist

Before production deployment:

- [ ] Environment variables properly set (secrets in .env)
- [ ] SSL/TLS configured on Traefik gateway
- [ ] S3 (MinIO) storage verified and tested
- [ ] Robot hardware calibration current
- [ ] SAM2 models downloaded and verified
- [ ] Ground truth calibration matrices loaded
- [ ] Database backups configured
- [ ] Monitoring and alerting enabled
- [ ] Log aggregation configured
- [ ] CORS settings verified and restricted
- [ ] Rate limiting configured (if needed)
- [ ] Circuit breakers tested
- [ ] Failover tested (robot, vision, S3)
- [ ] Documentation updated for ops team
- [ ] Performance baseline established

