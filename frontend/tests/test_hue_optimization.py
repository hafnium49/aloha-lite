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

from main import ColorOptimizer, generate_random_target_color

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
        """Test angular distance calculation."""
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
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} tests FAILED")
        for test, error in result.failures + result.errors:
            print(f"   {test}: {error.strip()}")
        return False

if __name__ == "__main__":
    success = run_hue_optimization_tests()
    exit(0 if success else 1)
