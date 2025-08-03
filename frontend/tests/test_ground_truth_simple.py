#!/usr/bin/env python3
"""
Simplified ground truth calibration tests that work with direct imports.
These tests focus on testing the actual functionality without complex mocking.
"""

import sys
import os
import unittest
import tempfile
import json
import shutil
from pathlib import Path
import numpy as np

# Add the frontend directory to Python path
frontend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(frontend_dir))

# Import the functions we want to test
from main import load_ground_truth_calibration, BottleModel, _sample_reachable_rgb, generate_random_target_color


class TestGroundTruthSimple(unittest.TestCase):
    """Simple tests for ground truth calibration functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.ground_truth_dir = Path(self.test_dir) / "ground_truth_calibration"
        self.ground_truth_dir.mkdir(exist_ok=True)
        
        # Store original __file__ location to restore later
        self.original_file = sys.modules['main'].__file__
        
        # Temporarily change the module's __file__ to point to our test directory
        sys.modules['main'].__file__ = str(Path(self.test_dir) / "main.py")
        
    def tearDown(self):
        """Clean up test environment."""
        # Restore original __file__
        sys.modules['main'].__file__ = self.original_file
        
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_load_from_summary_file(self):
        """Test loading calibration matrix from summary file."""
        # Create a test calibration summary file
        summary_data = {
            "calibration_summary": {
                "calibration_matrix": {
                    "matrix": [
                        [0.8, 0.1, 0.05],
                        [0.1, 0.9, 0.1],
                        [0.05, 0.1, 0.85]
                    ]
                }
            }
        }
        
        summary_file = self.ground_truth_dir / "calibration_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f)
            
        # Test the function
        result = load_ground_truth_calibration()
        
        # Verify results
        self.assertEqual(result.shape, (3, 3))
        np.testing.assert_array_almost_equal(result, np.array([
            [0.8, 0.1, 0.05],
            [0.1, 0.9, 0.1],
            [0.05, 0.1, 0.85]
        ]))
        
    def test_load_from_individual_files(self):
        """Test loading from individual solution files when summary is missing."""
        # Create individual solution files
        red_data = {
            "calibration_parameters": {"absorbance_coefficient": 0.85},
            "color_measurement": {"rgb": [220, 85, 45]}
        }
        yellow_data = {
            "calibration_parameters": {"absorbance_coefficient": 0.72},
            "color_measurement": {"rgb": [245, 235, 65]}
        }
        blue_data = {
            "calibration_parameters": {"absorbance_coefficient": 0.78},
            "color_measurement": {"rgb": [95, 155, 185]}
        }
        
        # Save individual files
        with open(self.ground_truth_dir / "red_solution_ground_truth.json", 'w') as f:
            json.dump(red_data, f)
        with open(self.ground_truth_dir / "yellow_solution_ground_truth.json", 'w') as f:
            json.dump(yellow_data, f)
        with open(self.ground_truth_dir / "blue_solution_ground_truth.json", 'w') as f:
            json.dump(blue_data, f)
            
        # Test the function
        result = load_ground_truth_calibration()
        
        # Verify results
        self.assertEqual(result.shape, (3, 3))
        # Check that diagonal values match the coefficients
        self.assertAlmostEqual(result[0, 0], 0.85, places=2)
        self.assertAlmostEqual(result[1, 1], 0.72, places=2)
        self.assertAlmostEqual(result[2, 2], 0.78, places=2)
        
    def test_fallback_to_random_matrix(self):
        """Test fallback to random matrix when no files exist."""
        # Don't create any calibration files
        
        # Test the function
        result = load_ground_truth_calibration()
        
        # Verify we get a valid matrix
        self.assertEqual(result.shape, (3, 3))
        self.assertTrue(np.all(result >= 0))  # Should be all positive values
        
    def test_bottle_model_initialization(self):
        """Test BottleModel initialization with a ground truth matrix."""
        test_matrix = np.array([
            [0.8, 0.1, 0.05],
            [0.1, 0.9, 0.1],
            [0.05, 0.1, 0.85]
        ])
        
        bottle_model = BottleModel(test_matrix)
        
        # Verify the model was initialized correctly
        np.testing.assert_array_equal(bottle_model.P_est, test_matrix)
        self.assertIsNotNone(bottle_model.P_est)
        
    def test_sample_reachable_rgb(self):
        """Test _sample_reachable_rgb function."""
        test_matrix = np.array([
            [0.5, 0.1, 0.05],
            [0.1, 0.5, 0.1],
            [0.05, 0.1, 0.5]
        ])
        
        rgb, weights = _sample_reachable_rgb(test_matrix)
        
        # Verify RGB is valid
        self.assertEqual(len(rgb), 3)
        for value in rgb:
            self.assertTrue(0 <= value <= 255)
            self.assertIsInstance(value, (int, np.integer))
            
        # Verify weights are valid
        self.assertEqual(len(weights), 3)
        self.assertTrue(np.all(weights >= 0))
        
    def test_target_color_generation(self):
        """Test generate_random_target_color function."""
        # This test will use the actual ground truth files if they exist
        rgb = generate_random_target_color()
        
        # Verify RGB is valid
        self.assertEqual(len(rgb), 3)
        for value in rgb:
            self.assertTrue(0 <= value <= 255)
            self.assertIsInstance(value, (int, np.integer))


class TestRealGroundTruthFiles(unittest.TestCase):
    """Test with the actual ground truth files in the repository."""
    
    def setUp(self):
        """Set up test to use real ground truth files."""
        self.frontend_dir = Path(__file__).parent.parent
        self.ground_truth_dir = self.frontend_dir / "ground_truth_calibration"
        
    def test_real_calibration_files_exist(self):
        """Test that the real calibration files exist and are valid."""
        if not self.ground_truth_dir.exists():
            self.skipTest("Ground truth calibration directory doesn't exist")
            
        # Check for expected files
        expected_files = [
            "calibration_summary.json",
            "red_solution_ground_truth.json",
            "yellow_solution_ground_truth.json",
            "blue_solution_ground_truth.json"
        ]
        
        for filename in expected_files:
            file_path = self.ground_truth_dir / filename
            self.assertTrue(file_path.exists(), f"Missing file: {filename}")
            
            # Verify it's valid JSON
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, dict)
                
    def test_real_ground_truth_loading(self):
        """Test loading with real ground truth files."""
        if not self.ground_truth_dir.exists():
            self.skipTest("Ground truth calibration directory doesn't exist")
            
        # Test the actual loading function
        result = load_ground_truth_calibration()
        
        # Verify we get a valid matrix
        self.assertEqual(result.shape, (3, 3))
        self.assertTrue(np.all(result >= 0))  # Should be all positive
        self.assertFalse(np.all(result == 0))  # Should not be all zeros
        
        # Print the loaded matrix for inspection
        print(f"\n📊 Loaded ground truth matrix:")
        print(result)
        print(f"📊 Mean absorbance: {result.mean():.3f}")
        print(f"📊 Diagonal values: {np.diag(result)}")


def main():
    """Run the tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
