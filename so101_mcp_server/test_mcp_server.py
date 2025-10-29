"""
Test script for SO-101 MCP Server

Usage:
    python test_mcp_server.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from server import (
        PhosphobotClient,
        RobotServiceClient,
        SEQUENCES,
        ROBOT_CONFIG
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure dependencies are installed: uv sync")
    sys.exit(1)


def test_config_loading():
    """Test configuration file loading."""
    print("🧪 Testing configuration loading...")

    print(f"  • Sequences loaded: {len(SEQUENCES)}")
    if len(SEQUENCES) != 21:
        print(f"    ⚠️  Expected 21 sequences, got {len(SEQUENCES)}")
    else:
        print("    ✅ All 21 sequences loaded")

    print(f"  • Robot arms configured: {len(ROBOT_CONFIG.get('robot_arms', {}))}")
    left_arm = ROBOT_CONFIG.get('robot_arms', {}).get('left_arm', {})
    right_arm = ROBOT_CONFIG.get('robot_arms', {}).get('right_arm', {})

    print(f"    - Left arm: robot_id={left_arm.get('robot_id')}, device_id={left_arm.get('device_id')}")
    print(f"    - Right arm: robot_id={right_arm.get('robot_id')}, device_id={right_arm.get('device_id')}")

    print()


def test_phosphobot_client():
    """Test Phosphobot client initialization and health check."""
    print("🧪 Testing Phosphobot client...")

    client = PhosphobotClient()
    print(f"  • Base URL: {client.BASE_URL}")

    # Try health check
    result = client.get("/health")

    if result.get("status") == "error":
        print(f"  ⚠️  Connection failed: {result.get('error')}")
        print("     Make sure Phosphobot server is running:")
        print("     cd phosphobot && python -m uvicorn phosphobot.server:app --host 0.0.0.0 --port 80")
    else:
        print("  ✅ Phosphobot server connected")
        print(f"     Response: {json.dumps(result, indent=6)}")

    print()


def test_robot_service_client():
    """Test robot service client initialization."""
    print("🧪 Testing Robot Service client...")

    client = RobotServiceClient()
    print(f"  • Base URL: {client.BASE_URL}")

    # Try health check (if available)
    result = client.get("/health")

    if result.get("status") == "error":
        print(f"  ⚠️  Connection failed: {result.get('error')}")
        print("     Robot service may not be running on port 8001")
    else:
        print("  ✅ Robot service connected")

    print()


def test_sequence_listing():
    """Test sequence listing functionality."""
    print("🧪 Testing sequence listing...")

    print(f"  • Total sequences: {len(SEQUENCES)}")

    # Test a few key sequences
    test_sequences = [
        "full_lab_procedure",
        "multi_color_dispensing_workflow",
        "pick_paper_workflow",
        "timed_laboratory_procedure"
    ]

    for seq_name in test_sequences:
        if seq_name in SEQUENCES:
            seq = SEQUENCES[seq_name]
            configs = seq.get("configurations", [])
            print(f"  ✅ {seq_name}: {len(configs)} steps")
        else:
            print(f"  ❌ {seq_name}: NOT FOUND")

    print()


def test_special_functions():
    """Test special function detection in sequences."""
    print("🧪 Testing special functions in sequences...")

    special_functions = {
        "squeeze": 0,
        "await": 0,
        "take picture": 0,
        "capture image": 0,
        "analyze beaker": 0
    }

    for seq_name, seq_data in SEQUENCES.items():
        configs = seq_data.get("configurations", [])
        for config in configs:
            config_lower = config.lower()
            if "squeeze" in config_lower:
                special_functions["squeeze"] += 1
            if "await" in config_lower:
                special_functions["await"] += 1
            if "take picture" in config_lower or "capture image" in config_lower:
                special_functions["take picture"] += 1
            if "analyze beaker" in config_lower:
                special_functions["analyze beaker"] += 1

    print("  Special function occurrences:")
    for func, count in special_functions.items():
        print(f"    • {func}: {count} times")

    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("SO-101 MCP Server - Test Suite")
    print("=" * 60)
    print()

    test_config_loading()
    test_phosphobot_client()
    test_robot_service_client()
    test_sequence_listing()
    test_special_functions()

    print("=" * 60)
    print("✅ Test suite completed")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start Phosphobot server: cd phosphobot && uvicorn phosphobot.server:app --port 80")
    print("  2. Test MCP server: uv run mcp dev server.py")
    print("  3. Install to Claude Desktop: uv run mcp install server.py")
    print()


if __name__ == "__main__":
    main()
