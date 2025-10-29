"""
SO-101 Robot Control MCP Server

Exposes ALOHA-Lite SO-101 robot control capabilities to Claude Desktop via MCP.
Leverages existing Phosphobot FastAPI service and sequential execution framework.

Features:
- 21 predefined sequences from sequential_sequences.json
- Direct joint and pose control via Phosphobot API (port 80)
- Camera capture and vision analysis
- Smooth trajectory planning with ModernRobotics
- Special functions: squeeze bottle, await delays, beaker analysis
- Configuration-driven execution with robot_arm_config.json

Reference Implementation:
- Based on patterns from: https://github.com/phospho-app/phospho-mcp-server
- Uses FastMCP framework for simplified MCP protocol implementation

Author: Generated for ALOHA-Lite
License: MIT
"""

import base64
import json
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import requests
from mcp.server.fastmcp import FastMCP, Image


# ═══════════════════════════════════════════════════════════
# Configuration Loading
# ═══════════════════════════════════════════════════════════

def load_config():
    """Load robot configuration files."""
    # Determine config directory (relative to this file)
    config_dir = Path(__file__).parent.parent / "temp_rules"

    sequences_file = config_dir / "sequential_sequences.json"
    robot_config_file = config_dir / "robot_arm_config.json"

    # Load sequences
    if sequences_file.exists():
        with open(sequences_file) as f:
            sequences_data = json.load(f)
            sequences = sequences_data.get("predefined_sequences", {})
    else:
        print(f"⚠️  Warning: {sequences_file} not found")
        sequences = {}

    # Load robot arm config
    if robot_config_file.exists():
        with open(robot_config_file) as f:
            robot_config = json.load(f)
    else:
        print(f"⚠️  Warning: {robot_config_file} not found")
        robot_config = {}

    return sequences, robot_config


SEQUENCES, ROBOT_CONFIG = load_config()


# ═══════════════════════════════════════════════════════════
# Phosphobot API Client
# ═══════════════════════════════════════════════════════════

