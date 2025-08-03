#!/usr/bin/env python3
"""
Test script to verify the 4-pigment ColorOptimizer system with white background support.

Tests:
1. 4-pigment matrix dimensions
2. White pigment normalization
3. Ground truth calibration with white pigment
4. Color optimization with white solvent
"""

import sys
import os
import numpy as np
import unittest

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import ColorOptimizer, BottleModel, generate_random_target_color, _sample_reachable_rgb, load_ground_truth_calibration

class Test4PigmentSystem(unittest.TestCase):
    """Test the 4-pigment system implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ColorOptimizer()
        self.target_color = (200, 150, 100)  # Test target
        self.optimizer.set_target_color(self.target_color)
    
    def test_optimizer_initialization(self):
        """Test that ColorOptimizer initializes correctly for 4-pigment system."""
        print("🧪 Testing ColorOptimizer initialization...")
        
        # Test _ratios_to_array with 4 pigments
        test_ratios = {'red': 1.0, 'yellow': 2.0, 'blue': 3.0, 'white': 0.5}
        array = self.optimizer._ratios_to_array(test_ratios)
        
        self.assertEqual(len(array), 4)
        np.testing.assert_array_equal(array, [1.0, 2.0, 3.0, 0.5])
        print("✅ _ratios_to_array works correctly with 4 pigments")
        
        # Test _array_to_ratios
        back_to_dict = self.optimizer._array_to_ratios(array)
        expected = {'red': 1.0, 'yellow': 2.0, 'blue': 3.0, 'white': 0.5}
        self.assertEqual(back_to_dict, expected)
        print("✅ _array_to_ratios works correctly with 4 pigments")
    
    def test_normalization_with_white(self):
        """Test the normalization logic with white solvent."""
        print("\n🧪 Testing normalization with white pigment...")
        
        # Test case 1: Normal case
        test_ratios = {'red': 1.0, 'yellow': 1.0, 'blue': 1.0}
        normalized = self.optimizer._normalize(test_ratios, max_total=3.0)
        
        # Should have 4 keys including white
        self.assertEqual(len(normalized), 4)
        self.assertIn('white', normalized)
        
        # Total should be max_total
        total = sum(normalized.values())
        self.assertAlmostEqual(total, 3.0, places=2)
        
        # White should be non-negative
        self.assertGreaterEqual(normalized['white'], 0.0)
        print(f"✅ Normal case: {normalized}")
        
        # Test case 2: Large ratios (should scale down colored pigments)
        test_ratios = {'red': 5.0, 'yellow': 5.0, 'blue': 5.0}
        normalized = self.optimizer._normalize(test_ratios, max_total=3.0)
        
        total = sum(normalized.values())
        self.assertAlmostEqual(total, 3.0, places=2)
        self.assertGreaterEqual(normalized['white'], 0.1)  # Minimum white volume
        print(f"✅ Large ratios case: {normalized}")
        
        # Test case 3: Ensure minimum white volume
        test_ratios = {'red': 2.9, 'yellow': 0.05, 'blue': 0.05}  # Almost max_total in colored
        normalized = self.optimizer._normalize(test_ratios, max_total=3.0)
        
        self.assertGreaterEqual(normalized['white'], 0.1)  # Should enforce minimum
        print(f"✅ Minimum white volume enforced: {normalized}")
    
    def test_ground_truth_matrix_shape(self):
        """Test that ground truth calibration returns 4x3 matrix."""
        print("\n🧪 Testing ground truth matrix shape...")
        
        # Load ground truth calibration
        matrix = load_ground_truth_calibration()
        
        # Should be 4x3 (4 pigments, 3 RGB channels)
        self.assertEqual(matrix.shape, (4, 3))
        print(f"✅ Ground truth matrix shape: {matrix.shape}")
        
        # White row (index 3) should have low absorbance
        white_row = matrix[3, :]
        max_white_absorbance = np.max(np.abs(white_row))
        self.assertLessEqual(max_white_absorbance, 0.1)
        print(f"✅ White pigment max absorbance: {max_white_absorbance:.4f}")
    
    def test_sample_reachable_rgb(self):
        """Test _sample_reachable_rgb with 4-pigment system."""
        print("\n🧪 Testing _sample_reachable_rgb with 4 pigments...")
        
        # Create a test 4x3 matrix
        test_matrix = np.array([
            [0.5, 0.1, 0.1],  # Red
            [0.1, 0.5, 0.1],  # Yellow
            [0.1, 0.1, 0.5],  # Blue
            [0.0, 0.0, 0.0]   # White
        ])
        
        # Generate sample
        rgb, weights = _sample_reachable_rgb(test_matrix, max_total=3.0)
        
        # Check dimensions
        self.assertEqual(len(rgb), 3)  # RGB tuple
        self.assertEqual(len(weights), 4)  # 4 pigment weights
        
        # Check weight normalization
        total_weight = np.sum(weights)
        self.assertAlmostEqual(total_weight, 3.0, places=2)
        
        # Check RGB range
        for channel in rgb:
            self.assertGreaterEqual(channel, 0)
            self.assertLessEqual(channel, 255)
        
        print(f"✅ Sample RGB: {rgb}, Weights: {weights}")
        print(f"✅ Total weight: {total_weight:.2f}")
    
    def test_optimization_phases(self):
        """Test that optimization works through all phases with 4 pigments."""
        print("\n🧪 Testing optimization phases with 4-pigment system...")
        
        # Simulate multiple optimization steps
        for i in range(5):
            ratios = self.optimizer.recommend_next_ratios()
            
            # Should always have 4 keys
            self.assertEqual(len(ratios), 4)
            expected_keys = {'red', 'yellow', 'blue', 'white'}
            self.assertEqual(set(ratios.keys()), expected_keys)
            
            # All ratios should be positive
            for key, value in ratios.items():
                self.assertGreaterEqual(value, 0.0)
            
            # White should have minimum volume
            self.assertGreaterEqual(ratios['white'], 0.1)
            
            # Simulate measurement result
            simulated_rgb = self._simulate_measurement(ratios)
            self.optimizer.add_measurement(ratios, simulated_rgb)
            
            print(f"✅ Step {i+1}: {ratios}")
        
        # Check that calibration matrix is developed (should be 4x3)
        if hasattr(self.optimizer, 'P_est') and self.optimizer.P_est is not None:
            self.assertEqual(self.optimizer.P_est.shape, (4, 3))
            print(f"✅ Calibration matrix shape: {self.optimizer.P_est.shape}")
    
    def _simulate_measurement(self, ratios):
        """Simulate a color measurement result."""
        # Simple simulation - mix the ratios with some target bias
        red_contrib = ratios['red'] * 0.8
        yellow_contrib = ratios['yellow'] * 0.6  
        blue_contrib = ratios['blue'] * 0.7
        white_contrib = ratios['white'] * 0.1  # White adds brightness
        
        r = min(255, int(red_contrib * 100 + white_contrib * 50))
        g = min(255, int(yellow_contrib * 120 + white_contrib * 50))
        b = min(255, int(blue_contrib * 110 + white_contrib * 50))
        
        return (r, g, b)

def run_4_pigment_tests():
    """Run all 4-pigment system tests."""
    print("🚀 Running 4-Pigment System Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(Test4PigmentSystem)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All 4-pigment system tests passed!")
        return True
    else:
        print("❌ Some tests failed:")
        for failure in result.failures:
            print(f"  - {failure[0]}: {failure[1]}")
        for error in result.errors:
            print(f"  - {error[0]}: {error[1]}")
        return False

if __name__ == "__main__":
    run_4_pigment_tests()
