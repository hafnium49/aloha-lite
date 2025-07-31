#!/usr/bin/env python3
"""
Comprehensive test suite for ground truth calibration integration in frontend/main.py

Tests the load_ground_truth_calibration() function, BottleModel initialization,
and related functionality with various scenarios including missing files,
malformed data, and different calibration data formats.
"""

import unittest
import json
import tempfile
import shutil
import numpy as np
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Add the frontend directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestGroundTruthCalibration(unittest.TestCase):
    """Test ground truth calibration loading functionality."""
    
    def setUp(self):
        """Set up test fixtures and mock data."""
        self.temp_dir = tempfile.mkdtemp()
        self.ground_truth_dir = Path(self.temp_dir) / "ground_truth_calibration"
        self.ground_truth_dir.mkdir()
        
        # Sample calibration summary data (updated for 4x3 matrix)
        self.valid_summary_data = {
            "calibration_summary": {
                "timestamp": "2025-07-30T14:36:00.123456",
                "total_solutions": 3,
                "calibration_matrix": {
                    "description": "Derived 4x3 absorbance matrix including white solvent",
                    "matrix": [
                        [0.85, 0.12, 0.08],
                        [0.15, 0.72, 0.11],
                        [0.18, 0.16, 0.78],
                        [0.00, 0.00, 0.00]  # White solvent row
                    ],
                    "units": "absorbance per unit volume"
                }
            }
        }
        
        # Sample individual solution data
        self.valid_red_solution = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.85,
                "concentration": "10mg/mL"
            },
            "color_measurement": {
                "rgb": [220, 85, 45],
                "hex": "#dc552d"
            }
        }
        
        self.valid_yellow_solution = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.72,
                "concentration": "8mg/mL"
            },
            "color_measurement": {
                "rgb": [245, 235, 65],
                "hex": "#f5eb41"
            }
        }
        
        self.valid_blue_solution = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.78,
                "concentration": "12mg/mL"
            },
            "color_measurement": {
                "rgb": [95, 155, 185],
                "hex": "#5f9bb9"
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_summary_file(self, data=None):
        """Helper to create calibration summary file."""
        if data is None:
            data = self.valid_summary_data
        summary_file = self.ground_truth_dir / "calibration_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(data, f)
        return summary_file
    
    def create_solution_files(self):
        """Helper to create individual solution files."""
        solutions = {
            "red": self.valid_red_solution,
            "yellow": self.valid_yellow_solution,
            "blue": self.valid_blue_solution
        }
        
        files = {}
        for color, data in solutions.items():
            file_path = self.ground_truth_dir / f"{color}_solution_ground_truth.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)
            files[color] = file_path
        return files
    
    @patch('main.Path')
    @patch('main.logger')
    def test_load_from_calibration_summary_success(self, mock_logger, mock_path):
        """Test successful loading from calibration summary file."""
        # Mock Path behavior
        mock_path.return_value.parent = self.ground_truth_dir.parent
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value = mock_file_path
        
        # Create the actual summary file
        self.create_summary_file()
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=json.dumps(self.valid_summary_data))):
            from main import load_ground_truth_calibration
            
            result = load_ground_truth_calibration()
            
            # Verify matrix shape and values (updated for 4x3 matrix)
            self.assertEqual(result.shape, (4, 3))
            expected_matrix = np.array([
                [0.85, 0.12, 0.08],
                [0.15, 0.72, 0.11],
                [0.18, 0.16, 0.78],
                [0.00, 0.00, 0.00]  # White solvent row
            ])
            np.testing.assert_array_equal(result, expected_matrix)
            
            # Verify logging calls
            mock_logger.info.assert_any_call("🎯 Loaded ground truth matrix from calibration summary")
    
    @patch('main.Path')
    @patch('main.logger')
    def test_load_from_individual_files_fallback(self, mock_logger, mock_path):
        """Test fallback to individual solution files when summary is missing."""
        # Mock Path behavior - summary file doesn't exist, individual files do
        mock_path.return_value.parent = self.ground_truth_dir.parent
        
        summary_mock = MagicMock()
        summary_mock.exists.return_value = False
        
        solution_mocks = {}
        for color in ["red", "yellow", "blue"]:
            solution_mock = MagicMock()
            solution_mock.exists.return_value = True
            solution_mocks[color] = solution_mock
        
        def path_side_effect(subpath):
            if "calibration_summary.json" in str(subpath):
                return summary_mock
            for color in ["red", "yellow", "blue"]:
                if f"{color}_solution_ground_truth.json" in str(subpath):
                    return solution_mocks[color]
            return MagicMock()
        
        mock_path.return_value.parent.__truediv__.side_effect = path_side_effect
        
        # Mock file reading for individual solutions
        solution_data = {
            "red_solution_ground_truth.json": json.dumps(self.valid_red_solution),
            "yellow_solution_ground_truth.json": json.dumps(self.valid_yellow_solution),
            "blue_solution_ground_truth.json": json.dumps(self.valid_blue_solution)
        }
        
        def mock_open_side_effect(filename, mode='r'):
            for file_key, data in solution_data.items():
                if file_key in str(filename):
                    return mock_open(read_data=data).return_value
            return mock_open().return_value
        
        with patch('builtins.open', side_effect=mock_open_side_effect):
            from main import load_ground_truth_calibration
            
            result = load_ground_truth_calibration()
            
            # Verify matrix constructed from individual coefficients
            self.assertEqual(result.shape, (3, 3))
            expected_matrix = np.array([
                [0.85, 0.1, 0.08],   # Red pigment (0.85 from file)
                [0.15, 0.72, 0.1],   # Yellow pigment (0.72 from file)
                [0.12, 0.15, 0.78]   # Blue pigment (0.78 from file)
            ])
            np.testing.assert_array_equal(result, expected_matrix)
            
            # Verify logging
            mock_logger.info.assert_any_call("🔧 Constructed ground truth matrix from individual files")
    
    @patch('frontend.main.Path')
    @patch('frontend.main.logger')
    def test_missing_calibration_files_fallback(self, mock_logger, mock_path):
        """Test fallback to random matrix when all files are missing."""
        # Mock Path behavior - no files exist
        mock_path.return_value.parent = self.ground_truth_dir.parent
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_path.return_value.parent.__truediv__.return_value = mock_file
        
        with patch('numpy.random.seed') as mock_seed, \
             patch('numpy.random.normal') as mock_normal:
            
            # Mock the random fallback generation
            mock_normal.return_value = np.array([
                [0.3, 0.25, 0.35],
                [0.28, 0.32, 0.27],
                [0.33, 0.29, 0.31]
            ])
            
            from frontend.main import load_ground_truth_calibration
            
            result = load_ground_truth_calibration()
            
            # Verify fallback behavior
            self.assertEqual(result.shape, (3, 3))
            mock_seed.assert_called_once_with(42)
            mock_normal.assert_called_once()
            
            # Verify logging
            mock_logger.info.assert_any_call("🎲 Using random fallback matrix")
    
    @patch('frontend.main.Path')
    @patch('frontend.main.logger')
    def test_malformed_summary_file(self, mock_logger, mock_path):
        """Test handling of malformed calibration summary file."""
        # Mock Path behavior
        mock_path.return_value.parent = self.ground_truth_dir.parent
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value = mock_file_path
        
        # Create malformed JSON
        malformed_data = '{"calibration_summary": {"invalid": "data"'  # Missing closing brace
        
        with patch('builtins.open', mock_open(read_data=malformed_data)):
            from frontend.main import load_ground_truth_calibration
            
            result = load_ground_truth_calibration()
            
            # Should fallback to random matrix
            self.assertEqual(result.shape, (3, 3))
            mock_logger.warning.assert_any_call("⚠️  Error loading ground truth calibration: %s", unittest.mock.ANY)
    
    @patch('frontend.main.Path')
    @patch('frontend.main.logger')
    def test_missing_matrix_in_summary(self, mock_logger, mock_path):
        """Test handling when calibration matrix is missing from summary."""
        # Mock Path behavior
        mock_path.return_value.parent = self.ground_truth_dir.parent
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value = mock_file_path
        
        # Summary without calibration matrix
        summary_without_matrix = {
            "calibration_summary": {
                "timestamp": "2025-07-30T14:36:00.123456",
                "total_solutions": 3
                # Missing calibration_matrix
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(summary_without_matrix))):
            # Mock individual solution files don't exist
            solution_mock = MagicMock()
            solution_mock.exists.return_value = False
            
            def path_side_effect(subpath):
                if "calibration_summary.json" in str(subpath):
                    return mock_file_path
                return solution_mock
            
            mock_path.return_value.parent.__truediv__.side_effect = path_side_effect
            
            from frontend.main import load_ground_truth_calibration
            
            result = load_ground_truth_calibration()
            
            # Should fallback to random matrix
            self.assertEqual(result.shape, (3, 3))
    
    @patch('frontend.main.Path')
    @patch('frontend.main.logger')
    def test_partial_solution_files(self, mock_logger, mock_path):
        """Test handling when only some solution files exist."""
        # Mock Path behavior
        mock_path.return_value.parent = self.ground_truth_dir.parent
        
        summary_mock = MagicMock()
        summary_mock.exists.return_value = False
        
        # Only red and yellow files exist, blue is missing
        solution_mocks = {
            "red": MagicMock(),
            "yellow": MagicMock(),
            "blue": MagicMock()
        }
        solution_mocks["red"].exists.return_value = True
        solution_mocks["yellow"].exists.return_value = True
        solution_mocks["blue"].exists.return_value = False  # Missing blue
        
        def path_side_effect(subpath):
            if "calibration_summary.json" in str(subpath):
                return summary_mock
            for color in ["red", "yellow", "blue"]:
                if f"{color}_solution_ground_truth.json" in str(subpath):
                    return solution_mocks[color]
            return MagicMock()
        
        mock_path.return_value.parent.__truediv__.side_effect = path_side_effect
        
        # Mock file reading for available solutions
        solution_data = {
            "red": json.dumps(self.valid_red_solution),
            "yellow": json.dumps(self.valid_yellow_solution)
        }
        
        def mock_open_side_effect(filename, mode='r'):
            for color, data in solution_data.items():
                if f"{color}_solution_ground_truth.json" in str(filename):
                    return mock_open(read_data=data).return_value
            return mock_open().return_value
        
        with patch('builtins.open', side_effect=mock_open_side_effect):
            from frontend.main import load_ground_truth_calibration
            
            result = load_ground_truth_calibration()
            
            # Should still construct matrix with fallback values for missing blue
            self.assertEqual(result.shape, (3, 3))
            expected_matrix = np.array([
                [0.85, 0.1, 0.08],   # Red from file
                [0.15, 0.72, 0.1],   # Yellow from file
                [0.12, 0.15, 0.5]    # Blue fallback value
            ])
            np.testing.assert_array_equal(result, expected_matrix)
            
            # Verify warning for missing file
            mock_logger.warning.assert_any_call("⚠️  Missing ground truth file: %s", unittest.mock.ANY)
    
    def test_bottle_model_initialization(self):
        """Test BottleModel initialization with ground truth data."""
        # Mock the calibration loading
        test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78]
        ])
        
        with patch('frontend.main.load_ground_truth_calibration', return_value=test_matrix):
            from frontend.main import BottleModel
            
            # Create bottle model instance
            bottle_model = BottleModel(test_matrix)
            
            # Verify initialization
            self.assertIsNotNone(bottle_model.P_est)
            np.testing.assert_array_equal(bottle_model.P_est, test_matrix)
            
            # Verify it's a copy (not reference)
            original_value = test_matrix[0, 0]
            bottle_model.P_est[0, 0] = 999
            self.assertEqual(test_matrix[0, 0], original_value)  # Original unchanged