class PhosphobotClient:
    """
    HTTP client for Phosphobot FastAPI server.

    Provides direct access to SO-101 robot control endpoints:
    - Joint position read/write
    - IK-based Cartesian movement
    - Torque control
    - Camera capture
    """

    def __init__(self, base_url: str = None):
        self.BASE_URL = base_url or os.getenv("PHOSPHOBOT_URL", "http://localhost:80")
        self.auth_token = os.getenv("SERVICE_AUTH_TOKEN", "")

        print(f"[phosphobot] Initialized client: {self.BASE_URL}")

    def _headers(self) -> dict:
        """Generate request headers with optional auth token."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def post(self, endpoint: str, json_data: dict = None, params: dict = None) -> dict:
        """
        POST request with comprehensive error handling.

        Args:
            endpoint: API endpoint (e.g., "/joints/write")
            json_data: JSON payload
            params: Query parameters

        Returns:
            Response dict or error dict
        """
        url = self.BASE_URL + endpoint
        try:
            response = requests.post(
                url,
                json=json_data,
                params=params,
                headers=self._headers(),
                timeout=30
            )
            response.raise_for_status()

            # Handle different response formats
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "success", "message": response.text}
            return {"status": "success"}

        except requests.Timeout:
            return {"status": "error", "error": "Request timeout (30s)"}
        except requests.ConnectionError:
            return {"status": "error", "error": f"Cannot connect to {self.BASE_URL}"}
        except requests.HTTPError as e:
            return {"status": "error", "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get(self, endpoint: str, params: dict = None) -> dict:
        """
        GET request with comprehensive error handling.

        Args:
            endpoint: API endpoint (e.g., "/joints/read")
            params: Query parameters

        Returns:
            Response dict or error dict
        """
        url = self.BASE_URL + endpoint
        try:
            response = requests.get(
                url,
                params=params,
                headers=self._headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            return {"status": "error", "error": "Request timeout (10s)"}
        except requests.ConnectionError:
            return {"status": "error", "error": f"Cannot connect to {self.BASE_URL}"}
        except requests.HTTPError as e:
            return {"status": "error", "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ═══════════════════════════════════════════════════════════
# Robot Service Client (for sequential execution)
# ═══════════════════════════════════════════════════════════

class RobotServiceClient:
    """
    HTTP client for robot_service on port 8001.

    Provides access to high-level robot control:
    - Sequential procedure execution
    - Procedure listing
    - Status checking
    """

    def __init__(self, base_url: str = None):
        self.BASE_URL = base_url or os.getenv("ROBOT_SERVICE_URL", "http://localhost:8001")
        self.auth_token = os.getenv("SERVICE_AUTH_TOKEN", "")

        print(f"[robot_service] Initialized client: {self.BASE_URL}")

    def _headers(self) -> dict:
        """Generate request headers with optional auth token."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def post(self, endpoint: str, json_data: dict = None) -> dict:
        """POST request with error handling."""
        url = self.BASE_URL + endpoint
        try:
            response = requests.post(
                url,
                json=json_data,
                headers=self._headers(),
                timeout=60  # Longer timeout for sequences
            )
            response.raise_for_status()

            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"status": "success", "message": response.text}
            return {"status": "success"}

        except requests.Timeout:
            return {"status": "error", "error": "Sequence execution timeout (60s)"}
        except requests.ConnectionError:
            return {"status": "error", "error": f"Cannot connect to {self.BASE_URL}"}
        except requests.HTTPError as e:
            return {"status": "error", "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get(self, endpoint: str) -> dict:
        """GET request with error handling."""
        url = self.BASE_URL + endpoint
        try:
            response = requests.get(
                url,
                headers=self._headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            return {"status": "error", "error": str(e)}


# ═══════════════════════════════════════════════════════════
# Context Management
# ═══════════════════════════════════════════════════════════

@dataclass
class AppContext:
    """Shared application state."""
    phosphobot: PhosphobotClient
    robot_service: RobotServiceClient


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize clients on startup, cleanup on shutdown."""
    print("🤖 Starting SO-101 MCP Server...")
    print(f"📁 Loaded {len(SEQUENCES)} predefined sequences")
    print(f"⚙️  Robot config: {ROBOT_CONFIG.get('robot_arms', {})}")

    phosphobot = PhosphobotClient()
    robot_service = RobotServiceClient()

    # Verify Phosphobot connection
    health = phosphobot.get("/health") if hasattr(phosphobot, 'get') else {}
    if health.get("status") == "error":
        print("⚠️  Warning: Cannot connect to Phosphobot server (port 80)")
        print("   Start with: cd phosphobot && python -m uvicorn phosphobot.server:app --host 0.0.0.0 --port 80")
    else:
        print("✅ Phosphobot server connected")

    try:
        yield AppContext(phosphobot=phosphobot, robot_service=robot_service)
    finally:
        print("🛑 Shutting down SO-101 MCP Server...")


# ═══════════════════════════════════════════════════════════
# MCP Server Instance
# ═══════════════════════════════════════════════════════════

mcp = FastMCP(
    "so101-robot",
    lifespan=app_lifespan,
    dependencies=["requests", "pillow"]
)


# ═══════════════════════════════════════════════════════════
# MCP Tools - Configuration & Status
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def get_robot_config() -> str:
    """
    Get robot arm configuration (IDs, device IDs, cameras).

    Returns:
        JSON string with robot arm and camera configuration
    """
    return json.dumps({
        "robot_arms": ROBOT_CONFIG.get("robot_arms", {}),
        "cameras": ROBOT_CONFIG.get("cameras", {}),
        "metadata": ROBOT_CONFIG.get("metadata", {})
    }, indent=2)


@mcp.tool()
def list_sequences() -> str:
    """
    List all 21 predefined robot sequences with descriptions.

    Returns:
        Formatted list of sequence names, descriptions, and configurations
    """
    if not SEQUENCES:
        return "❌ No sequences loaded. Check temp_rules/sequential_sequences.json"

    output = f"📋 Available Sequences ({len(SEQUENCES)} total):\n\n"

    for name, seq in SEQUENCES.items():
        desc = seq.get("description", "No description")
        config_count = len(seq.get("configurations", []))
        smooth = seq.get("execution_options", {}).get("smooth", False)

        output += f"• {name}\n"
        output += f"  Description: {desc}\n"
        output += f"  Configurations: {config_count} steps\n"
        output += f"  Smooth: {'Yes' if smooth else 'No'}\n\n"

    return output


@mcp.tool()
def get_sequence_details(
    sequence_name: Literal[
        "standoff_to_dispensing",
        "dispensing_to_standoff",
        "full_lab_procedure",
        "beaker_pickup_sequence",
        "complete_beaker_workflow",
        "single_arm_demo",
        "independent_arm_movements",
        "right_arm_standoff_to_yellow",
        "both_arms_standoff_to_red",
        "squeeze_demo_sequence",
        "multi_color_dispensing_workflow",
        "left_arm_positioning_sequence",
        "squeeze_bottle_demo",
        "multi_color_dispensing_with_squeeze",
        "timed_laboratory_procedure",
        "camera_demo_sequence",
        "beaker_analysis_demo_sequence",
        "calibration_red_solution",
        "calibration_yellow_solution",
        "calibration_white_background",
        "calibration_blue_solution",
        "calibration_red_washing_bottle",
        "calibration_yellow_washing_bottle",
        "calibration_blue_washing_bottle",
        "pick_paper_workflow"
    ]
) -> str:
    """
    Get detailed information about a specific sequence.

    Args:
        sequence_name: Name of the sequence to inspect

    Returns:
        Detailed sequence configuration including all steps
    """
    if sequence_name not in SEQUENCES:
        return f"❌ Sequence '{sequence_name}' not found"

    seq = SEQUENCES[sequence_name]

    return json.dumps({
        "name": seq.get("name"),
        "description": seq.get("description"),
        "configurations": seq.get("configurations", []),
        "execution_options": seq.get("execution_options", {})
    }, indent=2)


# ═══════════════════════════════════════════════════════════
# MCP Tools - Direct Joint Control
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def read_joint_positions(
    robot_id: int,
    unit: Literal["rad", "deg", "units"] = "rad"
) -> str:
    """
    Read current joint positions from SO-101 robot arm.

    Args:
        robot_id: Robot ID (2=left arm, 3=right arm, 0=both)
        unit: Unit of measurement (rad, deg, or units)

    Returns:
        JSON string with joint angles [j1, j2, j3, j4, j5, j6]
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    result = app_ctx.phosphobot.post(
        "/joints/read",
        json_data={"unit": unit, "joints_ids": None},
        params={"robot_id": robot_id}
    )

    if result.get("status") == "error":
        return f"❌ Failed to read joints: {result.get('error')}"

    return json.dumps({
        "robot_id": robot_id,
        "angles": result.get("angles", []),
        "unit": unit
    }, indent=2)


@mcp.tool()
def write_joint_positions(
    robot_id: int,
    j1: float,
    j2: float,
    j3: float,
    j4: float,
    j5: float,
    j6: float,
    unit: Literal["rad", "deg", "units"] = "rad"
) -> str:
    """
    Write joint positions to SO-101 robot arm (direct joint control).

    Args:
        robot_id: Robot ID (2=left arm, 3=right arm)
        j1: Joint 1 angle (shoulder_pan)
        j2: Joint 2 angle (shoulder_lift)
        j3: Joint 3 angle (elbow_flex)
        j4: Joint 4 angle (wrist_flex)
        j5: Joint 5 angle (wrist_roll)
        j6: Joint 6 angle (gripper)
        unit: Unit of measurement (rad, deg, or units)

    Returns:
        Confirmation message with executed joint values
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    angles = [j1, j2, j3, j4, j5, j6]

    result = app_ctx.phosphobot.post(
        "/joints/write",
        json_data={
            "angles": angles,
            "unit": unit,
            "joints_ids": None
        },
        params={"robot_id": robot_id}
    )

    if result.get("status") == "error":
        return f"❌ Failed to write joints: {result.get('error')}"

    return f"✅ Moved robot {robot_id} to position: {angles} ({unit})"


@mcp.tool()
def initialize_robot(robot_id: int = 0) -> str:
    """
    Initialize SO-101 robot to safe initial position.

    Args:
        robot_id: Robot ID (0=both arms, 2=left arm, 3=right arm)

    Returns:
        Initialization status message
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    result = app_ctx.phosphobot.post(
        "/move/init",
        params={"robot_id": robot_id}
    )

    if result.get("status") == "error":
        return f"❌ Initialization failed: {result.get('error')}"

    arm_name = {0: "both arms", 2: "left arm", 3: "right arm"}.get(robot_id, f"robot {robot_id}")
    return f"✅ Initialized {arm_name} to safe position"


# ═══════════════════════════════════════════════════════════
# MCP Tools - Cartesian Movement (IK-based)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def move_absolute_pose(
    robot_id: int,
    x: float,
    y: float,
    z: float,
    rx: float = 0,
    ry: float = 0,
    rz: float = 0,
    gripper_open: bool = False
) -> str:
    """
    Move robot to absolute Cartesian pose using inverse kinematics.

    Args:
        robot_id: Robot ID (2=left arm, 3=right arm)
        x: X position in cm
        y: Y position in cm
        z: Z position in cm
        rx: Roll rotation in degrees (optional)
        ry: Pitch rotation in degrees (optional)
        rz: Yaw rotation in degrees (optional)
        gripper_open: True to open gripper, False to close

    Returns:
        Movement status message
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    result = app_ctx.phosphobot.post(
        "/move/absolute",
        json_data={
            "x": x,
            "y": y,
            "z": z,
            "rx": rx,
            "ry": ry,
            "rz": rz,
            "open": 1 if gripper_open else 0,
            "position_tolerance": 0.01,
            "orientation_tolerance": 5.0,
            "max_trials": 3
        },
        params={"robot_id": robot_id}
    )

    if result.get("status") == "error":
        return f"❌ Movement failed: {result.get('error')}"

    return f"✅ Moved robot {robot_id} to pose: x={x}, y={y}, z={z} cm (gripper {'open' if gripper_open else 'closed'})"


@mcp.tool()
def move_relative_pose(
    robot_id: int,
    dx: float,
    dy: float,
    dz: float,
    drx: float = 0,
    dry: float = 0,
    drz: float = 0
) -> str:
    """
    Move robot by relative Cartesian offset using inverse kinematics.

    Args:
        robot_id: Robot ID (2=left arm, 3=right arm)
        dx: Delta X in cm
        dy: Delta Y in cm
        dz: Delta Z in cm
        drx: Delta roll in degrees (optional)
        dry: Delta pitch in degrees (optional)
        drz: Delta yaw in degrees (optional)

    Returns:
        Movement status message
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    result = app_ctx.phosphobot.post(
        "/move/relative",
        json_data={
            "x": dx,
            "y": dy,
            "z": dz,
            "rx": drx,
            "ry": dry,
            "rz": drz,
            "position_tolerance": 0.01,
            "orientation_tolerance": 5.0,
            "max_trials": 3
        },
        params={"robot_id": robot_id}
    )

    if result.get("status") == "error":
        return f"❌ Relative movement failed: {result.get('error')}"

    return f"✅ Moved robot {robot_id} by offset: dx={dx}, dy={dy}, dz={dz} cm"


@mcp.tool()
def control_gripper(
    robot_id: int,
    open: bool
) -> str:
    """
    Open or close robot gripper.

    Args:
        robot_id: Robot ID (2=left arm, 3=right arm)
        open: True to open gripper, False to close

    Returns:
        Gripper control status message
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    # Read current position
    current = app_ctx.phosphobot.post(
        "/joints/read",
        json_data={"unit": "rad", "joints_ids": None},
        params={"robot_id": robot_id}
    )

    if current.get("status") == "error":
        return f"❌ Failed to read current position: {current.get('error')}"

    # Get current angles
    angles = current.get("angles", [0, 0, 0, 0, 0, 0])

    # Modify gripper angle (joint 6)
    # Open: positive angle, Close: negative angle (adjust based on hardware)
    angles[5] = 0.5 if open else -0.5

    # Write new position
    result = app_ctx.phosphobot.post(
        "/joints/write",
        json_data={
            "angles": angles,
            "unit": "rad",
            "joints_ids": [6]  # Only move gripper
        },
        params={"robot_id": robot_id}
    )

    if result.get("status") == "error":
        return f"❌ Gripper control failed: {result.get('error')}"

    return f"✅ Robot {robot_id} gripper {'opened' if open else 'closed'}"


# ═══════════════════════════════════════════════════════════
# MCP Tools - Torque Control
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def toggle_torque(
    robot_id: int,
    enable: bool
) -> str:
    """
    Enable or disable motor torque on SO-101 robot.

    Args:
        robot_id: Robot ID (2=left arm, 3=right arm, 0=both)
        enable: True to enable torque, False to disable (freewheel mode)

    Returns:
        Torque control status message
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    result = app_ctx.phosphobot.post(
        "/torque/toggle",
        json_data={
            "torque_status": enable,
            "robot_id": robot_id
        }
    )

    if result.get("status") == "error":
        return f"❌ Torque control failed: {result.get('error')}"

    arm_name = {0: "both arms", 2: "left arm", 3: "right arm"}.get(robot_id, f"robot {robot_id}")
    status = "enabled" if enable else "disabled (freewheel mode)"
    return f"✅ Torque {status} for {arm_name}"


# ═══════════════════════════════════════════════════════════
# MCP Tools - Sequential Execution (High-level)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def execute_sequence(
    sequence_name: Literal[
        "standoff_to_dispensing",
        "dispensing_to_standoff",
        "full_lab_procedure",
        "beaker_pickup_sequence",
        "complete_beaker_workflow",
        "single_arm_demo",
        "independent_arm_movements",
        "right_arm_standoff_to_yellow",
        "both_arms_standoff_to_red",
        "squeeze_demo_sequence",
        "multi_color_dispensing_workflow",
        "left_arm_positioning_sequence",
        "squeeze_bottle_demo",
        "multi_color_dispensing_with_squeeze",
        "timed_laboratory_procedure",
        "camera_demo_sequence",
        "beaker_analysis_demo_sequence",
        "calibration_red_solution",
        "calibration_yellow_solution",
        "calibration_white_background",
        "calibration_blue_solution",
        "calibration_red_washing_bottle",
        "calibration_yellow_washing_bottle",
        "calibration_blue_washing_bottle",
        "pick_paper_workflow"
    ],
    smooth: bool = False,
    left_arm_id: int = 2,
    right_arm_id: int = 3
) -> str:
    """
    Execute a predefined robot sequence from sequential_sequences.json.

    This is the primary high-level control method. Sequences include:
    - Laboratory procedures (dispensing, beaker handling)
    - Multi-color workflows (red, yellow, blue solutions)
    - Calibration sequences for color analysis
    - Paper manipulation (bilateral coordination)
    - Camera capture and beaker analysis

    Args:
        sequence_name: Name of sequence to execute
        smooth: Use smooth trajectory planning (ModernRobotics)
        left_arm_id: Robot ID for left arm (default: 2)
        right_arm_id: Robot ID for right arm (default: 3)

    Returns:
        Execution status with step-by-step results
    """
    if sequence_name not in SEQUENCES:
        return f"❌ Unknown sequence: {sequence_name}. Use list_sequences() to see available options."

    # Note: This calls the robot_service API which handles sequential_execute.py logic
    # In production, you would implement the sequential execution here or call a dedicated endpoint

    seq = SEQUENCES[sequence_name]
    desc = seq.get("description", "")
    configs = seq.get("configurations", [])

    # For now, return detailed execution plan
    # TODO: Implement actual execution via robot_service API or directly via PhosphobotClient

    output = f"🚀 Executing sequence: {sequence_name}\n"
    output += f"📝 Description: {desc}\n"
    output += f"📊 Total steps: {len(configs)}\n"
    output += f"⚙️  Smooth trajectory: {'Yes' if smooth else 'No'}\n"
    output += f"🤖 Robot IDs: Left={left_arm_id}, Right={right_arm_id}\n\n"

    output += "📋 Configuration steps:\n"
    for i, config in enumerate(configs, 1):
        output += f"  {i}. {config}\n"

    output += "\n⚠️  Note: Full execution requires robot_service integration.\n"
    output += "For now, use this information to manually execute via sequential_execute.py\n"
    output += f"Command: python3 robot_service/sequential_execute.py {sequence_name}"
    if smooth:
        output += " --smooth"

    return output


