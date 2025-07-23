import os, json, asyncio, uuid, time, logging, subprocess, sys
from typing import List, Dict, Optional
from pathlib import Path

import httpx, zmq, zmq.asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PHOS_URL   = os.getenv("PHOS_URL", "http://phosphobot")
MODEL_ID   = os.getenv("MODEL_ID")
TARGET_POSE = json.loads(os.getenv("TARGET_POSE", "[0,0,0,0,0,0]"))
TOL        = float(os.getenv("TOL", "0.03"))
REQUIRE_MODEL = os.getenv("REQUIRE_MODEL", "true").lower() == "true"

# Validate required environment variables (only if REQUIRE_MODEL is true)
if REQUIRE_MODEL and not MODEL_ID:
    logger.error("MODEL_ID environment variable is required")
    raise ValueError("MODEL_ID environment variable is required")

REQS_TOTAL = Counter("robot_requests_total", "Robot dispense requests")
REQ_LAT    = Histogram("robot_request_latency_seconds", "Robot latency")

# --- FastAPI -----------------------------------------------------------------
app = FastAPI(title="Robot Service", version="0.1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DispenseRequest(BaseModel):
    mix_id: int
    run_id: int
    colour: str = Field(pattern="^(red|yellow|blue)$")  # Updated to support yellow instead of green
    volume_ml: float = Field(default=None, gt=0.0, le=150.0)  # Made optional and increased max
    # New fields for multi-color support
    color_ratios: dict = Field(default=None, description="Color ratios for red, yellow, blue")
    normalized_percentages: dict = Field(default=None, description="Normalized percentages")

class ErrorResponse(BaseModel):
    error: str
    detail: str
    cmd_id: str | None = None

class DispenseStatus(BaseModel):
    status: str
    predicted_squeeze_sec: float | None = None
    created_at: float = Field(default_factory=time.time)
    # Extended fields for multi-color support
    request_id: Optional[str] = None
    current_operation: Optional[object] = None  # Will be ColorOperation
    operations: List[object] = []  # Will be List[ColorOperation]
    completed_operations: List[object] = []  # Will be List[ColorOperation]
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    # Beaker analysis results
    beaker_analysis_results: Optional[Dict] = None

class ColorRatios(BaseModel):
    red: float = Field(ge=0.0, le=100.0)
    yellow: float = Field(ge=0.0, le=100.0) 
    blue: float = Field(ge=0.0, le=100.0)

class NormalizedPercentages(BaseModel):
    red: float = Field(ge=0.0, le=100.0)
    yellow: float = Field(ge=0.0, le=100.0)
    blue: float = Field(ge=0.0, le=100.0)

class MultiColorDispenseRequest(BaseModel):
    mix_id: int
    run_id: int
    colour: str = Field(pattern="^(red|yellow|blue)$")  # dominant color for compatibility
    color_ratios: ColorRatios
    normalized_percentages: NormalizedPercentages
    base_duration: float = Field(default=3.0, gt=0.0, le=10.0, description="Base duration in seconds")

class ColorOperation(BaseModel):
    color: str
    ratio: float
    duration: float
    config: str
    status: str = "pending"

# in-memory store; replace w/ DB table in prod
TASKS: dict[str, DispenseStatus] = {}
TASK_CLEANUP_INTERVAL = 300  # 5 minutes
MAX_TASK_AGE = 3600  # 1 hour

# Multi-color dispensing state
CURRENT_DISPENSE_STATUS = DispenseStatus(status="idle")
# Global squeeze duration adjustments (normalized to 10 seconds total)
SQUEEZE_ADJUSTMENTS: dict[str, float] = {}
# Track current sequence step for color detection
CURRENT_SEQUENCE_STEP: int = 0
CONFIG_MAP = {
    "red": "dispensing_red_to_beaker.json",
    "yellow": "dispensing_yellow_to_beaker.json", 
    "blue": "dispensing_blue_to_beaker.json"
}


def pose_close(q: List[float]) -> bool:
    return all(abs(a-b) < TOL for a, b in zip(q, TARGET_POSE))


async def zmq_state_listener():
    ctx = zmq.asyncio.Context.instance()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://phosphobot:5555")   # state topic
    sub.setsockopt_string(zmq.SUBSCRIBE, "state")
    while True:
        try:
            _topic, raw = await sub.recv_multipart()
            msg = json.loads(raw)
            
            # Validate message structure
            if "joints" not in msg:
                logger.warning("Received message without 'joints' field")
                continue
                
            if pose_close(msg["joints"]):
                # broadcast event to any waiting CSR tasks
                async with POSE_WAITERS_LOCK:
                    completed_waiters = []
                    for fut in list(POSE_WAITERS):
                        if not fut.done():
                            fut.set_result(msg)
                            completed_waiters.append(fut)
                    # Clean up completed waiters
                    for fut in completed_waiters:
                        POSE_WAITERS.discard(fut)
            
            async with TASKS_LOCK:
                for tid, st in TASKS.items():
                    if st.status == "running" and msg.get("status") == "success":
                        st.status = "success"
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode ZMQ message: {e}")
        except Exception as e:
            logger.error(f"Error in ZMQ listener: {e}")
        await asyncio.sleep(0.0)

async def cleanup_old_tasks():
    """Periodically clean up old completed tasks"""
    while True:
        await asyncio.sleep(TASK_CLEANUP_INTERVAL)
        current_time = time.time()
        
        async with TASKS_LOCK:
            expired_tasks = [
                tid for tid, task in TASKS.items()
                if current_time - task.created_at > MAX_TASK_AGE
            ]
            for tid in expired_tasks:
                del TASKS[tid]
        
        # Also clean up any done futures in POSE_WAITERS
        async with POSE_WAITERS_LOCK:
            done_waiters = [fut for fut in POSE_WAITERS if fut.done()]
            for fut in done_waiters:
                POSE_WAITERS.discard(fut)

POSE_WAITERS: set[asyncio.Future] = set()
POSE_WAITERS_LOCK = asyncio.Lock()
TASKS_LOCK = asyncio.Lock()
asyncio.create_task(zmq_state_listener())
asyncio.create_task(cleanup_old_tasks())
start_http_server(9001)     # Prometheus

# --------------------------------------------------------------------------- #
# Multi-color dispensing functions

async def execute_squeeze_operation(color: str, duration: float, config: str) -> bool:
    """Execute a single squeeze operation for a specific color."""
    try:
        logger.info(f"Starting squeeze operation: {color} for {duration:.2f}s with config {config}")
        
        # Path to squeeze_bottle.py script
        squeeze_bottle_path = os.path.join(os.path.dirname(__file__), "squeeze_bottle.py")
        
        # Command to run squeeze operation
        cmd = [
            sys.executable,
            squeeze_bottle_path,
            "--duration", str(duration),
            "--base-config", config
        ]
        
        # Execute the squeeze operation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duration + 10,  # Add buffer time
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode != 0:
            logger.error(f"Squeeze operation failed for {color}: {result.stderr}")
            return False
        
        logger.info(f"Successfully completed squeeze operation for {color}")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Squeeze operation timed out for {color}")
        return False
    except Exception as e:
        logger.error(f"Error during {color} squeeze operation: {e}")
        return False

async def execute_sequential_configuration(config_name: str) -> bool:
    """Execute a single configuration using sequential_execute.py."""
    try:
        logger.info(f"Executing configuration: {config_name}")
        
        # Path to sequential_execute.py script
        sequential_execute_path = os.path.join(os.path.dirname(__file__), "sequential_execute.py")
        
        # Command to run configuration with fast timing
        cmd = [
            sys.executable,
            sequential_execute_path,
            config_name,
            "--smooth",
            "--pause-between", "0.1",
            "--pause-after", "0.1"
        ]
        
        # Execute the configuration
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode != 0:
            logger.error(f"Configuration failed for {config_name}: {result.stderr}")
            return False
        
        logger.info(f"Successfully completed configuration: {config_name}")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Configuration timed out for {config_name}")
        return False
    except Exception as e:
        logger.error(f"Error during configuration {config_name}: {e}")
        return False

async def parse_beaker_analysis_results() -> Optional[Dict]:
    """Parse the most recent beaker analysis results from temporary images directory."""
    try:
        # Look for the most recent beaker analysis results in temporary_images directory
        temp_images_dir = Path(os.path.dirname(__file__)) / "../temporary_images"
        if not temp_images_dir.exists():
            logger.warning("Temporary images directory not found")
            return None
        
        # Find the most recent beaker analysis JSON file
        analysis_files = list(temp_images_dir.glob("beaker_analysis_*.json"))
        if not analysis_files:
            logger.warning("No beaker analysis results found")
            return None
        
        # Get the most recent analysis file
        latest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Reading beaker analysis results from: {latest_analysis.name}")
        
        # Load and return the analysis results
        with open(latest_analysis, 'r') as f:
            analysis_data = json.load(f)
        
        # Add metadata about the analysis
        analysis_data['_metadata'] = {
            'filename': latest_analysis.name,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(latest_analysis.stat().st_mtime)),
            'file_size': latest_analysis.stat().st_size
        }
        
        logger.info(f"Successfully loaded beaker analysis results: {analysis_data.get('dominant_color', {}).get('hex', 'unknown color')}")
        return analysis_data
        
    except Exception as e:
        logger.error(f"Error parsing beaker analysis results: {e}")
        return None