class TestColorOptimizationIntegration(unittest.TestCase):
    """Test integration of ground truth calibration with color optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78]
        ])
    
    @patch('frontend.main.load_ground_truth_calibration')
    def test_target_color_generation_with_ground_truth(self, mock_load_calibration):
        """Test target color generation uses ground truth matrix."""
        mock_load_calibration.return_value = self.test_matrix
        
        # Import after patching
        from frontend.main import generate_random_target_color, bottle_model
        
        # Generate multiple target colors
        colors = [generate_random_target_color() for _ in range(10)]
        
        # Verify all colors are valid RGB tuples
        for color in colors:
            self.assertIsInstance(color, tuple)
            self.assertEqual(len(color), 3)
            for component in color:
                self.assertIsInstance(component, (int, np.integer))
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
    
    @patch('frontend.main.load_ground_truth_calibration')
    def test_reachable_rgb_sampling(self, mock_load_calibration):
        """Test _sample_reachable_rgb function with ground truth matrix."""
        mock_load_calibration.return_value = self.test_matrix
        
        from frontend.main import _sample_reachable_rgb
        
        # Sample multiple colors
        for _ in range(20):
            rgb, weights = _sample_reachable_rgb(self.test_matrix)
            
            # Verify RGB values
            self.assertIsInstance(rgb, tuple)
            self.assertEqual(len(rgb), 3)
            for component in rgb:
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
            
            # Verify weights
            self.assertIsInstance(weights, np.ndarray)
            self.assertEqual(len(weights), 3)
            self.assertGreater(weights.sum(), 0)  # Should have some positive weights


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end tests for the complete ground truth calibration system."""
    
    def setUp(self):
        """Set up temporary directory with real calibration files."""
        self.temp_dir = tempfile.mkdtemp()
        self.ground_truth_dir = Path(self.temp_dir) / "ground_truth_calibration"
        self.ground_truth_dir.mkdir()
        
        # Create realistic calibration files
        self.create_realistic_calibration_files()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def create_realistic_calibration_files(self):
        """Create realistic calibration files for testing."""
        # Calibration summary
        summary_data = {
            "calibration_summary": {
                "timestamp": "2025-07-30T14:36:00.123456",
                "total_solutions": 3,
                "calibration_session_id": "test_session_001",
                "calibration_matrix": {
                    "description": "Test calibration matrix",
                    "matrix": [
                        [0.85, 0.12, 0.08],
                        [0.15, 0.72, 0.11],
                        [0.18, 0.16, 0.78]
                    ],
                    "units": "absorbance per unit volume",
                    "condition_number": 5.23,
                    "determinant": 0.412
                }
            }
        }
        
        with open(self.ground_truth_dir / "calibration_summary.json", 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        # Individual solution files
        solutions = {
            "red": {
                "calibration_parameters": {
                    "absorbance_coefficient": 0.85,
                    "concentration": "10mg/mL",
                    "volume_dispensed": "5.0mL"
                },
                "color_measurement": {
                    "rgb": [220, 85, 45],
                    "hex": "#dc552d",
                    "lab": [42.3, 51.2, 35.8]
                }
            },
            "yellow": {
                "calibration_parameters": {
                    "absorbance_coefficient": 0.72,
                    "concentration": "8mg/mL",
                    "volume_dispensed": "4.5mL"
                },
                "color_measurement": {
                    "rgb": [245, 235, 65],
                    "hex": "#f5eb41",
                    "lab": [88.1, -15.6, 82.4]
                }
            },
            "blue": {
                "calibration_parameters": {
                    "absorbance_coefficient": 0.78,
                    "concentration": "12mg/mL",
                    "volume_dispensed": "6.0mL"
                },
                "color_measurement": {
                    "rgb": [95, 155, 185],
                    "hex": "#5f9bb9",
                    "lab": [62.8, -12.3, -25.7]
                }
            }
        }
        
        for color, data in solutions.items():
            with open(self.ground_truth_dir / f"{color}_solution_ground_truth.json", 'w') as f:
                json.dump(data, f, indent=2)
    
    @patch('frontend.main.Path')
    def test_complete_calibration_workflow(self, mock_path):
        """Test the complete calibration loading workflow with real files."""
        # Mock Path to point to our temp directory
        mock_path.return_value.parent = self.temp_dir
        
        from frontend.main import load_ground_truth_calibration, BottleModel
        
        # Load calibration data
        matrix = load_ground_truth_calibration()
        
        # Verify matrix properties
        self.assertEqual(matrix.shape, (3, 3))
        expected_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78]
        ])
        np.testing.assert_array_equal(matrix, expected_matrix)
        
        # Test BottleModel creation
        bottle_model = BottleModel(matrix)
        self.assertIsNotNone(bottle_model.P_est)
        np.testing.assert_array_equal(bottle_model.P_est, matrix)
        
        # Test that bottle_model inherits from ColorOptimizer
        from frontend.main import ColorOptimizer
        self.assertIsInstance(bottle_model, ColorOptimizer)


if __name__ == '__main__':
    # Create a test suite with all test cases
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestGroundTruthCalibration,
        TestColorOptimizationIntegration,
        TestEndToEndIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY:")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            failure_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"- {test}: {failure_msg}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"- {test}: {error_msg}")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