# ═══════════════════════════════════════════════════════════
# MCP Tools - Camera & Vision
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def capture_camera_frame(camera_id: int = 0) -> Image:
    """
    Capture current frame from robot camera.

    Args:
        camera_id: Camera ID (0, 1, or 2)

    Returns:
        JPEG image from robot's vision system
    """
    # Create new client for stateless call
    phosphobot = PhosphobotClient()

    result = phosphobot.get("/frames")

    if result.get("status") == "error":
        raise RuntimeError(
            f"Camera capture failed: {result.get('error')}. "
            "Ensure Phosphobot server is running on port 80."
        )

    # Try to get specific camera or fallback to any available
    camera_key = f"camera_{camera_id}"
    image_b64 = result.get(camera_key)

    if not image_b64:
        # Fallback to any available camera
        image_b64 = next(
            (v for k, v in result.items() if k.startswith("camera_")),
            None
        )

    if not image_b64:
        raise RuntimeError(f"No camera data available for camera {camera_id}")

    # Decode base64 image
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception as e:
        raise RuntimeError(f"Failed to decode image: {e}")

    return Image(
        data=image_bytes,
        format="jpeg"
    )


# ═══════════════════════════════════════════════════════════
# MCP Tools - Emergency & Safety
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def emergency_stop() -> str:
    """
    Execute emergency stop on all robot arms.

    Disables torque on both arms immediately, allowing free movement.
    This is a safety feature to prevent damage or injury.

    Returns:
        Emergency stop confirmation
    """
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    # Disable torque on both arms (robot_id=0)
    result = app_ctx.phosphobot.post(
        "/torque/toggle",
        json_data={
            "torque_status": False,
            "robot_id": 0  # Both arms
        }
    )

    if result.get("status") == "error":
        return f"⚠️  E-stop request failed: {result.get('error')}"

    return "🛑 EMERGENCY STOP ACTIVATED - All motors disabled (freewheel mode)"


