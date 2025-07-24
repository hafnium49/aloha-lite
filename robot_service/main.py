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
REQUIRE_ROBOT = os.getenv("REQUIRE_ROBOT", "true").lower() == "true"

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
    current_operation: Optional[Dict] = None  # Changed from object to Dict
    operations: List[Dict] = []  # Changed from List[object] to List[Dict]
    completed_operations: List[Dict] = []  # Changed from List[object] to List[Dict]
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
    mix_id: int = Field(default=1, description="Mix ID for tracking")
    run_id: int = Field(default=1, description="Run ID for tracking")
    colour: str = Field(default="red", pattern="^(red|yellow|blue)$", description="Dominant color for compatibility")
    color_ratios: ColorRatios
    normalized_percentages: Optional[NormalizedPercentages] = None
    base_duration: float = Field(default=3.0, gt=0.0, le=10.0, description="Base duration in seconds")

class SimpleMultiColorRequest(BaseModel):
    """Simplified request model for direct multi-color dispensing endpoint."""
    color_ratios: Dict[str, float] = Field(description="Color ratios as dict (red, yellow, blue)")
    base_duration: float = Field(default=1.0, gt=0.0, le=10.0, description="Base duration in seconds")

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
        
        # If robot hardware is not required, simulate successful execution
        if not REQUIRE_ROBOT:
            logger.info(f"REQUIRE_ROBOT=false: Simulating squeeze operation for {color} ({duration:.2f}s)")
            await asyncio.sleep(min(duration, 2.0))  # Simulate squeeze time (max 2s for testing)
            logger.info(f"Successfully simulated squeeze operation for {color}")
            return True
        
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

