#!/usr/bin/env python3
"""
Ground Truth Calibration Utility for ColorOptimizer

This utility helps prepare ground-truth calibration instances by:
1. Running calibration sequences for red, yellow, and blue solutions
2. Converting measured color metrics to ColorOptimizer format
3. Calibrating solutions and saving ground truth data

Usage:
    python ground_truth_calibrator.py --solution red
    python ground_truth_calibrator.py --solution yellow  
    python ground_truth_calibrator.py --solution blue
    python ground_truth_calibrator.py --all
"""

import argparse
import json
import os
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, Tuple, Optional, Union
from datetime import datetime

class GroundTruthCalibrator:
    """
    Utility class for preparing ground-truth calibration instances
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the calibrator
        
        Args:
            base_dir: Base directory of the project (defaults to parent of utilities)
        """
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.utilities_dir = self.base_dir / "utilities"
        self.temp_rules_dir = self.base_dir / "temp_rules"
        self.ground_truth_dir = self.base_dir / "frontend" / "ground_truth_calibration"
        
        # Ensure ground truth directory exists
        self.ground_truth_dir.mkdir(exist_ok=True, parents=True)
        
        # Solution configurations
        self.solutions = {
            "red": {
                "sequence": "calibration_red_solution",
                "description": "Red solution calibration"
            },
            "yellow": {
                "sequence": "calibration_yellow_solution", 
                "description": "Yellow solution calibration"
            },
            "blue": {
                "sequence": "calibration_blue_solution",
                "description": "Blue solution calibration (with red base)"
            }
        }
    
    def run_calibration_sequence(self, solution: str) -> bool:
        """
        Run the calibration sequence for a given solution
        
        Args:
            solution: Solution name ('red', 'yellow', 'blue')
            
        Returns:
            True if sequence ran successfully, False otherwise
        """
        if solution not in self.solutions:
            print(f"Error: Unknown solution '{solution}'. Valid options: {list(self.solutions.keys())}")
            return False
            
        sequence_name = self.solutions[solution]["sequence"]
        description = self.solutions[solution]["description"]
        
        print(f"\n=== Step 1: Running {description} ===")
        print(f"Executing sequence: {sequence_name}")
        
        # Change to robot_service directory to run sequential_execute.py
        original_dir = os.getcwd()
        robot_service_dir = self.base_dir / "robot_service"
        try:
            os.chdir(robot_service_dir)
            
            # Run the calibration sequence
            cmd = ["python", "sequential_execute.py", sequence_name, "--smooth"]
            print(f"Command: {' '.join(cmd)}")
            print(f"Working directory: {robot_service_dir}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Calibration sequence completed successfully")
                print("Output:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                return True
            else:
                print("✗ Calibration sequence failed")
                print("Error:", result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Error running calibration sequence: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def parse_color_metric(self, color_input: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse color metric from various formats to RGB tuple
        
        Args:
            color_input: Color in format like "RGB(201, 236, 38)" or "#c9ec26"
            
        Returns:
            RGB tuple (r, g, b) or None if parsing failed
        """
        color_input = color_input.strip()
        
        # Try RGB format: RGB(r, g, b)
        rgb_match = re.match(r'RGB\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_input, re.IGNORECASE)
        if rgb_match:
            return tuple(int(x) for x in rgb_match.groups())
        
        # Try hex format: #rrggbb
        hex_match = re.match(r'#([0-9a-fA-F]{6})', color_input)
        if hex_match:
            hex_color = hex_match.group(1)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        
        # Try comma-separated values: r, g, b
        csv_match = re.match(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_input)
        if csv_match:
            return tuple(int(x) for x in csv_match.groups())
            
        return None
    
    def get_color_measurement(self, solution: str) -> Optional[Tuple[int, int, int]]:
        """
        Get color measurement - first check if ground truth data exists, otherwise get user input
        
        Args:
            solution: Solution name for display
            
        Returns:
            RGB tuple or None if input is invalid
        """
        print(f"\n=== Step 2: Convert measured color metric for {solution} solution ===")
        
        # Check if ground truth data already exists
        existing_file = self.ground_truth_dir / f"{solution}_solution_ground_truth.json"
        if existing_file.exists():
            try:
                with open(existing_file, 'r') as f:
                    existing_data = json.load(f)
                    existing_rgb = tuple(existing_data["color_measurement"]["rgb"])
                    
                print(f"Found existing ground truth data for {solution} solution:")
                print(f"  RGB: {existing_rgb}")
                print(f"  Hex: {existing_data['color_measurement']['hex']}")
                print(f"  Timestamp: {existing_data.get('timestamp', 'Unknown')}")
                
                use_existing = input(f"\nUse existing color measurement? (y/n): ").strip().lower()
                if use_existing in ['y', 'yes']:
                    print(f"✓ Using existing color measurement: RGB{existing_rgb}")
                    return existing_rgb
                else:
                    print("Will get new color measurement...")
            except Exception as e:
                print(f"Warning: Could not read existing ground truth file: {e}")
        
        # Get new color measurement from user input
        print("Please enter the color measurement from vision_bridge:")
        print("Supported formats:")
        print("  - RGB(201, 236, 38)")
        print("  - #c9ec26") 
        print("  - 201, 236, 38")
        
        while True:
            user_input = input(f"\nEnter {solution} solution color measurement: ").strip()
            
            if not user_input:
                print("Empty input. Please try again.")
                continue
                
            rgb = self.parse_color_metric(user_input)
            if rgb:
                print(f"✓ Parsed color: RGB{rgb}")
                confirm = input("Is this correct? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return rgb
                else:
                    print("Please enter the color measurement again.")
            else:
                print("✗ Could not parse color format. Please try again.")
    
    def calibrate_and_save(self, solution: str, rgb: Tuple[int, int, int]) -> bool:
        """
        Calibrate solution and save as ground truth
        
        Args:
            solution: Solution name
            rgb: RGB color measurement
            
        Returns:
            True if calibration saved successfully
        """
        print(f"\n=== Step 3: Calibrate {solution} solution and save ground truth ===")
        
        # Create simplified ground truth data structure with only obtainable information
        ground_truth_data = {
            "solution": solution,
            "color_measurement": {
                "rgb": list(rgb),
                "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                "format": f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})"
            },
            "calibration_sequence": self.solutions[solution]["sequence"],
            "timestamp": datetime.now().isoformat(),
            "description": self.solutions[solution]["description"]
        }
        
        # Save ground truth data
        output_file = self.ground_truth_dir / f"{solution}_solution_ground_truth.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(ground_truth_data, f, indent=2)
            
            print(f"✓ Ground truth data saved to: {output_file}")
            
            # Also save a summary file with all calibrations
            self._update_calibration_summary()
            
            return True
            
        except Exception as e:
            print(f"✗ Error saving ground truth data: {e}")
            return False
    
    def _update_calibration_summary(self):
        """Update the calibration summary file with all solutions"""
        summary_file = self.ground_truth_dir / "calibration_summary.json"
        
        summary_data = {
            "calibration_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_solutions": 0,
                "calibration_session_id": f"gt_calib_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "solutions": {}
            }
        }
        
        # Load existing ground truth files and build summary
        solutions_found = 0
        for solution in self.solutions.keys():
            gt_file = self.ground_truth_dir / f"{solution}_solution_ground_truth.json"
            if gt_file.exists():
                try:
                    with open(gt_file, 'r') as f:
                        data = json.load(f)
                        
                        # Simple solution summary with only measurable data
                        summary_data["calibration_summary"]["solutions"][solution] = {
                            "rgb": data["color_measurement"]["rgb"],
                            "hex": data["color_measurement"]["hex"],
                            "timestamp": data["timestamp"],
                            "sequence": data["calibration_sequence"]
                        }
                        
                        solutions_found += 1
                        
                except Exception as e:
                    print(f"Warning: Could not read {gt_file}: {e}")
        
        summary_data["calibration_summary"]["total_solutions"] = solutions_found
        
        try:
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2)
            print(f"✓ Updated calibration summary: {summary_file}")
        except Exception as e:
            print(f"Warning: Could not update summary file: {e}")
    
    def calibrate_solution(self, solution: str, auto_run: bool = True) -> bool:
        """
        Complete calibration process for a solution
        
        Args:
            solution: Solution name ('red', 'yellow', 'blue')
            auto_run: Whether to automatically run the calibration sequence
            
        Returns:
            True if all steps completed successfully
        """
        print(f"\n{'='*60}")
        print(f"GROUND TRUTH CALIBRATION FOR {solution.upper()} SOLUTION")
        print(f"{'='*60}")
        
        # Step 1: Run calibration sequence
        if auto_run:
            if not self.run_calibration_sequence(solution):
                return False
        else:
            print(f"\n=== Step 1: Manual sequence execution ===")
            print(f"Please run: cd robot_service && python sequential_execute.py {self.solutions[solution]['sequence']} --smooth")
            input("Press Enter after the sequence completes...")
        
        # Step 2: Get color measurement
        rgb = self.get_color_measurement(solution)
        if not rgb:
            print("✗ Failed to get valid color measurement")
            return False
        
        # Step 3: Save ground truth
        if not self.calibrate_and_save(solution, rgb):
            return False
        
        print(f"\n✓ {solution.capitalize()} solution calibration completed successfully!")
        return True
    
    def calibrate_all_solutions(self, auto_run: bool = True) -> bool:
        """
        Calibrate all solutions (red, yellow, blue)
        
        Args:
            auto_run: Whether to automatically run calibration sequences
            
        Returns:
            True if all calibrations completed successfully
        """
        print("Starting calibration for all solutions...")
        
        results = {}
        for solution in ["red", "yellow", "blue"]:
            print(f"\n\nStarting calibration for {solution} solution...")
            results[solution] = self.calibrate_solution(solution, auto_run)
            
            if not results[solution]:
                print(f"✗ Failed to calibrate {solution} solution")
            else:
                print(f"✓ Successfully calibrated {solution} solution")
        
        # Summary
        print(f"\n{'='*60}")
        print("CALIBRATION SUMMARY")
        print(f"{'='*60}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for solution, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{solution.capitalize()} solution: {status}")
        
        print(f"\nOverall: {success_count}/{total_count} solutions calibrated successfully")
        
        if success_count == total_count:
            print("\n🎉 All solutions calibrated successfully!")
            print(f"Ground truth data saved in: {self.ground_truth_dir}")
            return True
        else:
            print(f"\n⚠️  Some calibrations failed. Check the output above.")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Ground Truth Calibration Utility for ColorOptimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ground_truth_calibrator.py --solution red
  python ground_truth_calibrator.py --solution yellow
  python ground_truth_calibrator.py --solution blue
  python ground_truth_calibrator.py --all
  python ground_truth_calibrator.py --all --no-auto-run
        """
    )
    
    parser.add_argument(
        "--solution",
        choices=["red", "yellow", "blue"],
        help="Calibrate a specific solution"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Calibrate all solutions (red, yellow, blue)"
    )
    
    parser.add_argument(
        "--no-auto-run",
        action="store_true",
        help="Don't automatically run calibration sequences (manual execution)"
    )
    
    parser.add_argument(
        "--base-dir",
        help="Base directory of the project (defaults to parent of utilities)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.solution and not args.all:
        parser.error("Must specify either --solution or --all")
    
    if args.solution and args.all:
        parser.error("Cannot specify both --solution and --all")
    
    # Create calibrator instance
    calibrator = GroundTruthCalibrator(args.base_dir)
    
    auto_run = not args.no_auto_run
    
    try:
        if args.all:
            success = calibrator.calibrate_all_solutions(auto_run)
        else:
            success = calibrator.calibrate_solution(args.solution, auto_run)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nCalibration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
