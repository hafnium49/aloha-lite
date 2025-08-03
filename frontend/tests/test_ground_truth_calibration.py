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

# Import all needed functions and classes from main
import main
from main import (
    load_ground_truth_calibration, 
    BottleModel, 
    ColorOptimizer, 
    generate_random_target_color, 
    _sample_reachable_rgb,
    bottle_model
)

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
        self.red_solution_data = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.85,
                "measurement_date": "2025-07-30T14:30:00.123456"
            },
            "color_measurement": {
                "rgb": [220, 85, 45],
                "measurement_conditions": "Standard lighting"
            }
        }
        
        self.yellow_solution_data = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.72,
                "measurement_date": "2025-07-30T14:31:00.123456"
            },
            "color_measurement": {
                "rgb": [245, 235, 65],
                "measurement_conditions": "Standard lighting"
            }
        }
        
        self.blue_solution_data = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.78,
                "measurement_date": "2025-07-30T14:32:00.123456"
            },
            "color_measurement": {
                "rgb": [95, 155, 185],
                "measurement_conditions": "Standard lighting"
            }
        }
        
        self.white_solution_data = {
            "calibration_parameters": {
                "absorbance_coefficient": 0.02,
                "measurement_date": "2025-07-30T14:33:00.123456"
            },
            "color_measurement": {
                "rgb": [255, 255, 255],
                "measurement_conditions": "Standard lighting"
            }
        }
        
        # RGB-only summary data for testing RGB fallback
        self.rgb_summary_data = {
            "calibration_summary": {
                "timestamp": "2025-07-30T14:36:00.123456",
                "total_solutions": 3,
                "solutions": {
                    "red": {
                        "rgb": [220, 85, 45],
                        "measurement_date": "2025-07-30T14:30:00"
                    },
                    "yellow": {
                        "rgb": [245, 235, 65],
                        "measurement_date": "2025-07-30T14:31:00"
                    },
                    "blue": {
                        "rgb": [95, 155, 185],
                        "measurement_date": "2025-07-30T14:32:00"
                    }
                }
            }
        }
        
        # Malformed data for error testing
        self.malformed_summary_data = {
            "invalid_key": "This is not a valid calibration summary"
        }
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @patch('main.Path')
    def test_load_from_calibration_summary_success(self, mock_path_class):
        """Test successful loading from calibration summary file."""
        # Create a mock path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        # Mock the parent directory and file operations
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Mock the calibration summary file
        mock_summary_file = MagicMock()
        mock_summary_file.exists.return_value = True
        mock_parent.__truediv__.return_value = mock_summary_file
        
        with patch('builtins.open', mock_open(read_data=json.dumps(self.valid_summary_data))):
            result = load_ground_truth_calibration()
            
            # Verify the matrix shape and content
            self.assertEqual(result.shape, (4, 3))
            expected_matrix = np.array([
                [0.85, 0.12, 0.08],
                [0.15, 0.72, 0.11],
                [0.18, 0.16, 0.78],
                [0.00, 0.00, 0.00]
            ])
            np.testing.assert_array_almost_equal(result, expected_matrix)

    def test_load_from_individual_files_fallback(self):
        """Test fallback to individual solution files when summary is missing."""
        # Create actual temporary files for this test
        temp_dir = tempfile.mkdtemp()
        try:
            ground_truth_dir = Path(temp_dir) / "ground_truth_calibration"
            ground_truth_dir.mkdir()
            
            # Create individual solution files (no summary file)
            red_file = ground_truth_dir / "red_solution_ground_truth.json"
            yellow_file = ground_truth_dir / "yellow_solution_ground_truth.json"
            blue_file = ground_truth_dir / "blue_solution_ground_truth.json"
            white_file = ground_truth_dir / "white_solution_ground_truth.json"
            
            with open(red_file, 'w') as f:
                json.dump(self.red_solution_data, f)
            with open(yellow_file, 'w') as f:
                json.dump(self.yellow_solution_data, f)
            with open(blue_file, 'w') as f:
                json.dump(self.blue_solution_data, f)
            with open(white_file, 'w') as f:
                json.dump(self.white_solution_data, f)
            
            # Mock the ground truth directory path
            with patch('main.Path') as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.parent = ground_truth_dir.parent
                mock_path_class.return_value = mock_path_instance
                
                result = load_ground_truth_calibration()
                
                # Verify the result is a valid 4x3 matrix
                self.assertEqual(result.shape, (4, 3))
                
                # Check that the function constructed a matrix using the absorbance coefficients
                # The actual construction uses:
                # P_true = np.array([
                #     [red_coeff, 0.1, 0.08],
                #     [0.15, yellow_coeff, 0.1],
                #     [0.12, 0.15, blue_coeff],
                #     [white_absorbance, white_absorbance, white_absorbance]
                # ])
                self.assertAlmostEqual(result[0, 0], 0.85, places=2)  # red coefficient in position [0,0]
                self.assertAlmostEqual(result[1, 1], 0.72, places=2)  # yellow coefficient in position [1,1]
                self.assertAlmostEqual(result[2, 2], 0.78, places=2)  # blue coefficient in position [2,2]
                self.assertEqual(result[3, 0], 0.0)  # white locked to zero by default
                
                # Check some of the hardcoded off-diagonal elements
                self.assertAlmostEqual(result[0, 1], 0.1, places=2)   # hardcoded cross-term
                self.assertAlmostEqual(result[0, 2], 0.08, places=2)  # hardcoded cross-term
                
        finally:
            shutil.rmtree(temp_dir)

    @patch('main.Path')
    @patch('main.logger')
    def test_missing_calibration_files_fallback(self, mock_logger, mock_path_class):
        """Test fallback to random matrix when all files are missing."""
        # Create a mock path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        # Mock the parent directory and file operations
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Mock that no files exist
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_parent.__truediv__.return_value = mock_file
        
        with patch('numpy.random.seed') as mock_seed, \
             patch('numpy.random.normal') as mock_normal:
            
            # Mock the random fallback generation (for 3x3 base)
            mock_normal.return_value = np.array([
                [0.3, 0.25, 0.35],
                [0.28, 0.32, 0.27],
                [0.33, 0.29, 0.31]
            ])
            
            result = load_ground_truth_calibration()
            
            # Verify fallback behavior - should be 4x3 with white row added
            self.assertEqual(result.shape, (4, 3))
            mock_seed.assert_called_once_with(42)
            
            # Check that white row is zero (locked by default)
            np.testing.assert_array_equal(result[3, :], [0.0, 0.0, 0.0])
            
            # Verify logging
            mock_logger.info.assert_any_call("🎲 Using random fallback matrix (4x3 with white locked to zero)")

    @patch('main.Path')
    @patch('main.logger')
    def test_malformed_summary_file(self, mock_logger, mock_path_class):
        """Test handling of malformed calibration summary file."""
        # Create a mock path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        # Mock the parent directory and file operations
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Mock that the summary file exists
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_parent.__truediv__.return_value = mock_file_path
        
        with patch('builtins.open', mock_open(read_data=json.dumps(self.malformed_summary_data))):
            with patch('numpy.random.seed') as mock_seed, \
                 patch('numpy.random.normal') as mock_normal:
                
                # Mock the random fallback generation
                mock_normal.return_value = np.array([
                    [0.3, 0.25, 0.35],
                    [0.28, 0.32, 0.27],
                    [0.33, 0.29, 0.31]
                ])
                
                result = load_ground_truth_calibration()
                
                # Should fall back to random matrix
                self.assertEqual(result.shape, (4, 3))
                mock_seed.assert_called_once_with(42)

    @patch('main.Path')
    @patch('main.logger')
    def test_missing_matrix_in_summary(self, mock_logger, mock_path_class):
        """Test handling when calibration matrix is missing from summary."""
        # Summary data without calibration matrix
        summary_without_matrix = {
            "calibration_summary": {
                "timestamp": "2025-07-30T14:36:00.123456",
                "total_solutions": 3,
                "note": "Matrix data not available"
            }
        }
        
        # Create a mock path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        # Mock the parent directory and file operations
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Mock that the summary file exists
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_parent.__truediv__.return_value = mock_file_path
        
        with patch('builtins.open', mock_open(read_data=json.dumps(summary_without_matrix))):
            with patch('numpy.random.seed') as mock_seed, \
                 patch('numpy.random.normal') as mock_normal:
                
                # Mock the random fallback generation
                mock_normal.return_value = np.array([
                    [0.3, 0.25, 0.35],
                    [0.28, 0.32, 0.27],
                    [0.33, 0.29, 0.31]
                ])
                
                result = load_ground_truth_calibration()
                
                # Should fall back to random matrix
                self.assertEqual(result.shape, (4, 3))
                mock_seed.assert_called_once_with(42)

    @patch('main.Path')
    def test_partial_solution_files(self, mock_path_class):
        """Test handling when only some solution files exist."""
        # Create a mock path instance
        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        
        # Mock the parent directory
        mock_parent = MagicMock()
        mock_path_instance.parent = mock_parent
        
        # Mock file existence behavior - only red and yellow files exist
        def mock_truediv_side_effect(filename):
            mock_file = MagicMock()
            if "red_solution" in str(filename) or "yellow_solution" in str(filename):
                mock_file.exists.return_value = True
            else:
                mock_file.exists.return_value = False
            return mock_file
        
        mock_parent.__truediv__.side_effect = mock_truediv_side_effect
        
        # Mock file contents for available files
        file_contents = {
            "red_solution_ground_truth.json": json.dumps(self.red_solution_data),
            "yellow_solution_ground_truth.json": json.dumps(self.yellow_solution_data)
        }
        
        def open_side_effect(filename, mode='r'):
            for file_key, content in file_contents.items():
                if file_key in str(filename):
                    return mock_open(read_data=content).return_value
            return mock_open(read_data="{}").return_value
        
        with patch('builtins.open', side_effect=open_side_effect):
            with patch('numpy.random.seed') as mock_seed, \
                 patch('numpy.random.normal') as mock_normal:
                
                # Mock the random fallback generation
                mock_normal.return_value = np.array([
                    [0.3, 0.25, 0.35],
                    [0.28, 0.32, 0.27],
                    [0.33, 0.29, 0.31]
                ])
                
                result = load_ground_truth_calibration()
                
                # Should fall back to random matrix since not all colored solutions are available
                self.assertEqual(result.shape, (4, 3))
                mock_seed.assert_called_once_with(42)

    @patch('main.load_ground_truth_calibration', return_value=np.array([[0.85, 0.12, 0.08], [0.15, 0.72, 0.11], [0.18, 0.16, 0.78], [0.00, 0.00, 0.00]]))
    def test_bottle_model_initialization(self, mock_load):
        """Test BottleModel initialization with ground truth data."""
        test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78],
            [0.00, 0.00, 0.00]
        ])
        
        bottle = BottleModel(test_matrix)
        
        # Verify the matrix is stored correctly
        np.testing.assert_array_equal(bottle.P_est, test_matrix)
        
        # Verify it inherits from ColorOptimizer
        self.assertIsInstance(bottle, ColorOptimizer)


