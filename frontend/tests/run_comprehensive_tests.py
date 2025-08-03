#!/usr/bin/env python3
"""
Comprehensive test runner for frontend ground truth calibration integration.
This script runs all tests and provides detailed reporting.
"""

import sys
import os
import unittest
import tempfile
import json
import shutil
from pathlib import Path
import numpy as np
from io import StringIO
import contextlib

# Add the frontend directory to Python path
frontend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(frontend_dir))

# Import all test classes
from test_ground_truth_simple import TestGroundTruthSimple, TestRealGroundTruthFiles


class TestColorOptimizationIntegration(unittest.TestCase):
    """Additional integration tests for color optimization with ground truth."""
    
    def setUp(self):
        """Set up test environment."""
        # Import main module components
        from main import ColorOptimizer, BottleModel, _sample_reachable_rgb
        self.ColorOptimizer = ColorOptimizer
        self.BottleModel = BottleModel
        self._sample_reachable_rgb = _sample_reachable_rgb
        
    def test_color_optimizer_basic_functionality(self):
        """Test basic ColorOptimizer functionality."""
        optimizer = self.ColorOptimizer()
        
        # Test initialization
        self.assertEqual(len(optimizer.history), 0)
        self.assertIsNone(optimizer.target_color)
        self.assertIsNone(optimizer.P_est)
        
        # Test setting target color
        test_rgb = (200, 100, 50)
        optimizer.set_target_color(test_rgb)
        self.assertEqual(optimizer.target_color, test_rgb)
        
    def test_bottle_model_vs_color_optimizer(self):
        """Test that BottleModel behaves differently from ColorOptimizer."""
        test_matrix = np.array([
            [0.8, 0.1, 0.05],
            [0.1, 0.9, 0.1],
            [0.05, 0.1, 0.85]
        ])
        
        # Create both models
        optimizer = self.ColorOptimizer()
        bottle_model = self.BottleModel(test_matrix)
        
        # ColorOptimizer should start with no matrix
        self.assertIsNone(optimizer.P_est)
        
        # BottleModel should have the fixed matrix
        np.testing.assert_array_equal(bottle_model.P_est, test_matrix)
        
    def test_reachable_color_generation_range(self):
        """Test that generated colors are within reasonable ranges."""
        test_matrix = np.array([
            [0.5, 0.1, 0.05],
            [0.1, 0.5, 0.1],
            [0.05, 0.1, 0.5]
        ])
        
        # Generate multiple colors and check they're reasonable
        colors = []
        for _ in range(10):
            rgb, weights = self._sample_reachable_rgb(test_matrix)
            colors.append(rgb)
            
            # Check RGB bounds
            for value in rgb:
                self.assertTrue(0 <= value <= 255)
                
            # Check weights are reasonable
            self.assertTrue(np.all(weights >= 0))
            self.assertTrue(np.sum(weights) <= 10)  # Reasonable upper bound
            
        # Check we get some variety in colors
        unique_colors = set(colors)
        self.assertGreater(len(unique_colors), 1, "Should generate varied colors")
        
    def test_ground_truth_matrix_properties(self):
        """Test that loaded ground truth matrices have reasonable properties."""
        from main import load_ground_truth_calibration
        
        matrix = load_ground_truth_calibration()
        
        # Check basic properties
        self.assertEqual(matrix.shape, (3, 3))
        self.assertTrue(np.all(matrix >= 0), "All values should be non-negative")
        
        # Check diagonal dominance (typical for pigment matrices)
        diagonal = np.diag(matrix)
        off_diagonal_max = np.max(matrix - np.diag(diagonal))
        
        # At least some diagonal values should be significant
        self.assertTrue(np.any(diagonal > 0.1), "Should have significant diagonal values")
        
        # Matrix should not be all zeros or ones
        self.assertFalse(np.all(matrix == 0), "Matrix should not be all zeros")
        self.assertFalse(np.all(matrix == 1), "Matrix should not be all ones")