async def execute_special_function(function_description: str, cmd_id: str = None) -> bool:
    """Execute special functions like squeeze, await, or analyze beaker."""
    try:
        logger.info(f"Executing special function: {function_description}")
        
        # Parse different types of special functions
        if "squeeze washing bottle" in function_description.lower():
            # Determine the current color being dispensed based on sequence position
            global SQUEEZE_ADJUSTMENTS, CURRENT_SEQUENCE_STEP
            
            # Extract the default duration first
            import re
            match = re.search(r"(\d+\.?\d*)\s*seconds?", function_description)
            default_duration = float(match.group(1)) if match else 1.5
            
            # Map squeeze operations to colors based on timed_laboratory_procedure sequence
            # Red squeeze: step 4 (after dispensing_red_to_beaker at step 3)
            # Yellow squeeze: step 10 (after dispensing_yellow_to_beaker at step 9) 
            # Blue squeeze: step 16 (after dispensing_blue_to_beaker at step 15)
            current_color = None
            if CURRENT_SEQUENCE_STEP == 4:  # After red dispensing
                current_color = 'red'
            elif CURRENT_SEQUENCE_STEP == 10:  # After yellow dispensing
                current_color = 'yellow'
            elif CURRENT_SEQUENCE_STEP == 16:  # After blue dispensing
                current_color = 'blue'
            
            # Use adjusted duration if available, otherwise use default
            if current_color and current_color in SQUEEZE_ADJUSTMENTS:
                duration = SQUEEZE_ADJUSTMENTS[current_color]
                logger.info(f"Using adjusted squeeze duration for {current_color}: {duration:.2f}s (normalized from 10s total)")
            else:
                duration = default_duration
                logger.info(f"Using default squeeze duration: {duration:.2f}s (step {CURRENT_SEQUENCE_STEP})")
            
            # Use squeeze_bottle.py directly for washing bottle
            squeeze_bottle_path = os.path.join(os.path.dirname(__file__), "squeeze_bottle.py")
            cmd = [
                sys.executable,
                squeeze_bottle_path,
                "--duration", str(duration)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10, cwd=os.path.dirname(__file__))
            if result.returncode != 0:
                logger.error(f"Squeeze operation failed: {result.stderr}")
                return False
            return True
            
        elif "await" in function_description.lower() or "wait" in function_description.lower():
            # Extract duration from description like "await 10 seconds"
            import re
            match = re.search(r"(\d+\.?\d*)\s*seconds?", function_description)
            if match:
                duration = float(match.group(1))
                logger.info(f"Waiting for {duration} seconds...")
                await asyncio.sleep(duration)
                return True
                
        elif "analyze beaker" in function_description.lower():
            # Use sequential_execute.py to run beaker analysis
            sequential_execute_path = os.path.join(os.path.dirname(__file__), "sequential_execute.py")
            cmd = [
                sys.executable,
                sequential_execute_path,
                "analyze beaker color",
                "--smooth",
                "--pause-between", "0.1",
                "--pause-after", "0.1"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=os.path.dirname(__file__))
            if result.returncode != 0:
                logger.error(f"Beaker analysis failed: {result.stderr}")
                return False
            
            # Parse beaker analysis results from sequential_execute.py output
            analysis_results = await parse_beaker_analysis_results()
            if analysis_results and cmd_id:
                # Store analysis results in task status
                async with TASKS_LOCK:
                    if cmd_id in TASKS:
                        TASKS[cmd_id].beaker_analysis_results = analysis_results
                        logger.info(f"Stored beaker analysis results for cmd_id={cmd_id}")
            
            return True
        
        logger.warning(f"Unknown special function: {function_description}")
        return False
        
    except Exception as e:
        logger.error(f"Error executing special function {function_description}: {e}")
        return False

