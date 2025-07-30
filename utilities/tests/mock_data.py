#!/usr/bin/env python3
"""
Mock data generator for ground truth calibrator tests

This module provides mock data and scenarios for testing the calibrator
without requiring actual robot operations or user inputs.
"""

import json
import random
from typing import Dict, List, Tuple
from pathlib import Path

class MockDataGenerator:
    """Generates mock data for testing scenarios"""
    
    @staticmethod
    def generate_realistic_colors() -> Dict[str, Tuple[int, int, int]]:
        """Generate realistic color measurements for each solution"""
        return {
            "red": (220, 85, 45),      # Realistic red pigment color
            "yellow": (245, 235, 65),  # Realistic yellow pigment color
            "blue": (95, 155, 185)     # Realistic blue pigment color (with red base)
        }
    
    @staticmethod
    def generate_color_variations(base_color: Tuple[int, int, int], 
                                  variations: int = 5) -> List[Tuple[int, int, int]]:
        """Generate color variations around a base color"""
        colors = []
        r, g, b = base_color
        
        for _ in range(variations):
            # Add small random variations (±10)
            new_r = max(0, min(255, r + random.randint(-10, 10)))
            new_g = max(0, min(255, g + random.randint(-10, 10)))
            new_b = max(0, min(255, b + random.randint(-10, 10)))
            colors.append((new_r, new_g, new_b))
        
        return colors
    
    @staticmethod
    def generate_mock_subprocess_outputs() -> Dict[str, Dict[str, str]]:
        """Generate mock subprocess outputs for different scenarios"""
        return {
            "success": {
                "stdout": """
Executing sequence: calibration_red_solution
✓ Configuration loaded: left_arm_serving_standoff
✓ Configuration loaded: left_arm_standoff_with_beaker
✓ Configuration loaded: right_arm_standoff_yellow
✓ Configuration loaded: dispensing_red_to_beaker
✓ Squeezing washing bottle for 10 seconds
✓ Robot sequence completed successfully
✓ Color analysis completed: RGB(220, 85, 45)
Sequence execution time: 45.2 seconds
                """.strip(),
                "stderr": ""
            },
            "failure": {
                "stdout": "Starting sequence execution...",
                "stderr": """
Error: Failed to connect to robot controller
Robot communication timeout after 30 seconds
Sequence aborted for safety
                """.strip()
            },
            "partial_success": {
                "stdout": """
✓ Positioning sequence completed
✓ Solution dispensing completed
⚠ Warning: Squeeze bottle pressure low
✓ Stirring completed
✓ Color analysis completed with warning: RGB(180, 70, 30)
Note: Color measurement may be affected by low pressure
                """.strip(),
                "stderr": "Warning: Squeeze bottle pressure below optimal range"
            }
        }
    
    @staticmethod
    def create_mock_sequence_file(file_path: Path) -> None:
        """Create a mock sequential_sequences.json file for testing"""
        mock_sequences = {
            "predefined_sequences": {
                "calibration_red_solution": {
                    "name": "calibration_red_solution",
                    "description": "Calibration sequence for red solution",
                    "configurations": [
                        "left_arm_serving_standoff",
                        "left_arm_standoff_with_beaker",
                        "right_arm_standoff_yellow",
                        "dispensing_red_to_beaker",
                        "squeeze washing bottle for 10 seconds",
                        "right_arm_standoff_yellow",
                        "right_arm_standoff",
                        "left_arm_standoff_with_beaker",
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
                    ],
                    "execution_options": {
                        "smooth": True,
                        "description": "Ground-truth calibration procedure for red solution"
                    }
                },
                "calibration_yellow_solution": {
                    "name": "calibration_yellow_solution",
                    "description": "Calibration sequence for yellow solution",
                    "configurations": [
                        "left_arm_serving_standoff",
                        "left_arm_standoff_with_beaker",
                        "left_arm_standoff_yellow",
                        "right_arm_standoff_yellow",
                        "dispensing_yellow_to_beaker",
                        "squeeze washing bottle for 10 seconds",
                        "right_arm_standoff_yellow",
                        "right_arm_standoff",
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
                    ],
                    "execution_options": {
                        "smooth": True,
                        "description": "Ground-truth calibration procedure for yellow solution"
                    }
                },
                "calibration_blue_solution": {
                    "name": "calibration_blue_solution",
                    "description": "Calibration sequence for blue solution",
                    "configurations": [
                        "left_arm_serving_standoff",
                        "left_arm_standoff_with_beaker",
                        "right_arm_standoff_yellow",
                        "dispensing_red_to_beaker",
                        "squeeze washing bottle for 1.5 seconds",
                        "right_arm_standoff_yellow",
                        "left_arm_standoff_blue",
                        "dispensing_blue_to_beaker",
                        "squeeze washing bottle for 10 seconds",
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
                    ],
                    "execution_options": {
                        "smooth": True,
                        "description": "Ground-truth calibration procedure for blue solution"
                    }
                }
            },
            "metadata": {
                "version": "1.0",
                "description": "Mock sequences for testing",
                "total_sequences": 3
            }
        }
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(mock_sequences, f, indent=2)

