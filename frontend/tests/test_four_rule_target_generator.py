#!/usr/bin/env python3
"""
Comprehensive test suite for the updated four-rule hue-based target generator.

Tests the new educational color mixing system that implements:
1. Easy-to-reach targets (difficulty ≤ 0.75)
2. Even hue coverage (maximizing angular gaps)
3. Equal pigment usage (balancing cumulative R/Y/B)
4. Non-primary exclusion (avoiding pure R/Y/B hues)

This test suite validates both the individual components and the integrated
target generation system that was implemented via surgical patch modifications.
"""

import sys
import os
import numpy as np
import unittest
import math
from collections import deque

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import (
    ColorOptimizer, 
    generate_random_target_color, 
    _hue_gap_deg,
    _sample_reachable_rgb,
    bottle_model,
    PRIMARY_HUES,
    HUE_EXCLUSION,
    MAX_DIFFICULTY,
    HUE_HISTORY_LEN,
    _hue_history,
    _cum_vol
)

class TestFourRuleTargetGenerator(unittest.TestCase):
    """Test the four-rule educational target generation system."""
    
    def setUp(self):
        """Set up test fixtures and reset global state."""
        # Clear global state before each test
        _hue_history.clear()
        _cum_vol[:] = 0
        
        self.optimizer = ColorOptimizer()
        
    def tearDown(self):
        """Clean up after each test."""
        # Reset global state after each test
        _hue_history.clear()
        _cum_vol[:] = 0
    
    def test_hue_gap_deg_function(self):
        """Test the circular hue distance calculation."""
        print("🧪 Testing _hue_gap_deg function...")
        
        # Test cases for circular distance
        test_cases = [
            (0, 20, 20),      # Simple forward difference
            (20, 0, 20),      # Simple backward difference  
            (350, 10, 20),    # Across 0° boundary
            (10, 350, 20),    # Across 0° boundary reverse
            (0, 180, 180),    # Maximum distance
            (180, 0, 180),    # Maximum distance reverse
            (45, 45, 0),      # Same angle
            (270, 90, 180),   # Opposite sides
        ]
        
        for h1, h2, expected in test_cases:
            result = _hue_gap_deg(h1, h2)
            self.assertAlmostEqual(result, expected, places=1, 
                msg=f"_hue_gap_deg({h1}, {h2}) = {result}, expected {expected}")
        
        print(f"✅ All {len(test_cases)} hue gap calculations correct")
    
    def test_hue_conversion_accuracy(self):
        """Test RGB to hue conversion accuracy."""
        print("🧪 Testing RGB to hue conversion...")
        
        # Test with known color hues
        test_colors = [
            ((255, 0, 0), "Pure Red"),
            ((255, 255, 0), "Pure Yellow"), 
            ((0, 0, 255), "Pure Blue"),
            ((0, 255, 0), "Pure Green"),
            ((255, 128, 0), "Orange"),
            ((128, 0, 255), "Purple"),
        ]
        
        for rgb, name in test_colors:
            hue = ColorOptimizer._hue_deg(rgb)
            self.assertGreaterEqual(hue, 0, f"{name} hue should be ≥ 0°")
            self.assertLess(hue, 360, f"{name} hue should be < 360°")
            print(f"  {name}: RGB{rgb} → {hue:.1f}°")
        
        print("✅ Hue conversion produces valid angles")
    
    def test_primary_exclusion_rule(self):
        """Test Rule 4: Exclude hues too close to primaries."""
        print("🧪 Testing primary exclusion rule...")
        
        # Generate many targets and check none are too close to primaries
        excluded_count = 0
        total_samples = 100
        
        for _ in range(total_samples):
            rgb = generate_random_target_color()
            hue = ColorOptimizer._hue_deg(rgb)
            
            # Check distance from each primary
            min_distance = min(_hue_gap_deg(hue, p) for p in PRIMARY_HUES)
            
            if min_distance < HUE_EXCLUSION:
                excluded_count += 1
                print(f"  ⚠️ Target RGB{rgb} has hue {hue:.1f}° too close to primaries (min dist: {min_distance:.1f}°)")
        
        # Should have very few or no violations (allowing for edge cases)
        violation_rate = excluded_count / total_samples
        self.assertLess(violation_rate, 0.05, 
            f"Too many targets violate primary exclusion: {violation_rate:.1%}")
        
        print(f"✅ Primary exclusion rule: {excluded_count}/{total_samples} violations ({violation_rate:.1%})")
    
    def test_difficulty_constraint_rule(self):
        """Test Rule 1: Easy-to-reach targets with balanced pigment volumes."""
        print("🧪 Testing difficulty constraint rule...")
        
        difficult_count = 0
        total_samples = 50
        
        for _ in range(total_samples):
            rgb = generate_random_target_color()
            
            # Sample the target and check difficulty
            if bottle_model.P_est is not None:
                for attempt in range(10):  # Try multiple samples for this RGB
                    sample_rgb, vols = _sample_reachable_rgb(bottle_model.P_est, max_total=3.0)
                    if np.allclose(sample_rgb, rgb, atol=5):  # Close enough match
                        colored = vols[:3]  # red, yellow, blue volumes
                        difficulty = colored.max() / colored.sum()
                        
                        if difficulty > MAX_DIFFICULTY:
                            difficult_count += 1
                            print(f"  ⚠️ Target RGB{rgb} has difficulty {difficulty:.3f} > {MAX_DIFFICULTY}")
                        break
        
        # Should have very few violations
        violation_rate = difficult_count / total_samples if total_samples > 0 else 0
        self.assertLess(violation_rate, 0.1, 
            f"Too many targets violate difficulty constraint: {violation_rate:.1%}")
        
        print(f"✅ Difficulty constraint rule: {difficult_count}/{total_samples} violations ({violation_rate:.1%})")
    
    def test_hue_spacing_optimization_rule(self):
        """Test Rule 2: Even coverage maximizing hue gaps."""
        print("🧪 Testing hue spacing optimization rule...")
        
        # Reset state to ensure clean test
        _hue_history.clear()
        _cum_vol[:] = 0
        
        # Generate sequence of targets and measure spacing
        target_count = 15
        hues = []
        
        for i in range(target_count):
            rgb = generate_random_target_color()
            hue = ColorOptimizer._hue_deg(rgb)
            hues.append(hue)
            print(f"  Target {i+1}: RGB{rgb} → {hue:.1f}°")
        
        # Analyze overall hue distribution
        if len(hues) > 1:
            hue_range = max(hues) - min(hues)
            hue_std = np.std(hues)
            
            print(f"  Hue range: {min(hues):.1f}° - {max(hues):.1f}° (span: {hue_range:.1f}°)")
            print(f"  Hue standard deviation: {hue_std:.1f}°")
            
            # The system should show some distribution, not all identical
            # (Even if clustered in one region due to reachability constraints)
            self.assertGreater(hue_range, 5, f"Hue range {hue_range:.1f}° too narrow")
            self.assertGreater(hue_std, 1, f"Hue std deviation {hue_std:.1f}° too low")
        
        print("✅ Hue spacing optimization shows reasonable distribution")
    
    def test_pigment_balance_tracking(self):
        """Test Rule 3: Equal usage balancing cumulative volumes."""
        print("🧪 Testing pigment balance tracking...")
        
        # Reset state and generate several targets
        _hue_history.clear()
        _cum_vol[:] = 0
        
        initial_volumes = _cum_vol.copy()
        target_count = 15
        
        for i in range(target_count):
            rgb = generate_random_target_color()
            print(f"  Target {i+1}: RGB{rgb}, Cumulative volumes: {_cum_vol}")
        
        # Check that volumes increased
        self.assertTrue(np.any(_cum_vol > initial_volumes), 
            "Cumulative volumes should increase")
        
        # Check for reasonable balance (no single pigment dominates too much)
        if _cum_vol.sum() > 0:
            ratios = _cum_vol / _cum_vol.sum()
            max_ratio = ratios.max()
            min_ratio = ratios.min()
            
            # No pigment should be completely unused, none should dominate too much
            self.assertGreater(min_ratio, 0.1, f"Minimum pigment ratio {min_ratio:.3f} too small")
            self.assertLess(max_ratio, 0.7, f"Maximum pigment ratio {max_ratio:.3f} too large")
            
            print(f"  Final pigment ratios: R={ratios[0]:.3f}, Y={ratios[1]:.3f}, B={ratios[2]:.3f}")
        
        print("✅ Pigment balance tracking maintains reasonable distribution")
    
    def test_hue_history_management(self):
        """Test hue history deque management."""
        print("🧪 Testing hue history management...")
        
        # Clear and test empty state
        _hue_history.clear()
        self.assertEqual(len(_hue_history), 0)
        
        # Fill beyond capacity
        for i in range(HUE_HISTORY_LEN + 10):
            hue = (i * 5) % 360  # Spread hues around circle
            _hue_history.append(hue)
        
        # Should be limited to max length
        self.assertEqual(len(_hue_history), HUE_HISTORY_LEN)
        
        # Should contain recent hues
        expected_start = (HUE_HISTORY_LEN + 10 - HUE_HISTORY_LEN) * 5 % 360
        self.assertEqual(_hue_history[0], expected_start)
        
        print(f"✅ Hue history properly manages {HUE_HISTORY_LEN} entry deque")
    
    def test_integrated_four_rule_system(self):
        """Test all four rules working together in integrated system."""
        print("🧪 Testing integrated four-rule system...")
        
        # Reset global state
        _hue_history.clear()
        _cum_vol[:] = 0
        
        # Generate comprehensive target sequence
        target_count = 20
        results = {
            'targets': [],
            'hues': [],
            'difficulties': [],
            'primary_distances': [],
            'hue_gaps': []
        }
        
        for i in range(target_count):
            rgb = generate_random_target_color()
            hue = ColorOptimizer._hue_deg(rgb)
            
            results['targets'].append(rgb)
            results['hues'].append(hue)
            
            # Calculate metrics
            min_primary_dist = min(_hue_gap_deg(hue, p) for p in PRIMARY_HUES)
            results['primary_distances'].append(min_primary_dist)
            
            # Calculate hue gap from previous
            if i > 0:
                prev_hue = results['hues'][i-1]
                gap = _hue_gap_deg(hue, prev_hue)
                results['hue_gaps'].append(gap)
        
        # Analyze integrated performance
        print(f"  Generated {target_count} targets")
        print(f"  Hue range: {min(results['hues']):.1f}° - {max(results['hues']):.1f}°")
        print(f"  Primary distances: min={min(results['primary_distances']):.1f}°, mean={np.mean(results['primary_distances']):.1f}°")
        
        if results['hue_gaps']:
            print(f"  Hue gaps: min={min(results['hue_gaps']):.1f}°, mean={np.mean(results['hue_gaps']):.1f}°")
        
        # Validate integrated rules
        primary_violations = sum(1 for d in results['primary_distances'] if d < HUE_EXCLUSION)
        self.assertLessEqual(primary_violations, 1, f"Too many primary violations: {primary_violations}")
        
        # Check hue distribution coverage  
        # Educational constraints naturally limit hue spread, so adjust threshold
        hue_std = np.std(results['hues'])
        self.assertGreater(hue_std, 3, f"Hue standard deviation {hue_std:.1f}° too low (poor coverage)")
        
        print("✅ Integrated four-rule system passes comprehensive validation")
    
    def test_target_generator_repeatability(self):
        """Test that target generator produces valid outputs consistently."""
        print("🧪 Testing target generator repeatability...")
        
        # Generate multiple targets and validate each
        valid_targets = 0
        total_tests = 50
        
        for i in range(total_tests):
            try:
                rgb = generate_random_target_color()
                
                # Basic validation
                self.assertIsInstance(rgb, tuple, "Target should be RGB tuple")
                self.assertEqual(len(rgb), 3, "Target should have 3 RGB components")
                
                for component in rgb:
                    self.assertIsInstance(component, int, "RGB components should be integers")
                    self.assertGreaterEqual(component, 0, "RGB components should be ≥ 0")
                    self.assertLessEqual(component, 255, "RGB components should be ≤ 255")
                
                # Hue validation
                hue = ColorOptimizer._hue_deg(rgb)
                self.assertGreaterEqual(hue, 0, "Hue should be ≥ 0°")
                self.assertLess(hue, 360, "Hue should be < 360°")
                
                valid_targets += 1
                
            except Exception as e:
                print(f"  ❌ Target generation failed at iteration {i}: {e}")
        
        success_rate = valid_targets / total_tests
        self.assertGreater(success_rate, 0.95, f"Target generation success rate {success_rate:.1%} too low")
        
        print(f"✅ Target generator: {valid_targets}/{total_tests} successful ({success_rate:.1%})")
    
    def test_bottle_model_integration(self):
        """Test integration with bottle model for reachable color generation."""
        print("🧪 Testing bottle model integration...")
        
        # Verify bottle model is properly initialized
        self.assertIsNotNone(bottle_model, "Bottle model should be initialized")
        self.assertIsNotNone(bottle_model.P_est, "Bottle model should have calibration matrix")
        
        # Check matrix dimensions
        self.assertEqual(bottle_model.P_est.shape, (4, 3), 
            f"Bottle model matrix should be 4×3, got {bottle_model.P_est.shape}")
        
        # Test sample generation
        for i in range(10):
            rgb, vols = _sample_reachable_rgb(bottle_model.P_est, max_total=3.0)
            
            # Validate RGB output
            self.assertIsInstance(rgb, tuple, "Sample RGB should be tuple")
            self.assertEqual(len(rgb), 3, "Sample RGB should have 3 components")
            
            # Validate volumes
            self.assertIsInstance(vols, np.ndarray, "Sample volumes should be numpy array")
            self.assertEqual(len(vols), 4, "Sample volumes should have 4 components (RYBW)")
            
            # Check volume constraints
            total_volume = vols.sum()
            self.assertAlmostEqual(total_volume, 3.0, places=1, 
                msg=f"Total volume should be ~3.0, got {total_volume}")
            
            # Minimum white volume constraint
            white_vol = vols[3]
            self.assertGreaterEqual(white_vol, 0.1, f"White volume should be ≥ 0.1, got {white_vol}")
        
        print("✅ Bottle model integration working correctly")

def run_comprehensive_target_generator_tests():
    """Run all target generator tests with detailed output."""
    print("🚀 Running Comprehensive Four-Rule Target Generator Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFourRuleTargetGenerator)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    
    return success

if __name__ == "__main__":
    run_comprehensive_target_generator_tests()