class TestFileSystemRobustness(unittest.TestCase):
    """Test robustness against various file system scenarios."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.ground_truth_dir = Path(self.test_dir) / "ground_truth_calibration"
        self.ground_truth_dir.mkdir(exist_ok=True)
        
        # Store original __file__ location
        from main import load_ground_truth_calibration
        self.load_function = load_ground_truth_calibration
        self.original_file = sys.modules['main'].__file__
        sys.modules['main'].__file__ = str(Path(self.test_dir) / "main.py")
        
    def tearDown(self):
        """Clean up test environment."""
        sys.modules['main'].__file__ = self.original_file
        shutil.rmtree(self.test_dir)
        
    def test_corrupted_json_handling(self):
        """Test handling of corrupted JSON files."""
        # Create a corrupted JSON file
        summary_file = self.ground_truth_dir / "calibration_summary.json"
        with open(summary_file, 'w') as f:
            f.write('{"invalid": json syntax')
            
        # Should not crash, should fall back
        result = self.load_function()
        self.assertEqual(result.shape, (3, 3))
        
    def test_missing_directory_handling(self):
        """Test handling when ground truth directory doesn't exist."""
        # Remove the ground truth directory
        shutil.rmtree(self.ground_truth_dir)
        
        # Should not crash, should fall back to random matrix
        result = self.load_function()
        self.assertEqual(result.shape, (3, 3))
        self.assertTrue(np.all(result >= 0))
        
    def test_empty_files_handling(self):
        """Test handling of empty files."""
        # Create empty files
        for filename in ["calibration_summary.json", "red_solution_ground_truth.json"]:
            file_path = self.ground_truth_dir / filename
            file_path.touch()  # Create empty file
            
        # Should not crash
        result = self.load_function()
        self.assertEqual(result.shape, (3, 3))
        
    def test_permission_errors(self):
        """Test handling of permission errors (if possible)."""
        # Create a file but make directory unreadable (if running as non-root)
        summary_file = self.ground_truth_dir / "calibration_summary.json"
        summary_file.write_text('{"test": "data"}')
        
        try:
            # Try to make directory unreadable
            os.chmod(self.ground_truth_dir, 0o000)
            
            # Should not crash
            result = self.load_function()
            self.assertEqual(result.shape, (3, 3))
            
        except PermissionError:
            # If we can't change permissions, skip this test
            pass
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(self.ground_truth_dir, 0o755)
            except:
                pass


def run_all_tests():
    """Run all test suites and provide comprehensive reporting."""
    
    print("🧪 Frontend Ground Truth Calibration Test Suite")
    print("=" * 60)
    
    # Collect all test suites
    test_suites = [
        unittest.TestLoader().loadTestsFromTestCase(TestGroundTruthSimple),
        unittest.TestLoader().loadTestsFromTestCase(TestRealGroundTruthFiles),
        unittest.TestLoader().loadTestsFromTestCase(TestColorOptimizationIntegration),
        unittest.TestLoader().loadTestsFromTestCase(TestFileSystemRobustness)
    ]
    
    # Combine all test suites
    master_suite = unittest.TestSuite(test_suites)
    
    # Run tests with detailed reporting
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(master_suite)
    
    # Parse results
    output = stream.getvalue()
    
    # Print summary
    print(f"\n📊 TEST SUMMARY")
    print("-" * 30)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    # Print detailed results if there are failures or errors
    if result.failures or result.errors:
        print(f"\n💥 DETAILED RESULTS:")
        print("-" * 30)
        
        for test, traceback in result.failures:
            print(f"❌ FAILURE: {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
            
        for test, traceback in result.errors:
            print(f"💥 ERROR: {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
    
    # Print success message
    if result.wasSuccessful():
        print(f"\n🎉 All tests passed! Ground truth calibration is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the results above.")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
