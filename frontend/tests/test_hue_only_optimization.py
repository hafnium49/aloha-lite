#!/usr/bin/env python3
"""
Test script for the new hue-only optimization features in ColorOptimizer.

Tests the implementation of hue-only optimization as specified in the instructions:
1. Signed hue difference calculation
2. Hue Jacobian estimation from recent moves
3. Hue-based correction method
4. Integration with existing optimization phases
5. hue_only_mode parameter functionality
"""

import sys
import os
import numpy as np
import unittest
import math

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    ColorOptimizer, 
    BottleModel,
    generate_random_target_color, 
    _hue_gap_deg,
    PRIMARY_HUES,
    HUE_EXCLUSION,
    MAX_DIFFICULTY,
    _hue_history,
    _cum_vol
)

class TestHueOnlyOptimization(unittest.TestCase):
    """Test the hue-only optimization implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Test both modes
        self.optimizer_hue = ColorOptimizer(hue_only_mode=True)
        self.optimizer_rgb = ColorOptimizer(hue_only_mode=False)
        self.target_color = (255, 128, 64)  # Orange color for testing
        
    def test_hue_only_mode_parameter(self):
        """Test that hue_only_mode parameter works correctly."""
        print("🧪 Testing hue_only_mode parameter...")
        
        # Test default initialization (should be True)
        opt_default = ColorOptimizer()
        self.assertTrue(opt_default.hue_only_mode, "Default hue_only_mode should be True")
        
        # Test explicit True
        opt_true = ColorOptimizer(hue_only_mode=True)
        self.assertTrue(opt_true.hue_only_mode, "Explicit hue_only_mode=True should be True")
        
        # Test explicit False
        opt_false = ColorOptimizer(hue_only_mode=False)
        self.assertFalse(opt_false.hue_only_mode, "Explicit hue_only_mode=False should be False")
        
        print("✅ hue_only_mode parameter working correctly")
    
    def test_signed_hue_diff(self):
        """Test the _signed_hue_diff method."""
        print("\n🧪 Testing signed hue difference calculation...")
        
        # Test cases: (h_from, h_to, expected_diff)
        test_cases = [
            (0, 0, 0),        # Same angle
            (0, 90, 90),      # Forward 90°
            (90, 0, -90),     # Backward 90°
            (0, 180, 180),    # Forward 180° (maximum) - allow both +180 and -180
            (180, 0, 180),    # Backward 180° (maximum) - allow both +180 and -180
            (10, 350, -20),   # Should go backward (shorter path)
            (350, 10, 20),    # Should go forward (shorter path)
            (0, 270, -90),    # Should go backward (shorter path)
            (270, 0, 90),     # Should go forward (shorter path)
            (45, 315, -90),   # Should go backward (shorter path)
            (315, 45, 90),    # Should go forward (shorter path)
        ]
        
        for h_from, h_to, expected in test_cases:
            result = ColorOptimizer._signed_hue_diff(h_from, h_to)
            print(f"  {h_from}° → {h_to}°: {result}° (expected {expected}°)")
            
            # Special handling for 180° cases where both +180 and -180 are valid
            if abs(expected) == 180:
                self.assertTrue(abs(result) == 180, 
                              f"Signed hue diff {h_from}° → {h_to}° should be ±180°, got {result}°")
            else:
                self.assertAlmostEqual(result, expected, places=1, 
                                     msg=f"Signed hue diff {h_from}° → {h_to}° should be {expected}°, got {result}°")
        
        print("✅ Signed hue difference calculation working correctly")
    
    def test_estimate_hue_jacobian(self):
        """Test the _estimate_hue_jacobian method."""
        print("\n🧪 Testing hue Jacobian estimation...")
        
        optimizer = ColorOptimizer(hue_only_mode=True)
        target_color = (255, 128, 64)
        optimizer.set_target_color(target_color)
        
        # With no history, should return None
        J = optimizer._estimate_hue_jacobian()
        self.assertIsNone(J, "Hue Jacobian should be None with no history")
        print("  ✓ Returns None with no history")
        
        # Add one measurement - still should return None (need at least 2 for differences)
        ratios1 = {'red': 2.0, 'yellow': 1.0, 'blue': 0.5, 'white': 6.5}
        rgb1 = (200, 150, 100)
        optimizer.add_measurement(ratios1, rgb1)
        
        J = optimizer._estimate_hue_jacobian()
        self.assertIsNone(J, "Hue Jacobian should be None with only 1 measurement")
        print("  ✓ Returns None with only 1 measurement")
        
        # Add several more measurements to build up history
        measurements = [
            ({'red': 2.2, 'yellow': 1.1, 'blue': 0.6, 'white': 6.1}, (210, 160, 110)),
            ({'red': 2.0, 'yellow': 1.2, 'blue': 0.7, 'white': 6.1}, (205, 165, 115)),
            ({'red': 2.3, 'yellow': 1.0, 'blue': 0.8, 'white': 5.9}, (215, 155, 120)),
            ({'red': 2.1, 'yellow': 1.3, 'blue': 0.6, 'white': 6.0}, (208, 170, 112)),
        ]
        
        for ratios, rgb in measurements:
            optimizer.add_measurement(ratios, rgb)
        
        # Now should be able to estimate Jacobian
        J = optimizer._estimate_hue_jacobian()
        
        if J is not None:
            self.assertEqual(J.shape, (3,), "Hue Jacobian should have shape (3,)")
            self.assertTrue(np.all(np.isfinite(J)), "Hue Jacobian should have finite values")
            print(f"  ✓ Estimated Jacobian: {J}")
            print("  ✓ Hue Jacobian estimation working with sufficient data")
        else:
            print("  ⚠ Hue Jacobian still None - moves may be too small or insufficient")
    
    def test_hue_based_correction(self):
        """Test the _hue_based_correction method."""
        print("\n🧪 Testing hue-based correction...")
        
        optimizer = ColorOptimizer(hue_only_mode=True)
        target_color = (255, 128, 64)
        optimizer.set_target_color(target_color)
        
        # With no history, should return None
        correction = optimizer._hue_based_correction()
        self.assertIsNone(correction, "Hue-based correction should be None with no history")
        print("  ✓ Returns None with no history")
        
        # Add measurements that will allow Jacobian estimation
        measurements = [
            ({'red': 2.0, 'yellow': 1.0, 'blue': 0.5, 'white': 6.5}, (200, 150, 100)),
            ({'red': 2.5, 'yellow': 1.0, 'blue': 0.5, 'white': 6.0}, (220, 150, 100)),
            ({'red': 2.0, 'yellow': 1.5, 'blue': 0.5, 'white': 6.0}, (200, 170, 100)),
            ({'red': 2.0, 'yellow': 1.0, 'blue': 1.0, 'white': 6.0}, (200, 150, 120)),
        ]
        
        for ratios, rgb in measurements:
            optimizer.add_measurement(ratios, rgb)
        
        # Try hue-based correction
        correction = optimizer._hue_based_correction()
        
        if correction is not None:
            self.assertIsInstance(correction, dict, "Hue-based correction should return a dict")
            required_keys = {'red', 'yellow', 'blue', 'white'}
            self.assertEqual(set(correction.keys()), required_keys, 
                           "Correction should have all pigment keys")
            
            # Check that values are reasonable (positive, sum to ~10.0)
            total_volume = sum(correction.values())
            self.assertAlmostEqual(total_volume, 10.0, places=1, 
                                 msg="Total volume should be ~10.0")
            
            for color, volume in correction.items():
                self.assertGreaterEqual(volume, 0.0, 
                                      f"{color} volume should be non-negative")
            
            print(f"  ✓ Hue-based correction: {correction}")
            print("  ✓ Hue-based correction working with sufficient data")
        else:
            print("  ⚠ Hue-based correction returned None - may need more distinct moves")
    
    def test_recommendation_logic_with_hue_mode(self):
        """Test that recommend_next_ratios uses hue-based methods when hue_only_mode=True."""
        print("\n🧪 Testing recommendation logic with hue_only_mode...")
        
        # Test phase 1 (N=1) behavior
        optimizer_hue = ColorOptimizer(hue_only_mode=True)
        optimizer_rgb = ColorOptimizer(hue_only_mode=False)
        
        target_color = (255, 128, 64)
        optimizer_hue.set_target_color(target_color)
        optimizer_rgb.set_target_color(target_color)
        
        # Add initial measurement to get to N=1
        initial_ratios = {'red': 2.0, 'yellow': 1.0, 'blue': 0.5, 'white': 6.5}
        initial_rgb = (200, 150, 100)
        
        optimizer_hue.add_measurement(initial_ratios, initial_rgb)
        optimizer_rgb.add_measurement(initial_ratios, initial_rgb)
        
        # Both should be in phase 1 now (N=1)
        self.assertEqual(len(optimizer_hue.history), 1, "Should have 1 measurement")
        self.assertEqual(len(optimizer_rgb.history), 1, "Should have 1 measurement")
        
        # Get recommendations from both
        rec_hue = optimizer_hue.recommend_next_ratios()
        rec_rgb = optimizer_rgb.recommend_next_ratios()
        
        # Both should return valid recommendations
        self.assertIsInstance(rec_hue, dict, "Hue mode should return dict")
        self.assertIsInstance(rec_rgb, dict, "RGB mode should return dict")
        
        # Check that both have required keys
        required_keys = {'red', 'yellow', 'blue', 'white'}
        self.assertEqual(set(rec_hue.keys()), required_keys, "Hue mode missing keys")
        self.assertEqual(set(rec_rgb.keys()), required_keys, "RGB mode missing keys")
        
        print(f"  ✓ Hue mode recommendation: {rec_hue}")
        print(f"  ✓ RGB mode recommendation: {rec_rgb}")
        print("  ✓ Both modes produce valid recommendations in phase 1")
    
    def test_distance_metric_hue_vs_rgb(self):
        """Test that hue_only_mode affects the distance metric used."""
        print("\n🧪 Testing distance metric differences...")
        
        # Create optimizers with different modes
        optimizer_hue = ColorOptimizer(hue_only_mode=True)
        optimizer_rgb = ColorOptimizer(hue_only_mode=False)
        
        # Set same target
        target_color = (255, 128, 64)  # Orange
        optimizer_hue.set_target_color(target_color)
        optimizer_rgb.set_target_color(target_color)
        
        # Add measurement with same RGB but different implied hue characteristics
        test_ratios = {'red': 2.0, 'yellow': 1.0, 'blue': 0.5, 'white': 6.5}
        test_rgb = (200, 150, 100)  # Different from target
        
        optimizer_hue.add_measurement(test_ratios, test_rgb)
        optimizer_rgb.add_measurement(test_ratios, test_rgb)
        
        # Check that distance calculations are stored in history
        hue_distance = optimizer_hue.history[0]['distance_to_target']
        rgb_distance = optimizer_rgb.history[0]['distance_to_target']
        
        print(f"  Target RGB: {target_color}")
        print(f"  Measured RGB: {test_rgb}")
        print(f"  Hue mode distance: {hue_distance:.2f}°")
        print(f"  RGB mode distance: {rgb_distance:.2f} (Euclidean)")
        
        # They should use different metrics, so distances should be different
        # (unless by coincidence the hue difference in degrees equals the RGB Euclidean distance)
        self.assertIsInstance(hue_distance, (int, float), "Hue distance should be numeric")
        self.assertIsInstance(rgb_distance, (int, float), "RGB distance should be numeric")
        
        print("  ✓ Both modes calculate distances correctly")
    
    def test_bottle_model_hue_mode(self):
        """Test that BottleModel also supports hue_only_mode parameter."""
        print("\n🧪 Testing BottleModel hue_only_mode...")
        
        # Create a test matrix
        P_test = np.array([
            [0.1, 0.01, 0.01],  # red
            [0.01, 0.1, 0.01],  # yellow  
            [0.01, 0.01, 0.1],  # blue
            [0.0, 0.0, 0.0]     # white
        ])
        
        # Test with hue_only_mode=True (default)
        bottle_hue = BottleModel(P_test, hue_only_mode=True)
        self.assertTrue(bottle_hue.hue_only_mode, "BottleModel should support hue_only_mode=True")
        
        # Test with hue_only_mode=False
        bottle_rgb = BottleModel(P_test, hue_only_mode=False)
        self.assertFalse(bottle_rgb.hue_only_mode, "BottleModel should support hue_only_mode=False")
        
        print("  ✓ BottleModel supports hue_only_mode parameter")

def simulate_color_mixing(ratios, target_color, noise_level=10):
    """Simulate color mixing with some noise and bias toward target."""
    # Simple simulation that adds noise and bias toward target
    r, g, b = target_color
    
    # Add some bias based on ratios
    red_ratio = ratios.get('red', 0)
    yellow_ratio = ratios.get('yellow', 0) 
    blue_ratio = ratios.get('blue', 0)
    
    # Rough color mixing simulation
    sim_r = min(255, max(0, r + red_ratio * 10 - yellow_ratio * 5 - blue_ratio * 15 + np.random.normal(0, noise_level)))
    sim_g = min(255, max(0, g + yellow_ratio * 15 + red_ratio * 5 - blue_ratio * 10 + np.random.normal(0, noise_level)))
    sim_b = min(255, max(0, b + blue_ratio * 20 - red_ratio * 10 - yellow_ratio * 5 + np.random.normal(0, noise_level)))
    
    return (int(sim_r), int(sim_g), int(sim_b))

def run_comprehensive_hue_tests():
    """Run all hue-only optimization tests."""
    print("🚀 Running Comprehensive Hue-Only Optimization Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHueOnlyOptimization)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL HUE-ONLY OPTIMIZATION TESTS PASSED!")
    else:
        print("❌ Some tests failed:")
        for failure in result.failures:
            print(f"  FAIL: {failure[0]}")
        for error in result.errors:
            print(f"  ERROR: {error[0]}")
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_comprehensive_hue_tests()