async def execute_multi_color_dispensing_task(cmd_id: str, color_ratios: ColorRatios, base_duration: float):
    """
    Background task to execute the complete timed laboratory procedure with multi-color dispensing.
    This implements the full timed_laboratory_procedure sequence from sequential_sequences.json.
    
    Args:
        cmd_id: Unique command identifier
        color_ratios: Color ratios from frontend (used to customize squeeze durations)
        base_duration: Base duration for scaling (affects squeeze timing)
    """
    try:
        async with TASKS_LOCK:
            if cmd_id not in TASKS:
                logger.error(f"Command ID {cmd_id} not found in TASKS")
                return
            TASKS[cmd_id].status = "running"
        
        # Define the complete timed laboratory procedure sequence
        laboratory_sequence = [
            "left_arm_serving_standoff",
            "left_arm_standoff_with_beaker",
            "dispensing_red_to_beaker",
            "squeeze washing bottle for 1.5 seconds",
            "right_arm_standoff",
            "left_arm_standoff_with_beaker",
            "left_arm_standoff_yellow", 
            "right_arm_standoff_yellow",
            "dispensing_yellow_to_beaker",
            "squeeze washing bottle for 2.5 seconds",
            "right_arm_standoff_yellow",
            "right_arm_standoff",
            "left_arm_standoff_yellow",
            "left_arm_standoff_blue",
            "dispensing_blue_to_beaker",
            "squeeze washing bottle for 1 seconds",
            "right_arm_standoff",
            "left_arm_standoff_blue",
            "left_arm_standoff_yellow",
            "left_arm_stirer_standoff",
            "left_arm_stirring",
            "await 10 seconds",
            "analyze beaker color",
            "await 3 seconds",
            "left_arm_stirer_standoff",
            "left_arm_standoff_yellow",
            "left_arm_standoff_with_beaker",
            "left_arm_serving_standoff",
            "left_arm_serving_beaker"
        ]
        
        # Calculate adjusted squeeze durations based on color ratios if provided
        # Normalize total duration to 10 seconds and apply proportionally
        global SQUEEZE_ADJUSTMENTS
        SQUEEZE_ADJUSTMENTS = {}
        
        if color_ratios:
            total_ratio = color_ratios.red + color_ratios.yellow + color_ratios.blue
            if total_ratio > 0:
                # Normalize to 10 seconds total duration
                total_duration = 10.0
                # Adjust squeeze durations proportionally with minimum 0.5 seconds
                SQUEEZE_ADJUSTMENTS = {
                    "red": max(0.5, (color_ratios.red / total_ratio) * total_duration),
                    "yellow": max(0.5, (color_ratios.yellow / total_ratio) * total_duration), 
                    "blue": max(0.5, (color_ratios.blue / total_ratio) * total_duration)
                }
                logger.info(f"Normalized squeeze durations (10s total): {SQUEEZE_ADJUSTMENTS}")
            else:
                # Use default durations if no valid ratios
                SQUEEZE_ADJUSTMENTS = {"red": 1.5, "yellow": 2.5, "blue": 1.0}
        else:
            # Use default durations from sequential_sequences.json
            SQUEEZE_ADJUSTMENTS = {"red": 1.5, "yellow": 2.5, "blue": 1.0}
        
        logger.info(f"Starting timed laboratory procedure for cmd_id={cmd_id}")
        logger.info(f"Total sequence steps: {len(laboratory_sequence)}")
        
        # Initialize sequence step tracking
        global CURRENT_SEQUENCE_STEP
        CURRENT_SEQUENCE_STEP = 0
        
        # Execute each step in the laboratory sequence
        for i, step in enumerate(laboratory_sequence, 1):
            # Update current sequence step for color detection
            CURRENT_SEQUENCE_STEP = i
            
            # Update current operation status
            async with TASKS_LOCK:
                if hasattr(TASKS[cmd_id], 'current_operation'):
                    TASKS[cmd_id].current_operation = {
                        "step": i,
                        "total_steps": len(laboratory_sequence),
                        "description": step,
                        "status": "running"
                    }
            
            logger.info(f"Step {i}/{len(laboratory_sequence)}: {step}")
            
            # Determine if this is a configuration or special function
            if any(keyword in step.lower() for keyword in ["squeeze", "await", "wait", "analyze"]):
                # Special function
                success = await execute_special_function(step, cmd_id)
            else:
                # Regular configuration
                success = await execute_sequential_configuration(step)
            
            if not success:
                async with TASKS_LOCK:
                    TASKS[cmd_id].status = "failed"
                    TASKS[cmd_id].error_message = f"Failed at step {i}: {step}"
                raise RuntimeError(f"Failed at step {i}: {step}")
            
            # Mark step as completed
            logger.info(f"✅ Completed step {i}/{len(laboratory_sequence)}: {step}")
            
            # Small delay between steps for system stability
            await asyncio.sleep(0.1)
        
        # Mark entire task as completed
        async with TASKS_LOCK:
            TASKS[cmd_id].status = "completed"
            TASKS[cmd_id].current_operation = None
            TASKS[cmd_id].completed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"🎉 Timed laboratory procedure completed successfully for cmd_id={cmd_id}")
        
    except Exception as e:
        logger.error(f"Timed laboratory procedure failed for cmd_id={cmd_id}: {e}")
        async with TASKS_LOCK:
            if cmd_id in TASKS:
                TASKS[cmd_id].status = "failed"
                TASKS[cmd_id].error_message = str(e)
                TASKS[cmd_id].current_operation = None