async def execute_multi_color_dispensing_task(cmd_id: str, color_ratios: ColorRatios, base_duration: float):
    """
    Background task to execute the complete timed laboratory procedure with multi-color dispensing.
    Creates a temporary modified sequence with dynamic squeeze durations and uses sequential_execute.py.
    
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
        
        # Load the original timed_laboratory_procedure from sequential_sequences.json
        sequences_file = os.path.join(os.path.dirname(__file__), "..", "temp_rules", "sequential_sequences.json")
        try:
            with open(sequences_file, 'r') as f:
                sequences_data = json.load(f)
            
            original_sequence = sequences_data["predefined_sequences"]["timed_laboratory_procedure"]["configurations"]
            execution_options = sequences_data["predefined_sequences"]["timed_laboratory_procedure"].get("execution_options", {})
            
            logger.info(f"Loaded original timed_laboratory_procedure with {len(original_sequence)} steps")
            
        except Exception as e:
            logger.error(f"Failed to load sequential_sequences.json: {e}")
            raise RuntimeError(f"Could not load timed_laboratory_procedure: {e}")
        
        # Calculate adjusted squeeze durations based on color ratios
        squeeze_adjustments = {}
        if color_ratios:
            total_ratio = color_ratios.red + color_ratios.yellow + color_ratios.blue
            if total_ratio > 0:
                # Normalize to 10 seconds total duration
                total_duration = 10.0
                squeeze_adjustments = {
                    "red": max(0.5, (color_ratios.red / total_ratio) * total_duration),
                    "yellow": max(0.5, (color_ratios.yellow / total_ratio) * total_duration), 
                    "blue": max(0.5, (color_ratios.blue / total_ratio) * total_duration)
                }
                logger.info(f"Normalized squeeze durations (10s total): {squeeze_adjustments}")
            else:
                # Use default durations if no valid ratios
                squeeze_adjustments = {"red": 1.5, "yellow": 2.5, "blue": 1.0}
        else:
            # Use default durations from sequential_sequences.json
            squeeze_adjustments = {"red": 1.5, "yellow": 2.5, "blue": 1.0}
        
        # Create modified sequence with dynamic squeeze durations
        modified_sequence = []
        color_sequence = ["red", "yellow", "blue"]  # Order of colors in the sequence
        color_index = 0
        
        for step in original_sequence:
            if "squeeze washing bottle" in step.lower():
                # Replace with dynamic duration
                current_color = color_sequence[color_index] if color_index < len(color_sequence) else "red"
                dynamic_duration = squeeze_adjustments.get(current_color, 1.5)
                modified_step = f"squeeze washing bottle for {dynamic_duration} seconds"
                modified_sequence.append(modified_step)
                color_index += 1
                logger.info(f"Modified squeeze step: {step} → {modified_step}")
            else:
                modified_sequence.append(step)
        
        # Create temporary sequence file
        temp_sequence_data = {
            "predefined_sequences": {
                f"temp_timed_laboratory_{cmd_id}": {
                    "name": f"temp_timed_laboratory_{cmd_id}",
                    "description": f"Temporary timed laboratory procedure with dynamic squeeze durations (cmd_id: {cmd_id})",
                    "configurations": modified_sequence,
                    "execution_options": execution_options
                }
            },
            "metadata": {
                "version": "1.0_temp",
                "description": "Temporary sequence with dynamic squeeze durations",
                "created_for_cmd_id": cmd_id,
                "original_sequence": "timed_laboratory_procedure"
            }
        }
        
        # Save temporary sequence file in untracked tmp directory
        tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        temp_sequence_file = os.path.join(tmp_dir, f"temp_sequence_{cmd_id}.json")
        try:
            with open(temp_sequence_file, 'w') as f:
                json.dump(temp_sequence_data, f, indent=2)
            logger.info(f"Created temporary sequence file: {temp_sequence_file}")
        except Exception as e:
            logger.error(f"Failed to create temporary sequence file: {e}")
            raise RuntimeError(f"Could not create temporary sequence: {e}")
        
        logger.info(f"Starting timed laboratory procedure for cmd_id={cmd_id}")
        logger.info(f"Total sequence steps: {len(modified_sequence)}")
        
        # Execute the modified sequence using sequential_execute.py
        try:
            if not REQUIRE_ROBOT:
                # Simulation mode
                logger.info(f"REQUIRE_ROBOT=false: Simulating timed laboratory procedure")
                await asyncio.sleep(5.0)  # Simulate full procedure (shortened for testing)
                logger.info(f"Successfully simulated timed laboratory procedure")
                success = True
            else:
                # Real execution
                sequential_execute_path = os.path.join(os.path.dirname(__file__), "sequential_execute.py")
                cmd = [
                    sys.executable,
                    sequential_execute_path,
                    f"temp_timed_laboratory_{cmd_id}",
                    "--smooth",
                    "--pause-between", str(execution_options.get("pause_between", 0.1)),
                    "--pause-after", str(execution_options.get("pause_after", 0.1)),
                    "--sequences-file", temp_sequence_file
                ]
                
                logger.info(f"Executing command: {' '.join(cmd)}")
                
                # Execute the complete sequence
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout for full sequence
                    cwd=os.path.dirname(__file__)
                )
                
                if result.returncode != 0:
                    logger.error(f"Sequential execution failed: {result.stderr}")
                    raise RuntimeError(f"Sequential execution failed: {result.stderr}")
                
                logger.info("Sequential execution completed successfully")
                success = True
                
        except subprocess.TimeoutExpired:
            logger.error("Timed laboratory procedure timed out")
            success = False
        except Exception as e:
            logger.error(f"Error during sequential execution: {e}")
            success = False
        finally:
            # Keep temporary sequence file for debugging and inspection
            # The file will remain in robot_service/tmp/ directory
            try:
                if os.path.exists(temp_sequence_file):
                    logger.info(f"Temporary sequence file preserved for debugging: {temp_sequence_file}")
                    logger.info(f"File contains the modified sequence with dynamic squeeze durations")
            except Exception as e:
                logger.warning(f"Could not check temporary file {temp_sequence_file}: {e}")
        
        if not success:
            async with TASKS_LOCK:
                TASKS[cmd_id].status = "failed"
                TASKS[cmd_id].error_message = "Sequential execution failed"
            raise RuntimeError("Sequential execution failed")
        
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
async def dispense(req: DispenseRequest, background_tasks: BackgroundTasks):
    """Handle dispense requests and start the background procedure."""
    REQS_TOTAL.inc()
    with REQ_LAT.time():
        return await _dispense_impl(req, background_tasks)

async def _dispense_impl(req: DispenseRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received dispense request: {req}")
    logger.info(f"color_ratios: {req.color_ratios}")
    logger.info(f"normalized_percentages: {req.normalized_percentages}")
    
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
            try:
                logger.info(f"Creating ColorRatios from: {req.color_ratios}")
                color_ratios = ColorRatios(
                    red=req.color_ratios.get("red", 0),
                    yellow=req.color_ratios.get("yellow", 0),
                    blue=req.color_ratios.get("blue", 0)
                )
                logger.info(f"ColorRatios created successfully: {color_ratios}")
            except Exception as e:
                logger.error(f"Failed to create ColorRatios: {e}")
                raise HTTPException(400, f"Invalid color ratios: {str(e)}")
            
            # Create task entry with extended fields for timed laboratory procedure
            try:
                logger.info(f"Creating DispenseStatus with cmd_id: {cmd_id}")
                task_status = DispenseStatus(
                    status="pending",
                    request_id=cmd_id,
                    operations=[],
                    completed_operations=[],
                    started_at=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                logger.info(f"DispenseStatus created successfully")
            except Exception as e:
                logger.error(f"Failed to create DispenseStatus: {e}")
                raise HTTPException(500, f"Task creation error: {str(e)}")
            
            try:
                async with TASKS_LOCK:
                    TASKS[cmd_id] = task_status
                logger.info(f"Task {cmd_id} added to TASKS dictionary")
            except Exception as e:
                logger.error(f"Failed to add task to TASKS: {e}")
                raise HTTPException(500, f"Task storage error: {str(e)}")
            
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
    logger.info("Processing legacy single-color request")
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


@app.post("/multi_color_dispensing")
async def multi_color_dispensing(req: SimpleMultiColorRequest, background_tasks: BackgroundTasks):
    """
    Direct endpoint for multi-color dispensing with timed laboratory procedure.
    This endpoint specifically handles the complete laboratory workflow with dynamic squeeze durations.
    """
    logger.info(f"Received multi-color dispensing request: {req}")
    
    try:
        # Generate unique command ID
        cmd_id = str(uuid.uuid4())
        
        # Convert dict to ColorRatios model
        color_ratios = ColorRatios(
            red=req.color_ratios.get("red", 0.0),
            yellow=req.color_ratios.get("yellow", 0.0),
            blue=req.color_ratios.get("blue", 0.0)
        )
        
        # Validate that at least one color has a non-zero ratio
        total_ratio = color_ratios.red + color_ratios.yellow + color_ratios.blue
        if total_ratio <= 0:
            raise HTTPException(400, "At least one color ratio must be greater than 0")
        
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
        
        # Start background task for complete laboratory procedure
        background_tasks.add_task(
            execute_multi_color_dispensing_task,
            cmd_id,
            color_ratios,
            req.base_duration
        )
        
        logger.info(f"Multi-color dispensing task started with cmd_id={cmd_id}")
        return {
            "cmd_id": cmd_id, 
            "status": "pending",
            "procedure": "timed_laboratory_procedure",
            "description": "Complete laboratory workflow with positioning, dispensing, squeezing, stirring, waiting, and beaker analysis",
            "color_ratios": {
                "red": color_ratios.red,
                "yellow": color_ratios.yellow,
                "blue": color_ratios.blue
            },
            "base_duration": req.base_duration
        }
        
    except Exception as e:
        logger.error(f"Error starting multi-color dispensing task: {e}")
        raise HTTPException(500, f"Multi-color dispensing error: {str(e)}")


@app.get("/task_status/{cmd_id}")
async def get_task_status(cmd_id: str):
    """Get the status of a multi-color dispensing task."""
    async with TASKS_LOCK:
        task = TASKS.get(cmd_id)
        
        if not task:
            raise HTTPException(404, f"Task {cmd_id} not found")
        
        return {
            "cmd_id": cmd_id,
            "status": task.status,
            "request_id": task.request_id,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "current_operation": task.current_operation,
            "error_message": task.error_message,
            "beaker_analysis_results": task.beaker_analysis_results
        }


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
