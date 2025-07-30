#!/usr/bin/env python3
"""
Demo script showing the ground truth calibrator in action with mock data

This script demonstrates how the calibrator works without requiring
actual robot hardware, using the same mocking techniques as the tests.
"""

import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ground_truth_calibrator import GroundTruthCalibrator

def demo_calibrator():
    """Demonstrate the calibrator with mock robot operations"""
    
    print("🤖 GROUND TRUTH CALIBRATOR DEMO")
    print("=" * 50)
    print("This demo shows the calibrator working with mocked robot operations")
    print()
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        calibrator = GroundTruthCalibrator(temp_dir)
        
        print(f"📁 Using temporary directory: {temp_dir}")
        print(f"📊 Ground truth data will be saved to: {calibrator.ground_truth_dir}")
        print()
        
        # Demo 1: Color parsing
        print("🎨 DEMO 1: Color Format Parsing")
        print("-" * 30)
        
        test_colors = [
            "RGB(220, 85, 45)",
            "#f5eb41", 
            "95, 155, 185",
            "invalid_format"
        ]
        
        for color_input in test_colors:
            parsed = calibrator.parse_color_metric(color_input)
            if parsed:
                hex_color = f"#{parsed[0]:02x}{parsed[1]:02x}{parsed[2]:02x}"
                print(f"  Input: {color_input:15} → RGB{parsed} / {hex_color}")
            else:
                print(f"  Input: {color_input:15} → ❌ Invalid format")
        
        print()
        
        # Demo 2: Mocked calibration workflow
        print("🔧 DEMO 2: Mocked Calibration Workflow")
        print("-" * 40)
        
        # Mock subprocess (robot execution) and user input
        with patch('subprocess.run') as mock_subprocess, \
             patch('builtins.input') as mock_input:
            
            # Setup mock subprocess to simulate successful robot execution
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout="✓ Robot sequence completed\n✓ Color analysis: RGB(220, 85, 45)"
            )
            
            # Setup mock user input (realistic interaction)
            mock_input.side_effect = [
                "RGB(220, 85, 45)",  # User enters color measurement
                "y"                   # User confirms
            ]
            
            print("Simulating red solution calibration...")
            
            # Run the calibration
            success = calibrator.calibrate_solution("red", auto_run=True)
            
            if success:
                print("✅ Calibration completed successfully!")
                
                # Show the generated ground truth file
                gt_file = calibrator.ground_truth_dir / "red_solution_ground_truth.json"
                if gt_file.exists():
                    with open(gt_file, 'r') as f:
                        data = json.load(f)
                    
                    print("\n📄 Generated Ground Truth Data:")
                    print(f"  Solution: {data['solution']}")
                    print(f"  RGB Color: {data['color_measurement']['rgb']}")
                    print(f"  Hex Color: {data['color_measurement']['hex']}")
                    print(f"  Sequence: {data['calibration_sequence']}")
                    print(f"  Timestamp: {data['timestamp']}")
                    
            else:
                print("❌ Calibration failed")
        
        print()
        
        # Demo 3: Summary file generation
        print("📋 DEMO 3: Summary File Generation")
        print("-" * 35)
        
        # Add more solutions to demonstrate summary
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["y"]  # Just confirm existing data
            
            # Manually create additional ground truth files
            solutions_data = {
                "yellow": (245, 235, 65),
                "blue": (95, 155, 185)
            }
            
            for solution, rgb in solutions_data.items():
                calibrator.calibrate_and_save(solution, rgb)
            
            # Show summary
            summary_file = calibrator.ground_truth_dir / "calibration_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                
                print("📊 Calibration Summary:")
                for solution, data in summary["calibration_summary"]["solutions"].items():
                    rgb = data["rgb"]
                    hex_color = data["hex"]
                    print(f"  {solution.capitalize():6}: RGB{rgb} / {hex_color}")
        
        print()
        print("🎉 Demo completed! All operations were mocked - no robot hardware required.")
        print(f"🗂️  Files created in: {calibrator.ground_truth_dir}")
        
        # List created files
        files = list(calibrator.ground_truth_dir.glob("*.json"))
        if files:
            print("\n📁 Generated Files:")
            for file in files:
                print(f"  - {file.name}")

if __name__ == "__main__":
    demo_calibrator()