class TestColorOptimizationIntegration(unittest.TestCase):
    """Test integration of ground truth calibration with color optimization."""
    
    @patch('main.load_ground_truth_calibration')
    def test_target_color_generation_with_ground_truth(self, mock_load):
        """Test target color generation uses ground truth matrix."""
        # Mock ground truth matrix
        test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78],
            [0.00, 0.00, 0.00]
        ])
        mock_load.return_value = test_matrix
        
        # Generate some target colors
        for _ in range(5):
            rgb = generate_random_target_color()
            self.assertIsInstance(rgb, tuple)
            self.assertEqual(len(rgb), 3)
            for component in rgb:
                self.assertIsInstance(component, int)
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)

    @patch('main.load_ground_truth_calibration')
    def test_reachable_rgb_sampling(self, mock_load):
        """Test _sample_reachable_rgb function with ground truth matrix."""
        # Mock ground truth matrix
        test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78],
            [0.00, 0.00, 0.00]
        ])
        mock_load.return_value = test_matrix
        
        # Test reachable RGB sampling
        rgb, weights = _sample_reachable_rgb(test_matrix)
        
        # Verify output format
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        self.assertIsInstance(weights, np.ndarray)
        self.assertEqual(len(weights), 4)  # 4 pigments including white
        
        # Verify RGB values are valid
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)
        
        # Verify weights sum to approximately 3.0 (max_total)
        self.assertAlmostEqual(np.sum(weights), 3.0, places=1)
        
        # Verify all weights are non-negative
        self.assertTrue(np.all(weights >= 0))