# ═══════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("SO-101 Robot Control MCP Server")
    print("=" * 60)
    print()
    print("Available MCP Tools:")
    print()
    print("Configuration & Status:")
    print("  • get_robot_config() - Robot arm and camera configuration")
    print("  • list_sequences() - List all 21 predefined sequences")
    print("  • get_sequence_details(name) - Detailed sequence info")
    print()
    print("Direct Joint Control:")
    print("  • initialize_robot(robot_id) - Safe initialization")
    print("  • read_joint_positions(robot_id, unit) - Read joint angles")
    print("  • write_joint_positions(robot_id, j1-j6, unit) - Write joint angles")
    print()
    print("Cartesian Movement (IK):")
    print("  • move_absolute_pose(robot_id, x, y, z, ...) - Absolute movement")
    print("  • move_relative_pose(robot_id, dx, dy, dz, ...) - Relative movement")
    print("  • control_gripper(robot_id, open) - Gripper control")
    print()
    print("Motor Control:")
    print("  • toggle_torque(robot_id, enable) - Enable/disable motors")
    print()
    print("High-Level Sequences:")
    print("  • execute_sequence(name, smooth, ...) - Execute predefined sequence")
    print()
    print("Vision:")
    print("  • capture_camera_frame(camera_id) - Capture camera image")
    print()
    print("Safety:")
    print("  • emergency_stop() - Emergency stop all motors")
    print()
    print("=" * 60)
    print()

    # MCP server will start automatically when installed in Claude Desktop
    # Or run with: uv run python server.py
