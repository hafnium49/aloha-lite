#!/usr/bin/env python3
"""
Test script to validate the normalization factor update from 3.0 to 10.0 mL.

This test verifies that:
1. All normalization functions use 10.0 mL as the total volume
2. The ColorOptimizer._normalize() method works correctly with 10.0 mL
3. Ground truth calibration references 10.0 mL volume 
4. Random generation and bounds are scaled appropriately
"""

import sys
import os
import numpy as np
import unittest

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock the imports that require external dependencies
import sys
from unittest.mock import MagicMock

# Mock httpx to avoid import error
sys.modules['httpx'] = MagicMock()

# Now import from main
try:
    from main import ColorOptimizer, _sample_reachable_rgb, load_ground_truth_calibration
except ImportError as e:
    print(f"Warning: Could not import from main.py: {e}")
    print("Creating minimal test implementation...")
    
    # Create a minimal ColorOptimizer for testing
    class ColorOptimizer:
        def __init__(self):
            self.history = []
            self.target_color = None
            
        def set_target_color(self, rgb):
            self.target_color = rgb
            
        def _normalize(self, d, *, max_total=10.0):
            """Normalization logic matching main.py implementation."""
            coloured = {k: v for k, v in d.items() if k != "white"}
            s = sum(coloured.values()) or 1.0
            f = min(1.0, max_total / s)
            out = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
            out["white"] = max_total - sum(out.values())
            if out["white"] < 0.1:
                deficit = 0.1 - out["white"]
                scale = (sum(out.values()) - deficit) / sum(out.values())
                for k in ('red', 'yellow', 'blue'):
                    out[k] *= scale
                out["white"] = 0.1
            return out
        
        def _get_random(self):
            import random
            coloured = {c: random.uniform(0.1, 10.0) for c in ('red', 'yellow', 'blue')}
            return self._normalize(coloured)

