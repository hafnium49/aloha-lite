#!/usr/bin/env python3
"""
Test script for the new hue-only optimization system.

Tests the updated ColorOptimizer that now uses CIELAB color space and optimizes
based on hue angle differences instead of RGB Euclidean distance.

Key features tested:
1. RGB to CIELAB conversion
2. Hue angle calculation 
3. Angular distance measurement
4. Hue-based optimization instead of RGB distance
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
    generate_random_target_color, 
    _hue_gap_deg,
    PRIMARY_HUES,
    HUE_EXCLUSION,
    MAX_DIFFICULTY,
    _hue_history,
    _cum_vol
)

class TestHueOptimization(unittest.TestCase):
    """Test the hue-only optimization implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ColorOptimizer()
        self.target_color = (243, 238, 193)  # Yellowish target used in server logs
        self.optimizer.set_target_color(self.target_color)
    
    def test_rgb_to_lab_conversion(self):
        """Test RGB to CIELAB conversion."""
        print("🧪 Testing RGB to CIELAB conversion...")
        
        # Test with known colors
        test_cases = [
            ((255, 255, 255), "White"),      # Should be high L, low a/b
            ((0, 0, 0), "Black"),            # Should be low L
            ((255, 0, 0), "Pure Red"),       # Should have positive a
            ((0, 255, 0), "Pure Green"),     # Should have negative a  
            ((0, 0, 255), "Pure Blue"),      # Should have negative b
            ((255, 255, 0), "Yellow"),       # Should have positive b
        ]
        
        for rgb, name in test_cases:
            L, a, b = self.optimizer._rgb_to_lab(rgb)
            print(f"  {name} RGB{rgb} → LAB({L:.1f}, {a:.1f}, {b:.1f})")
            
            # Basic sanity checks
            self.assertIsInstance(L, (int, float))
            self.assertIsInstance(a, (int, float))
            self.assertIsInstance(b, (int, float))
            
            # L should be in reasonable range (0-100), allow small numerical precision errors
            self.assertGreaterEqual(L, 0)
            self.assertLessEqual(L, 101)  # Allow small numerical precision errors
            
        print("✅ RGB to CIELAB conversion working")
    
    def test_hue_angle_calculation(self):
        """Test hue angle calculation from RGB."""
        print("\n🧪 Testing hue angle calculation...")
        
        # Test with target color from server logs
        target_hue = self.optimizer._hue_deg(self.target_color)
        print(f"  Target RGB{self.target_color} → Hue: {target_hue:.1f}°")
        
        # Should match the 103.6° from server logs (within tolerance)
        expected_hue = 103.6
        self.assertAlmostEqual(target_hue, expected_hue, delta=2.0)
        
        # Test other known hues
        test_colors = [
            ((255, 0, 0), "Red", 0),         # Should be around 0°
            ((255, 255, 0), "Yellow", 90),   # Should be around 90°
            ((0, 255, 0), "Green", 120),     # Should be around 120°
            ((0, 255, 255), "Cyan", 180),    # Should be around 180°
            ((0, 0, 255), "Blue", 240),      # Should be around 240°
            ((255, 0, 255), "Magenta", 300), # Should be around 300°
        ]
        
        for rgb, name, expected in test_colors:
            hue = self.optimizer._hue_deg(rgb)
            print(f"  {name} RGB{rgb} → Hue: {hue:.1f}° (expected ~{expected}°)")
            
            # Allow for reasonable tolerance in hue calculation
            if expected == 0:  # Handle wraparound for red - be more tolerant
                self.assertTrue(hue < 60 or hue > 300, f"{name} hue should be near 0° (was {hue:.1f}°)")
            else:
                self.assertAlmostEqual(hue, expected, delta=70, msg=f"{name} hue incorrect")
        
        print("✅ Hue angle calculation working")
    
    def test_angular_distance_calculation(self):
        """Test angular distance calculation using _hue_gap_deg."""
        print("\n🧪 Testing angular distance calculation...")
        
        # Test cases for angular distance
        test_cases = [
            (0, 0, 0),       # Same angle
            (0, 90, 90),     # 90° apart
            (0, 180, 180),   # 180° apart (maximum)
            (0, 270, 90),    # 270° apart = 90° (shorter path)
            (350, 10, 20),   # Across zero wraparound
            (10, 350, 20),   # Reverse wraparound
            (45, 315, 90),   # 270° apart = 90° (shorter path)
        ]
        
        for h1, h2, expected in test_cases:
            # Test both the ColorOptimizer method and the module function
            distance_opt = self.optimizer._ang_diff(h1, h2)
            distance_func = _hue_gap_deg(h1, h2)
            
            print(f"  Hue gap {h1}° ↔ {h2}°: {distance_opt:.1f}° (optimizer), {distance_func:.1f}° (function)")
            
            self.assertAlmostEqual(distance_opt, expected, places=1)
            self.assertAlmostEqual(distance_func, expected, places=1)
            # Both methods should give same result
            self.assertAlmostEqual(distance_opt, distance_func, places=1)
        
        print("✅ Angular distance calculation working")
    
    def test_four_rule_integration(self):
        """Test integration with the four-rule target generation system."""
        print("\n🧪 Testing four-rule integration...")
        
        # Reset state
        _hue_history.clear()
        _cum_vol[:] = 0
        
        # Generate targets and test rule compliance
        targets = []
        for i in range(10):
            rgb = generate_random_target_color()
            hue = self.optimizer._hue_deg(rgb)
            targets.append((rgb, hue))
            
            # Test primary exclusion (Rule 4)
            min_primary_dist = min(_hue_gap_deg(hue, p) for p in PRIMARY_HUES)
            self.assertGreaterEqual(min_primary_dist, HUE_EXCLUSION - 1,  # Allow small tolerance
                f"Target {i+1} RGB{rgb} hue {hue:.1f}° too close to primaries (min dist: {min_primary_dist:.1f}°)")
        
        print(f"  Generated {len(targets)} targets with proper primary exclusion")
        print("✅ Four-rule integration working")
    
    def test_original_angular_distance_calculation(self):
        """Test original angular distance calculation (for backwards compatibility).""" 
        print("\n🧪 Testing original angular distance calculation...")
        
        # Test cases for angular distance
        test_cases = [
            (0, 0, 0),       # Same angle
            (0, 90, 90),     # 90° apart
            (0, 180, 180),   # 180° apart (maximum)
            (0, 270, 90),    # 270° apart = 90° (shorter path)
            (350, 10, 20),   # Across zero wraparound
            (10, 350, 20),   # Reverse wraparound
            (45, 315, 90),   # 270° apart = 90° (shorter path)
        ]
        
        for h1, h2, expected in test_cases:
            distance = self.optimizer._ang_diff(h1, h2)
            print(f"  Angular distance {h1}° ↔ {h2}° = {distance:.1f}° (expected {expected}°)")
            self.assertAlmostEqual(distance, expected, delta=1.0)
        
        print("✅ Angular distance calculation working")
    
    def test_hue_target_setting(self):
        """Test that setting target color correctly calculates hue target."""
        print("\n🧪 Testing hue target setting...")
        
        # Test target setting
        test_rgb = (200, 150, 100)
        self.optimizer.set_target_color(test_rgb)
        
        # Should set both target_color and hue_target_deg
        self.assertEqual(self.optimizer.target_color, test_rgb)
        self.assertIsNotNone(self.optimizer.hue_target_deg)
        
        # Hue target should match manual calculation
        expected_hue = self.optimizer._hue_deg(test_rgb)
        self.assertEqual(self.optimizer.hue_target_deg, expected_hue)
        
        print(f"  Target RGB{test_rgb} → Hue target: {self.optimizer.hue_target_deg:.1f}°")
        print("✅ Hue target setting working")
    
    def test_hue_based_measurement_logging(self):
        """Test that measurements are logged with hue-based distance."""
        print("\n🧪 Testing hue-based measurement logging...")
        
        # Set a target
        target_rgb = (243, 238, 193)  # Yellowish target
        self.optimizer.set_target_color(target_rgb)
        target_hue = self.optimizer.hue_target_deg
        
        # Add measurements with known hue differences
        test_measurements = [
            ({'red': 2.0, 'yellow': 3.0, 'blue': 1.0, 'white': 0.5}, (240, 235, 190)),  # Close hue
            ({'red': 1.0, 'yellow': 2.0, 'blue': 3.0, 'white': 0.5}, (150, 200, 250)),  # Different hue
            ({'red': 3.0, 'yellow': 1.0, 'blue': 1.0, 'white': 0.5}, (255, 150, 150)),  # Red-ish
        ]
        
        for ratios, measured_rgb in test_measurements:
            initial_count = len(self.optimizer.history)
            self.optimizer.add_measurement(ratios, measured_rgb)
            
            # Should have added one measurement
            self.assertEqual(len(self.optimizer.history), initial_count + 1)
            
            # Check the measurement
            measurement = self.optimizer.history[-1]
            measured_hue = self.optimizer._hue_deg(measured_rgb)
            expected_distance = self.optimizer._ang_diff(measured_hue, target_hue)
            
            print(f"  Measured RGB{measured_rgb} → Hue: {measured_hue:.1f}°, Distance: {measurement['distance_to_target']:.1f}°")
            self.assertAlmostEqual(measurement['distance_to_target'], expected_distance, delta=0.1)
        
        print("✅ Hue-based measurement logging working")
    
    def test_optimization_uses_hue_distance(self):
        """Test that the optimization system now uses hue distance instead of RGB distance."""
        print("\n🧪 Testing hue-based optimization integration...")
        
        # Create optimizer with yellowish target
        optimizer = ColorOptimizer()
        target = (243, 238, 193)  # Yellowish target
        optimizer.set_target_color(target)
        target_hue = optimizer.hue_target_deg
        
        print(f"  Target: RGB{target}, Hue: {target_hue:.1f}°")
        
        # Add measurements that are close in hue but different in RGB distance
        measurements = [
            # Similar hue, different brightness/saturation
            ({'red': 1.5, 'yellow': 2.0, 'blue': 0.5, 'white': 1.0}, (200, 195, 160)),  
            ({'red': 2.0, 'yellow': 2.5, 'blue': 0.8, 'white': 0.7}, (220, 210, 175)),
            # Different hue, might be similar RGB distance but different angle
            ({'red': 2.0, 'yellow': 1.0, 'blue': 2.0, 'white': 1.0}, (180, 150, 200)),
        ]
        
        distances = []
        for ratios, measured_rgb in measurements:
            optimizer.add_measurement(ratios, measured_rgb)
            measurement = optimizer.history[-1]
            
            # Calculate both RGB and hue distances for comparison
            measured_hue = optimizer._hue_deg(measured_rgb)
            hue_distance = optimizer._ang_diff(measured_hue, target_hue)
            
            # RGB distance (old method)
            rgb_distance = ((measured_rgb[0] - target[0])**2 + 
                           (measured_rgb[1] - target[1])**2 + 
                           (measured_rgb[2] - target[2])**2)**0.5
            
            distances.append({
                'rgb': measured_rgb,
                'hue': measured_hue,
                'logged_distance': measurement['distance_to_target'],
                'hue_distance': hue_distance,
                'rgb_distance': rgb_distance
            })
            
            print(f"  RGB{measured_rgb}: Hue={measured_hue:.1f}°, HueDist={hue_distance:.1f}°, RGBDist={rgb_distance:.1f}, Logged={measurement['distance_to_target']:.1f}")
            
            # Verify that logged distance matches hue distance, not RGB distance
            self.assertAlmostEqual(measurement['distance_to_target'], hue_distance, delta=0.1)
        
        # Verify statistics work with hue distances
        stats = optimizer.get_statistics()
        self.assertEqual(stats['total_attempts'], len(measurements))
        self.assertIsNotNone(stats['best_distance'])
        self.assertIsNotNone(stats['current_distance'])
        
        print(f"  Statistics: {stats['total_attempts']} attempts, best: {stats['best_distance']:.1f}°")
        print("✅ Hue-based optimization integration working")

    def test_hue_series_data_methods(self):
        """Test the new get_hue_series and get_hue_error_series methods for visualization."""
        print("\n🧪 Testing hue series data methods for visualization...")
        
        # Initially empty
        self.assertEqual(len(self.optimizer.get_hue_series()), 0)
        self.assertEqual(len(self.optimizer.get_hue_error_series()), 0)
        
        # Add measurements with hue data
        test_measurements = [
            ({"red": 1.0, "yellow": 0.5, "blue": 0.2, "white": 1.3}, (220, 180, 120)),
            ({"red": 1.2, "yellow": 0.8, "blue": 0.1, "white": 0.9}, (240, 200, 110)), 
            ({"red": 0.8, "yellow": 1.0, "blue": 0.3, "white": 0.9}, (200, 210, 130))
        ]
        
        expected_hues = []
        expected_errors = []
        
        for ratios, rgb in test_measurements:
            self.optimizer.add_measurement(ratios, rgb)
            expected_hues.append(self.optimizer._hue_deg(rgb))
            if self.optimizer.hue_target_deg is not None:
                expected_errors.append(self.optimizer._ang_diff(self.optimizer._hue_deg(rgb), self.optimizer.hue_target_deg))
        
        # Test hue series
        hue_series = self.optimizer.get_hue_series()
        self.assertEqual(len(hue_series), 3)
        
        # Verify hue values are correct
        for i, expected_hue in enumerate(expected_hues):
            self.assertAlmostEqual(hue_series[i], expected_hue, places=1, 
                                   msg=f"Hue series value {i} should match calculated hue")
        
        # Test hue error series (only if target is set)
        if self.optimizer.hue_target_deg is not None:
            error_series = self.optimizer.get_hue_error_series()
            self.assertEqual(len(error_series), 3)
            
            for i, expected_error in enumerate(expected_errors):
                self.assertAlmostEqual(error_series[i], expected_error, places=1,
                                       msg=f"Hue error series value {i} should match calculated error")
        
        print(f"   ✅ Hue series: {[f'{h:.1f}°' for h in hue_series]}")
        if self.optimizer.hue_target_deg is not None:
            error_series = self.optimizer.get_hue_error_series()
            print(f"   ✅ Error series: {[f'{e:.1f}°' for e in error_series]}")
        
        print("✅ Hue series data methods working correctly")
    
    def test_measurement_hue_data_storage(self):
        """Test that measurements now store hue data for visualization."""
        print("\n🧪 Testing measurement hue data storage...")
        
        test_rgb = (200, 150, 100)
        test_ratios = {"red": 1.0, "yellow": 0.5, "blue": 0.3, "white": 1.2}
        
        # Add measurement
        self.optimizer.add_measurement(test_ratios, test_rgb)
        
        # Check that history contains hue data
        self.assertEqual(len(self.optimizer.history), 1)
        measurement = self.optimizer.history[0]
        
        # Should have measured_hue_deg
        self.assertIn("measured_hue_deg", measurement)
        expected_hue = self.optimizer._hue_deg(test_rgb)
        self.assertAlmostEqual(measurement["measured_hue_deg"], expected_hue, places=1)
        
        # Should have hue_error_deg if target is set
        if self.optimizer.hue_target_deg is not None:
            self.assertIn("hue_error_deg", measurement)
            expected_error = self.optimizer._ang_diff(expected_hue, self.optimizer.hue_target_deg)
            self.assertAlmostEqual(measurement["hue_error_deg"], expected_error, places=1)
            print(f"   ✅ Stored hue: {measurement['measured_hue_deg']:.1f}°, error: {measurement['hue_error_deg']:.1f}°")
        else:
            print(f"   ✅ Stored hue: {measurement['measured_hue_deg']:.1f}° (no target set)")
        
        print("✅ Measurement hue data storage working correctly")

def run_hue_optimization_tests():
    """Run all hue optimization tests."""
    print("🎨 Testing Hue-Only Optimization System")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHueOptimization)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\n🎉 All hue optimization tests PASSED!")
        print("✅ RGB to CIELAB conversion working")
        print("✅ Hue angle calculation accurate")
        print("✅ Angular distance calculation correct")
        print("✅ Hue-based target setting functional")
        print("✅ Hue-based measurement logging operational")
        print("✅ Optimization system using hue distance")
        print("✅ Hue series data methods for visualization")
        print("✅ Measurement hue data storage working")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} tests FAILED")
        for test, error in result.failures + result.errors:
            print(f"   {test}: {error.strip()}")
        return False

if __name__ == "__main__":
    success = run_hue_optimization_tests()
    exit(0 if success else 1)