class TestScenarios:
    """Pre-defined test scenarios for various testing situations"""
    
    @staticmethod
    def get_happy_path_scenario():
        """Get a complete successful calibration scenario"""
        return {
            "name": "happy_path",
            "description": "All calibrations succeed with typical colors",
            "solutions": {
                "red": {
                    "subprocess_result": {"returncode": 0, "stdout": "Red sequence success"},
                    "user_inputs": ["RGB(220, 85, 45)", "y"],
                    "expected_color": (220, 85, 45)
                },
                "yellow": {
                    "subprocess_result": {"returncode": 0, "stdout": "Yellow sequence success"},
                    "user_inputs": ["#f5eb41", "yes"],
                    "expected_color": (245, 235, 65)
                },
                "blue": {
                    "subprocess_result": {"returncode": 0, "stdout": "Blue sequence success"}, 
                    "user_inputs": ["95, 155, 185", "y"],
                    "expected_color": (95, 155, 185)
                }
            }
        }
    
    @staticmethod
    def get_error_recovery_scenario():
        """Get a scenario with errors and user corrections"""
        return {
            "name": "error_recovery",
            "description": "User makes mistakes but recovers successfully",
            "solutions": {
                "red": {
                    "subprocess_result": {"returncode": 0, "stdout": "Red sequence success"},
                    "user_inputs": [
                        "invalid_format",        # User mistake
                        "RGB(300, 400, 500)",    # Values out of range (still parses)
                        "n",                     # User rejects
                        "RGB(220, 85, 45)",      # Correct input
                        "y"                      # User accepts
                    ],
                    "expected_color": (220, 85, 45)
                }
            }
        }
    
    @staticmethod
    def get_mixed_results_scenario():
        """Get a scenario with mixed success/failure results"""
        return {
            "name": "mixed_results", 
            "description": "Some sequences succeed, others fail",
            "solutions": {
                "red": {
                    "subprocess_result": {"returncode": 0, "stdout": "Red sequence success"},
                    "user_inputs": ["RGB(220, 85, 45)", "y"],
                    "expected_color": (220, 85, 45),
                    "should_succeed": True
                },
                "yellow": {
                    "subprocess_result": {"returncode": 1, "stderr": "Robot connection failed"},
                    "user_inputs": [],  # No user input since sequence fails
                    "should_succeed": False
                },
                "blue": {
                    "subprocess_result": {"returncode": 0, "stdout": "Blue sequence success"},
                    "user_inputs": ["95, 155, 185", "y"],
                    "expected_color": (95, 155, 185),
                    "should_succeed": True
                }
            }
        }

def create_test_data_files(test_dir: Path):
    """Create all necessary test data files in the test directory"""
    
    # Create mock sequential_sequences.json
    MockDataGenerator.create_mock_sequence_file(
        test_dir / "temp_rules" / "sequential_sequences.json"
    )
    
    # Create sample ground truth files for testing
    sample_data = MockDataGenerator.generate_realistic_colors()
    
    gt_dir = test_dir / "ground_truth_calibration"
    gt_dir.mkdir(parents=True, exist_ok=True)
    
    for solution, color in sample_data.items():
        sample_gt = {
            "solution": solution,
            "color_measurement": {
                "rgb": list(color),
                "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                "format": f"RGB({color[0]}, {color[1]}, {color[2]})"
            },
            "calibration_sequence": f"calibration_{solution}_solution",
            "timestamp": "2025-07-30T12:00:00.000",
            "description": f"{solution.capitalize()} solution calibration",
            "notes": {
                "squeeze_time": "10 seconds",
                "stir_time": "10 seconds",
                "analysis_wait": "3 seconds"
            }
        }
        
        with open(gt_dir / f"sample_{solution}_ground_truth.json", 'w') as f:
            json.dump(sample_gt, f, indent=2)

if __name__ == "__main__":
    # Demo of mock data generation
    print("Mock Data Generator Demo")
    print("=" * 40)
    
    # Generate realistic colors
    colors = MockDataGenerator.generate_realistic_colors()
    print("Realistic solution colors:")
    for solution, color in colors.items():
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        print(f"  {solution}: RGB{color} / {hex_color}")
    
    print("\nColor variations for red solution:")
    variations = MockDataGenerator.generate_color_variations(colors["red"])
    for i, color in enumerate(variations, 1):
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        print(f"  Variation {i}: RGB{color} / {hex_color}")
    
    print("\nTest scenarios available:")
    scenarios = [
        TestScenarios.get_happy_path_scenario(),
        TestScenarios.get_error_recovery_scenario(), 
        TestScenarios.get_mixed_results_scenario()
    ]
    
    for scenario in scenarios:
        print(f"  - {scenario['name']}: {scenario['description']}")