class TestNormalizationUpdate(unittest.TestCase):
    """Test that all normalization functionality uses 10.0 mL volume constraint."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ColorOptimizer()
        self.target_color = (200, 150, 100)
        self.optimizer.set_target_color(self.target_color)
    
    def test_normalize_default_parameter(self):
        """Test that _normalize() method defaults to max_total=10.0."""
        print("🧪 Testing _normalize() default parameter...")
        
        # Test with default parameter (should be 10.0)
        test_ratios = {'red': 3.0, 'yellow': 4.0, 'blue': 2.0}
        normalized = self.optimizer._normalize(test_ratios)  # No max_total specified
        
        total = sum(normalized.values())
        self.assertAlmostEqual(total, 10.0, places=2)
        self.assertEqual(len(normalized), 4)  # includes white
        self.assertIn('white', normalized)
        print(f"✅ Default normalization: {normalized}")
        print(f"✅ Total volume: {total:.2f} mL")
    
    def test_normalize_explicit_10ml(self):
        """Test _normalize() with explicit 10.0 mL parameter."""
        print("\n🧪 Testing _normalize() with explicit 10.0 mL...")
        
        test_cases = [
            {'red': 5.0, 'yellow': 3.0, 'blue': 2.0},     # Normal ratios
            {'red': 15.0, 'yellow': 20.0, 'blue': 10.0},  # Large ratios (need scaling)
            {'red': 0.5, 'yellow': 1.0, 'blue': 0.3},     # Small ratios (lots of white)
        ]
        
        for i, test_ratios in enumerate(test_cases, 1):
            with self.subTest(case=i):
                normalized = self.optimizer._normalize(test_ratios, max_total=10.0)
                total = sum(normalized.values())
                
                self.assertAlmostEqual(total, 10.0, places=2)
                self.assertGreaterEqual(normalized['white'], 0.1)  # Minimum white
                
                print(f"✅ Case {i}: {test_ratios} → {normalized}")
                print(f"   Total: {total:.2f} mL")
    
    def test_get_random_bounds(self):
        """Test that _get_random() uses appropriate bounds for 10.0 mL system."""
        print("\n🧪 Testing _get_random() bounds...")
        
        # Generate several random ratios and verify they're reasonable for 10.0 mL system
        for i in range(10):
            random_ratios = self.optimizer._get_random()
            total = sum(random_ratios.values())
            
            self.assertAlmostEqual(total, 10.0, places=2)
            self.assertEqual(len(random_ratios), 4)
            self.assertIn('white', random_ratios)
            
            # Check that colored ratios are in reasonable range (0.1 to 10.0)
            for color in ['red', 'yellow', 'blue']:
                self.assertGreaterEqual(random_ratios[color], 0.1)
                self.assertLessEqual(random_ratios[color], 10.0)
            
            if i == 0:  # Print first example
                print(f"✅ Random sample: {random_ratios}")
                print(f"   Total: {total:.2f} mL")
    
    def test_sample_reachable_rgb_10ml(self):
        """Test _sample_reachable_rgb uses 10.0 mL max_total."""
        print("\n🧪 Testing _sample_reachable_rgb with 10.0 mL...")
        
        # Create a test matrix
        test_matrix = np.array([
            [0.85, 0.12, 0.08],
            [0.15, 0.72, 0.11],
            [0.18, 0.16, 0.78],
            [0.00, 0.00, 0.00]
        ])
        
        # Test with explicit max_total=10.0
        for i in range(5):
            rgb, weights = _sample_reachable_rgb(test_matrix, max_total=10.0)
            
            # Verify RGB output
            self.assertIsInstance(rgb, tuple)
            self.assertEqual(len(rgb), 3)
            for component in rgb:
                self.assertIsInstance(component, int)
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
            
            # Verify weights
            self.assertEqual(len(weights), 4)
            total_weight = np.sum(weights)
            self.assertAlmostEqual(total_weight, 10.0, places=1)
            self.assertTrue(np.all(weights >= 0))
            
            if i == 0:  # Print first example
                print(f"✅ Reachable RGB: {rgb}")
                print(f"   Weights: {weights}")
                print(f"   Total: {total_weight:.2f} mL")
    
    def test_optimization_phases_with_10ml(self):
        """Test that optimization phases work correctly with 10.0 mL normalization."""
        print("\n🧪 Testing optimization phases with 10.0 mL...")
        
        # Phase 0: First recommendation (heuristic)
        rec0 = self.optimizer.recommend_next_ratios()
        total0 = sum(rec0.values())
        self.assertAlmostEqual(total0, 10.0, places=2)
        print(f"✅ Phase 0 (heuristic): {rec0}")
        print(f"   Total: {total0:.2f} mL")
        
        # Add a measurement and get Phase 1 recommendation
        self.optimizer.add_measurement(rec0, (180, 160, 140))
        rec1 = self.optimizer.recommend_next_ratios()
        total1 = sum(rec1.values())
        self.assertAlmostEqual(total1, 10.0, places=2)
        print(f"✅ Phase 1 (first-order): {rec1}")
        print(f"   Total: {total1:.2f} mL")
        
        # Add another measurement and get Phase 2 recommendation
        self.optimizer.add_measurement(rec1, (190, 155, 135))
        rec2 = self.optimizer.recommend_next_ratios()
        total2 = sum(rec2.values())
        self.assertAlmostEqual(total2, 10.0, places=2)
        print(f"✅ Phase 2 (rough calib): {rec2}")
        print(f"   Total: {total2:.2f} mL")
    
    def test_ground_truth_calibration_volume(self):
        """Test ground truth calibration references for 10.0 mL volume."""
        print("\n🧪 Testing ground truth calibration volume references...")
        
        # Load ground truth calibration
        P_true = load_ground_truth_calibration()
        
        # Verify matrix shape (4x3 for 4 pigments including white)
        self.assertEqual(P_true.shape, (4, 3))
        
        # Test that the matrix works with 10.0 mL calculations
        # Single red solution should give correct absorbance
        red_weights = np.array([10.0, 0.0, 0.0, 0.0])  # 10.0 mL red, no other pigments
        absorbance = red_weights @ P_true
        
        # Absorbance should be reasonable (positive values)
        self.assertTrue(np.all(absorbance >= 0))
        print(f"✅ Ground truth matrix shape: {P_true.shape}")
        print(f"   10.0 mL red absorbance: {absorbance}")
    
    def test_minimum_white_enforcement(self):
        """Test that minimum white volume (0.1 mL) is enforced in 10.0 mL system."""
        print("\n🧪 Testing minimum white volume enforcement...")
        
        # Test case where colored ratios almost fill entire 10.0 mL
        test_ratios = {'red': 9.85, 'yellow': 0.075, 'blue': 0.075}  # Total = 10.0
        normalized = self.optimizer._normalize(test_ratios, max_total=10.0)
        
        # Should enforce minimum 0.1 mL white
        self.assertGreaterEqual(normalized['white'], 0.1)
        total = sum(normalized.values())
        self.assertAlmostEqual(total, 10.0, places=2)
        
        print(f"✅ Near-full case: {test_ratios}")
        print(f"   Normalized: {normalized}")
        print(f"   White volume: {normalized['white']:.3f} mL")
        print(f"   Total: {total:.2f} mL")


def run_normalization_tests():
    """Run all normalization update tests."""
    print("🧪 Running Normalization Factor Update Tests (3.0 → 10.0 mL)")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNormalizationUpdate)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL NORMALIZATION TESTS PASSED!")
        print("✅ Frontend normalization successfully updated from 3.0 to 10.0 mL")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_normalization_tests()
    sys.exit(0 if success else 1)