# --------------------------------------------------------------------------- #
@app.post("/robot/dispense")
@REQ_LAT.time()
async def dispense(req: DispenseRequest, background_tasks: BackgroundTasks):
    REQS_TOTAL.inc()
    logger.info(f"Received dispense request: {req}")
    
    # Check if this is a multi-color request (now executes full laboratory procedure)
    if req.color_ratios is not None and req.normalized_percentages is not None:
        logger.info("Processing timed laboratory procedure request with multi-color ratios")
        
        try:
            # Generate unique command ID
            cmd_id = str(uuid.uuid4())
            
            # Validate that at least one color has a non-zero ratio
            total_ratio = sum(req.color_ratios.values())
            if total_ratio <= 0:
                raise HTTPException(400, "At least one color ratio must be greater than 0")
            
            # Convert dict to ColorRatios model
            color_ratios = ColorRatios(
                red=req.color_ratios.get("red", 0),
                yellow=req.color_ratios.get("yellow", 0),
                blue=req.color_ratios.get("blue", 0)
            )
            
            # Create task entry with extended fields for timed laboratory procedure
            task_status = DispenseStatus(
                status="pending",
                request_id=cmd_id,
                operations=[],
                completed_operations=[],
                started_at=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            async with TASKS_LOCK:
                TASKS[cmd_id] = task_status
            
            # Start background task with base_duration from request or default
            base_duration = getattr(req, 'base_duration', 3.0)
            background_tasks.add_task(
                execute_multi_color_dispensing_task,  # Now executes full laboratory procedure
                cmd_id,
                color_ratios,
                base_duration
            )
            
            logger.info(f"Timed laboratory procedure started with cmd_id={cmd_id}")
            response_data = {
                "cmd_id": cmd_id, 
                "status": "pending",
                "procedure": "timed_laboratory_procedure",
                "description": "Complete laboratory workflow with positioning, dispensing, squeezing, stirring, waiting, and beaker analysis"
            }
            logger.info(f"Returning response: {response_data}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error starting timed laboratory procedure: {e}")
            raise HTTPException(500, f"Laboratory procedure error: {str(e)}")
    
    # Handle traditional single-color requests (legacy support)
    tid = str(uuid.uuid4())
    volume = req.volume_ml if req.volume_ml is not None else 25.0  # Default volume
    prompt = f"Dispense {volume} ml from the {req.colour} bottle"
    
    try:
        async with TASKS_LOCK:
            TASKS[tid] = DispenseStatus(status="running")

        # Check if ML inference is available
        if MODEL_ID and REQUIRE_MODEL:
            # Use ML inference to predict squeeze duration
            async with httpx.AsyncClient(timeout=60.0) as client:
                phos_resp = await client.post(f"{PHOS_URL}/inference",
                                              json={"model": MODEL_ID, "prompt": prompt})
                if phos_resp.status_code != 200:
                    async with TASKS_LOCK:
                        TASKS[tid].status = "failed"
                    logger.error(f"Phosphobot error: {phos_resp.status_code}")
                    raise HTTPException(502, f"Phosphobot error: {phos_resp.status_code}")

                squeeze = phos_resp.json().get("predicted_squeeze_sec")
                async with TASKS_LOCK:
                    TASKS[tid].predicted_squeeze_sec = squeeze
        else:
            # Fallback: use default squeeze duration based on volume
            default_squeeze = max(2.0, volume / 10.0)  # 2 seconds minimum, or volume/10
            logger.info(f"Using default squeeze duration: {default_squeeze}s (MODEL_ID not configured)")
            async with TASKS_LOCK:
                TASKS[tid].predicted_squeeze_sec = default_squeeze

        async with TASKS_LOCK:
            return {"cmd_id": tid, **TASKS[tid].model_dump()}
    except httpx.TimeoutException:
        async with TASKS_LOCK:
            TASKS[tid].status = "failed"
        logger.error(f"Timeout calling Phosphobot for task {tid}")
        raise HTTPException(504, "Timeout calling Phosphobot")
    except Exception as e:
        async with TASKS_LOCK:
            TASKS[tid].status = "failed"
        logger.error(f"Unexpected error in dispense {tid}: {e}")
        raise HTTPException(500, f"Internal error: {str(e)}")


@app.get("/robot/{cmd_id}/status")
async def status(cmd_id: str):
    async with TASKS_LOCK:
        st = TASKS.get(cmd_id)
        
        if not st:
            raise HTTPException(404, f"Task {cmd_id} not found")
        
        return st.model_dump()


@app.get("/robot/{cmd_id}/beaker-analysis")
async def get_beaker_analysis(cmd_id: str):
    """Get beaker analysis results for a specific command."""
    async with TASKS_LOCK:
        st = TASKS.get(cmd_id)
        
        if not st:
            raise HTTPException(404, f"Task {cmd_id} not found")
        
        if st.beaker_analysis_results is None:
            raise HTTPException(404, f"No beaker analysis results found for task {cmd_id}")
        
        return {
            "cmd_id": cmd_id,
            "task_status": st.status,
            "analysis_results": st.beaker_analysis_results
        }


@app.get("/robot/procedure/info")
async def get_procedure_info():
    """Get information about the timed laboratory procedure."""
    return {
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


@app.get("/robot/{cmd_id}/pose-snapshot")
async def pose_snapshot(cmd_id: str, cam: str = "top_cam"):
    """
    Blocks until pose reached, then returns a presigned S3 URL provided
    by Vision-Bridge (polls kv-store every 100 ms).
    """
    fut = asyncio.get_event_loop().create_future()
    async with POSE_WAITERS_LOCK:
        POSE_WAITERS.add(fut)
    
    try:
        await asyncio.wait_for(fut, timeout=30.0)  # 30 second timeout
    except asyncio.TimeoutError:
        async with POSE_WAITERS_LOCK:
            POSE_WAITERS.discard(fut)
        raise HTTPException(408, "Timeout waiting for target pose")
    finally:
        async with POSE_WAITERS_LOCK:
            POSE_WAITERS.discard(fut)

    # ask Vision-Bridge to capture
    try:
        async with httpx.AsyncClient(timeout=30.0) as cl:
            vb = await cl.post("http://vision-bridge:8000/snapshot",
                               json={"cmd_id": cmd_id, "cam_id": cam})
            if vb.status_code != 200:
                logger.error(f"Vision bridge error: {vb.status_code}")
                raise HTTPException(502, f"Vision bridge error: {vb.status_code}")
            return vb.json()
    except httpx.TimeoutException:
        logger.error("Timeout calling vision bridge")
        raise HTTPException(504, "Timeout calling vision bridge")
    except Exception as e:
        logger.error(f"Error calling vision bridge: {e}")
        raise HTTPException(500, f"Vision bridge error: {str(e)}")