class TestEndToEndIntegration(unittest.TestCase):
    """Test end-to-end integration with real file loading."""
    
    @patch('main.Path')
    def test_complete_calibration_workflow(self, mock_path_class):
        """Test the complete calibration loading workflow with real files."""
        # Create a temporary directory structure
        temp_dir = tempfile.mkdtemp()
        try:
            ground_truth_dir = Path(temp_dir) / "ground_truth_calibration"
            ground_truth_dir.mkdir()
            
            # Create a valid calibration summary file
            summary_data = {
                "calibration_summary": {
                    "timestamp": "2025-07-30T14:36:00.123456",
                    "total_solutions": 3,
                    "calibration_matrix": {
                        "description": "Derived 4x3 absorbance matrix",
                        "matrix": [
                            [0.85, 0.12, 0.08],
                            [0.15, 0.72, 0.11],
                            [0.18, 0.16, 0.78],
                            [0.00, 0.00, 0.00]
                        ],
                        "units": "absorbance per unit volume"
                    }
                }
            }
            
            summary_file = ground_truth_dir / "calibration_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f)
            
            # Create a mock path instance
            mock_path_instance = MagicMock()
            mock_path_class.return_value = mock_path_instance
            
            # Mock the parent directory and file operations
            mock_parent = MagicMock()
            mock_path_instance.parent = mock_parent
            
            # Mock that the summary file exists
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = True
            mock_parent.__truediv__.return_value = mock_file_path
            
            with patch('builtins.open', mock_open(read_data=json.dumps(summary_data))):
                result = load_ground_truth_calibration()
                bottle = BottleModel(result)
                
                # Verify everything works together
                self.assertEqual(result.shape, (4, 3))
                self.assertIsInstance(bottle, BottleModel)
                self.assertIsInstance(bottle, ColorOptimizer)
                np.testing.assert_array_equal(bottle.P_est, result)
                
        finally:
            shutil.rmtree(temp_dir)

    def test_color_optimizer_integration(self):
        """Test ColorOptimizer works with ground truth calibration."""
        # Create a test matrix
        test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78],
            [0.00, 0.00, 0.00]
        ])
        
        optimizer = ColorOptimizer()
        optimizer.P_est = test_matrix
        
        # Test basic functionality
        optimizer.set_target_color((200, 150, 100))
        self.assertIsNotNone(optimizer.target_color)
        self.assertIsNotNone(optimizer.hue_target_deg)
        
        # Test recommendation generation
        ratios = optimizer.recommend_next_ratios()
        self.assertIsInstance(ratios, dict)
        self.assertIn('red', ratios)
        self.assertIn('yellow', ratios)
        self.assertIn('blue', ratios)
        self.assertIn('white', ratios)


if __name__ == '__main__':
    unittest.main()
