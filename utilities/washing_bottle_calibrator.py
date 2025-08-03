#!/usr/bin/env python3
"""
Washing Bottle Calibration Utility

This utility helps calibrate washing bottles by:
1. Taking color (red/yellow/blue) and squeeze duration as arguments
2. Executing robot arm sequences with custom squeeze durations
3. Supporting washing bottle calibration measurements

Usage:
    python washing_bottle_calibrator.py --color red --duration 5.0
    python washing_bottle_calibrator.py --color yellow --duration 7.5
    python washing_bottle_calibrator.py --color blue --duration 3.0
    python washing_bottle_calibrator.py --all --duration 6.0
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

class WashingBottleCalibrator:
    """
    Utility class for washing bottle calibration with custom squeeze durations
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
        self.robot_service_dir = self.base_dir / "robot_service"
        self.sequences_file = self.temp_rules_dir / "sequential_sequences.json"
        
        # Washing bottle sequence configurations
        self.washing_bottle_sequences = {
            "red": {
                "sequence": "calibration_red_washing_bottle",
                "description": "Red washing bottle calibration"
            },
            "yellow": {
                "sequence": "calibration_yellow_washing_bottle", 
                "description": "Yellow washing bottle calibration"
            },
            "blue": {
                "sequence": "calibration_blue_washing_bottle",
                "description": "Blue washing bottle calibration"
            }
        }
    
    def load_sequences(self) -> Dict:
        """
        Load the sequential sequences configuration
        
        Returns:
            Dictionary containing sequence configurations
        """
        try:
            with open(self.sequences_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sequences file {self.sequences_file}: {e}")
            return {}
    
    def create_custom_sequence(self, color: str, squeeze_duration: float) -> Optional[Dict]:
        """
        Create a custom sequence with the specified squeeze duration
        
        Args:
            color: Color name ('red', 'yellow', 'blue')
            squeeze_duration: Duration in seconds for bottle squeezing
            
        Returns:
            Modified sequence configuration or None if error
        """
        if color not in self.washing_bottle_sequences:
            print(f"Error: Unknown color '{color}'. Valid options: {list(self.washing_bottle_sequences.keys())}")
            return None
        
        # Load original sequences
        sequences_data = self.load_sequences()
        if not sequences_data:
            return None
        
        sequence_name = self.washing_bottle_sequences[color]["sequence"]
        
        if sequence_name not in sequences_data.get("predefined_sequences", {}):
            print(f"Error: Sequence '{sequence_name}' not found in sequences file")
            return None
        
        # Get the original sequence
        original_sequence = sequences_data["predefined_sequences"][sequence_name]
        
        # Create a copy for modification
        custom_sequence = original_sequence.copy()
        custom_sequence["configurations"] = original_sequence["configurations"].copy()
        
        # Replace squeeze duration in configurations
        for i, config in enumerate(custom_sequence["configurations"]):
            if isinstance(config, str) and config.startswith("squeeze washing bottle for"):
                # Replace with custom duration
                custom_sequence["configurations"][i] = f"squeeze washing bottle for {squeeze_duration} seconds"
                print(f"✓ Updated squeeze duration: {custom_sequence['configurations'][i]}")
        
        # Update sequence metadata
        custom_sequence["name"] = f"{sequence_name}_custom_{squeeze_duration}s"
        custom_sequence["description"] = f"{original_sequence['description']} - Custom squeeze duration: {squeeze_duration}s"
        
        return custom_sequence
    
    def create_temporary_sequences_file(self, custom_sequences: Dict[str, Dict]) -> Optional[str]:
        """
        Create a temporary sequences file with custom sequences
        
        Args:
            custom_sequences: Dictionary of custom sequences by color
            
        Returns:
            Path to temporary file or None if error
        """
        try:
            # Load original sequences
            sequences_data = self.load_sequences()
            if not sequences_data:
                return None
            
            # Add custom sequences
            for color, sequence in custom_sequences.items():
                sequences_data["predefined_sequences"][sequence["name"]] = sequence
            
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix=".json", prefix="washing_bottle_calibration_")
            
            with os.fdopen(temp_fd, 'w') as temp_file:
                json.dump(sequences_data, temp_file, indent=2)
            
            print(f"✓ Created temporary sequences file: {temp_path}")
            return temp_path
            
        except Exception as e:
            print(f"Error creating temporary sequences file: {e}")
            return None
    
    def execute_calibration_sequence(self, color: str, squeeze_duration: float, auto_run: bool = True) -> bool:
        """
        Execute calibration sequence with custom squeeze duration
        
        Args:
            color: Color name ('red', 'yellow', 'blue')
            squeeze_duration: Duration in seconds for bottle squeezing
            auto_run: Whether to automatically run the sequence
            
        Returns:
            True if sequence executed successfully, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"WASHING BOTTLE CALIBRATION FOR {color.upper()} SOLUTION")
        print(f"Squeeze Duration: {squeeze_duration} seconds")
        print(f"{'='*60}")
        
        if not auto_run:
            print(f"\n=== Manual execution mode ===")
            sequence_name = self.washing_bottle_sequences[color]["sequence"]
            print(f"Please manually run: cd robot_service && python sequential_execute.py {sequence_name} --smooth")
            print(f"Note: You'll need to manually adjust squeeze duration to {squeeze_duration} seconds")
            input("Press Enter after the sequence completes...")
            return True
        
        # Create custom sequence
        custom_sequence = self.create_custom_sequence(color, squeeze_duration)
        if not custom_sequence:
            return False
        
        # Create temporary sequences file
        temp_sequences_path = self.create_temporary_sequences_file({color: custom_sequence})
        if not temp_sequences_path:
            return False
        
        try:
            print(f"\n=== Executing {self.washing_bottle_sequences[color]['description']} ===")
            print(f"Sequence: {custom_sequence['name']}")
            print(f"Squeeze duration: {squeeze_duration} seconds")
            
            # Change to robot_service directory
            original_dir = os.getcwd()
            os.chdir(self.robot_service_dir)
            
            # Prepare command with temporary sequences file
            cmd = [
                "python", "sequential_execute.py", 
                custom_sequence["name"], 
                "--smooth",
                "--sequences-file", temp_sequences_path
            ]
            
            print(f"Command: {' '.join(cmd)}")
            print(f"Working directory: {self.robot_service_dir}")
            
            # Execute the sequence
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Washing bottle calibration sequence completed successfully")
                print("Output:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                return True
            else:
                print("✗ Washing bottle calibration sequence failed")
                print("Error:", result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Error executing calibration sequence: {e}")
            return False
        finally:
            # Cleanup
            os.chdir(original_dir)
            try:
                os.unlink(temp_sequences_path)
                print(f"✓ Cleaned up temporary file: {temp_sequences_path}")
            except Exception as e:
                print(f"Warning: Could not remove temporary file {temp_sequences_path}: {e}")
    
    def calibrate_all_colors(self, squeeze_duration: float, auto_run: bool = True) -> bool:
        """
        Calibrate all washing bottle colors with the same squeeze duration
        
        Args:
            squeeze_duration: Duration in seconds for bottle squeezing
            auto_run: Whether to automatically run sequences
            
        Returns:
            True if all calibrations completed successfully
        """
        print(f"\n{'='*60}")
        print("WASHING BOTTLE CALIBRATION FOR ALL COLORS")
        print(f"Squeeze Duration: {squeeze_duration} seconds")
        print(f"{'='*60}")
        
        results = {}
        colors = list(self.washing_bottle_sequences.keys())
        
        for i, color in enumerate(colors, 1):
            print(f"\n\n[{i}/{len(colors)}] Starting calibration for {color} washing bottle...")
            results[color] = self.execute_calibration_sequence(color, squeeze_duration, auto_run)
            
            if not results[color]:
                print(f"✗ Failed to calibrate {color} washing bottle")
            else:
                print(f"✓ Successfully calibrated {color} washing bottle")
            
            # Ask user if they want to continue to next color
            if i < len(colors) and auto_run:
                print(f"\nNext: {colors[i]} washing bottle calibration")
                continue_prompt = input("Continue to next color? (y/n): ").strip().lower()
                if continue_prompt not in ['y', 'yes']:
                    print("Calibration stopped by user")
                    break
        
        # Summary
        print(f"\n{'='*60}")
        print("WASHING BOTTLE CALIBRATION SUMMARY")
        print(f"{'='*60}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for color, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{color.capitalize()} washing bottle: {status}")
        
        print(f"\nOverall: {success_count}/{total_count} washing bottles calibrated successfully")
        print(f"Squeeze duration used: {squeeze_duration} seconds")
        
        if success_count == total_count:
            print("\n🎉 All washing bottle calibrations completed successfully!")
            return True
        else:
            print(f"\n⚠️  Some calibrations failed. Check the output above.")
            return False
    
    def validate_inputs(self, color: Optional[str], squeeze_duration: float) -> bool:
        """
        Validate input parameters
        
        Args:
            color: Color name (can be None for --all)
            squeeze_duration: Squeeze duration in seconds
            
        Returns:
            True if inputs are valid
        """
        # Validate squeeze duration
        if squeeze_duration <= 0:
            print(f"Error: Squeeze duration must be positive, got {squeeze_duration}")
            return False
        
        if squeeze_duration > 60:
            print(f"Warning: Squeeze duration {squeeze_duration}s is quite long (>60s)")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                return False
        
        # Validate color if specified
        if color and color not in self.washing_bottle_sequences:
            print(f"Error: Unknown color '{color}'. Valid options: {list(self.washing_bottle_sequences.keys())}")
            return False
        
        # Check if sequences file exists
        if not self.sequences_file.exists():
            print(f"Error: Sequences file not found: {self.sequences_file}")
            return False
        
        # Check if robot_service directory exists
        if not self.robot_service_dir.exists():
            print(f"Error: Robot service directory not found: {self.robot_service_dir}")
            return False
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Washing Bottle Calibration Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python washing_bottle_calibrator.py --color red --duration 5.0
  python washing_bottle_calibrator.py --color yellow --duration 7.5
  python washing_bottle_calibrator.py --color blue --duration 3.0
  python washing_bottle_calibrator.py --all --duration 6.0
  python washing_bottle_calibrator.py --color red --duration 4.5 --no-auto-run
        """
    )
    
    parser.add_argument(
        "--color",
        choices=["red", "yellow", "blue"],
        help="Calibrate a specific washing bottle color"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="Squeeze duration in seconds (e.g., 5.0, 7.5)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Calibrate all washing bottle colors with the same duration"
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
    if not args.color and not args.all:
        parser.error("Must specify either --color or --all")
    
    if args.color and args.all:
        parser.error("Cannot specify both --color and --all")
    
    # Create calibrator instance
    calibrator = WashingBottleCalibrator(args.base_dir)
    
    # Validate inputs
    if not calibrator.validate_inputs(args.color, args.duration):
        sys.exit(1)
    
    auto_run = not args.no_auto_run
    
    try:
        if args.all:
            success = calibrator.calibrate_all_colors(args.duration, auto_run)
        else:
            success = calibrator.execute_calibration_sequence(args.color, args.duration, auto_run)
        
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
