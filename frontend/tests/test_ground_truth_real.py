#!/usr/bin/env python3
"""
Simplified test suite for ground truth calibration integration using real files.
"""

import unittest
import numpy as np
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

class TestGroundTruthCalibrationReal(unittest.TestCase):
    """Test ground truth calibration loading functionality with real files."""
    
    def test_load_ground_truth_calibration_real_files(self):
        """Test loading from actual ground truth calibration files."""
        # Test with default settings (white locked to zero)
        result = load_ground_truth_calibration(allow_white_absorbance=False)
        
        # Verify the result is a valid 4x3 matrix
        self.assertEqual(result.shape, (4, 3))
        self.assertIsInstance(result, np.ndarray)
        
        # Check that white row (row 3) is zero when locked
        np.testing.assert_array_equal(result[3, :], [0.0, 0.0, 0.0])
        
        # Verify all values are non-negative (absorbance values)
        self.assertTrue(np.all(result >= 0))
        
        print(f"✅ Loaded ground truth matrix shape: {result.shape}")
        print(f"✅ Matrix:\n{result}")

    def test_load_ground_truth_calibration_with_white(self):
        """Test loading ground truth calibration with white absorbance allowed."""
        result = load_ground_truth_calibration(allow_white_absorbance=True)
        
        # Verify the result is a valid 4x3 matrix
        self.assertEqual(result.shape, (4, 3))
        self.assertIsInstance(result, np.ndarray)
        
        # Verify all values are non-negative
        self.assertTrue(np.all(result >= 0))
        
        print(f"✅ Loaded ground truth matrix with white learning: {result.shape}")

    def test_bottle_model_initialization_real(self):
        """Test BottleModel initialization with real ground truth data."""
        # Load real calibration matrix
        test_matrix = load_ground_truth_calibration()
        
        # Create bottle model
        bottle = BottleModel(test_matrix)
        
        # Verify the matrix is stored correctly
        np.testing.assert_array_equal(bottle.P_est, test_matrix)
        
        # Verify it inherits from ColorOptimizer
        self.assertIsInstance(bottle, ColorOptimizer)
        
        print(f"✅ BottleModel initialized with matrix shape: {bottle.P_est.shape}")

    def test_target_color_generation_real(self):
        """Test target color generation with real ground truth data."""
        # Generate several target colors
        for i in range(5):
            rgb = generate_random_target_color()
            
            # Verify format
            self.assertIsInstance(rgb, tuple)
            self.assertEqual(len(rgb), 3)
            
            # Verify RGB values are valid
            for component in rgb:
                self.assertIsInstance(component, int)
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
            
            print(f"✅ Generated target {i+1}: RGB{rgb}")

    def test_reachable_rgb_sampling_real(self):
        """Test _sample_reachable_rgb with real ground truth matrix."""
        # Load real calibration matrix
        test_matrix = load_ground_truth_calibration()
        
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
        
        print(f"✅ Sampled RGB: {rgb}, weights sum: {np.sum(weights):.2f}")

    def test_color_optimizer_with_real_data(self):
        """Test ColorOptimizer works with real ground truth calibration."""
        # Load real calibration matrix
        test_matrix = load_ground_truth_calibration()
        
        # Create optimizer and set its matrix
        optimizer = ColorOptimizer()
        optimizer.P_est = test_matrix
        
        # Test basic functionality
        test_color = (200, 150, 100)
        optimizer.set_target_color(test_color)
        
        self.assertEqual(optimizer.target_color, test_color)
        self.assertIsNotNone(optimizer.hue_target_deg)
        
        # Test recommendation generation
        ratios = optimizer.recommend_next_ratios()
        self.assertIsInstance(ratios, dict)
        self.assertIn('red', ratios)
        self.assertIn('yellow', ratios)
        self.assertIn('blue', ratios)
        self.assertIn('white', ratios)
        
        # Verify ratios are valid
        for pigment, ratio in ratios.items():
            self.assertIsInstance(ratio, (int, float))
            self.assertGreaterEqual(ratio, 0)
        
        # Check that ratios sum to approximately 3.0
        total = sum(ratios.values())
        self.assertAlmostEqual(total, 3.0, places=1)
        
        print(f"✅ Optimizer ratios: {ratios}")
        print(f"✅ Total volume: {total:.2f}")

    def test_bottle_model_global_instance(self):
        """Test that the global bottle_model instance is properly initialized."""
        # Check that bottle_model exists and is properly initialized
        self.assertIsNotNone(bottle_model)
        self.assertIsInstance(bottle_model, BottleModel)
        self.assertIsNotNone(bottle_model.P_est)
        self.assertEqual(bottle_model.P_est.shape, (4, 3))
        
        print(f"✅ Global bottle_model matrix shape: {bottle_model.P_est.shape}")
        print(f"✅ Global bottle_model matrix:\n{bottle_model.P_est}")

    def test_four_rule_integration(self):
        """Test that the four-rule target generation works with real data."""
        # Clear any existing history
        main._hue_history.clear()
        main._cum_vol[:] = 0
        
        # Generate several targets to test the four rules
        targets = []
        for i in range(10):
            rgb = generate_random_target_color()
            targets.append(rgb)
            hue = ColorOptimizer._hue_deg(rgb)
            
            # Verify primary exclusion (rule 4)
            min_primary_distance = min(main._hue_gap_deg(hue, p) for p in main.PRIMARY_HUES)
            self.assertGreaterEqual(min_primary_distance, main.HUE_EXCLUSION, 
                                  f"Target {rgb} hue {hue:.1f}° too close to primary (distance: {min_primary_distance:.1f}°)")
        
        print(f"✅ Generated {len(targets)} targets with proper primary exclusion")
        print(f"✅ Hue history length: {len(main._hue_history)}")
        print(f"✅ Cumulative volumes: {main._cum_vol}")


if __name__ == '__main__':
    unittest.main()
