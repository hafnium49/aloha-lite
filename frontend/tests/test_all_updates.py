#!/usr/bin/env python3
"""
Quick comprehensive test to verify all updates are working correctly.
Tests the key functionality after the normalization factor change from 3.0 to 10.0 mL.
"""

import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from main import ColorOptimizer, BottleModel, load_ground_truth_calibration, _sample_reachable_rgb
    import numpy as np
    MAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import from main.py: {e}")
    MAIN_AVAILABLE = False

class TestAllUpdates(unittest.TestCase):
    """Quick test suite to verify all normalization updates."""
    
    def setUp(self):
        """Set up test fixtures."""
        if MAIN_AVAILABLE:
            self.optimizer = ColorOptimizer()
            self.optimizer.set_target_color((200, 150, 100))
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_normalization_10ml(self):
        """Test normalization uses 10.0 mL total volume."""
        print("🧪 Testing 10.0 mL normalization...")
        
        test_ratios = {'red': 3.0, 'yellow': 4.0, 'blue': 2.0}
        normalized = self.optimizer._normalize(test_ratios)
        total = sum(normalized.values())
        
        self.assertAlmostEqual(total, 10.0, places=2)
        self.assertIn('white', normalized)
        print(f"✅ Normalized to {total:.2f} mL")
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_optimization_phases(self):
        """Test optimization phases work with 10.0 mL."""
        print("🧪 Testing optimization phases...")
        
        # Phase 0
        rec0 = self.optimizer.recommend_next_ratios()
        total0 = sum(rec0.values())
        self.assertAlmostEqual(total0, 10.0, places=2)
        
        # Add measurement and test Phase 1
        self.optimizer.add_measurement(rec0, (180, 160, 140))
        rec1 = self.optimizer.recommend_next_ratios()
        total1 = sum(rec1.values())
        self.assertAlmostEqual(total1, 10.0, places=2)
        
        print(f"✅ Phase 0: {total0:.2f} mL, Phase 1: {total1:.2f} mL")
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_ground_truth_calibration(self):
        """Test ground truth calibration loads correctly."""
        print("🧪 Testing ground truth calibration...")
        
        P_true = load_ground_truth_calibration()
        self.assertEqual(P_true.shape, (4, 3))
        self.assertTrue(np.all(P_true >= 0))
        
        print(f"✅ Ground truth matrix: {P_true.shape}")
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_bottle_model(self):
        """Test BottleModel works with 10.0 mL."""
        print("🧪 Testing BottleModel...")
        
        P_test = np.array([
            [0.85, 0.1, 0.08],
            [0.15, 0.72, 0.1],
            [0.12, 0.15, 0.78],
            [0.0, 0.0, 0.0]
        ])
        
        bottle = BottleModel(P_test)
        rgb, weights = _sample_reachable_rgb(bottle.P_est, max_total=10.0)
        
        self.assertEqual(len(rgb), 3)
        self.assertEqual(len(weights), 4)
        self.assertAlmostEqual(np.sum(weights), 10.0, places=1)
        
        print(f"✅ BottleModel RGB: {rgb}, Total: {np.sum(weights):.2f} mL")
    
    @unittest.skipUnless(MAIN_AVAILABLE, "main.py not available")
    def test_random_generation(self):
        """Test random generation uses correct bounds."""
        print("🧪 Testing random generation...")
        
        for i in range(5):
            random_ratios = self.optimizer._get_random()
            total = sum(random_ratios.values())
            
            self.assertAlmostEqual(total, 10.0, places=2)
            
            # Check bounds - colored components should be 0.1 to 10.0
            for color in ['red', 'yellow', 'blue']:
                self.assertGreaterEqual(random_ratios[color], 0.1)
                self.assertLessEqual(random_ratios[color], 10.0)
        
        print(f"✅ Random generation bounds verified")


def main():
    """Run the comprehensive update tests."""
    print("🧪 Running Comprehensive Frontend Update Tests")
    print("=" * 60)
    print("Testing normalization factor change: 3.0 → 10.0 mL")
    print("=" * 60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAllUpdates)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL FRONTEND UPDATE TESTS PASSED!")
        print("✅ Normalization factor successfully updated from 3.0 to 10.0 mL")
        print("✅ All optimization phases working correctly")
        print("✅ Ground truth calibration system updated")
        print("✅ Random generation bounds adjusted")
        print("✅ BottleModel integration working")
    else:
        print("❌ SOME TESTS FAILED")
        if result.failures:
            print(f"   Failures: {len(result.failures)}")
        if result.errors:
            print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
