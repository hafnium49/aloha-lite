#!/usr/bin/env python3
"""
Comprehensive test runner for the updated frontend with four-rule target generator.

This test runner executes all tests related to the new hue-based optimization
system and validates the integration of the surgical patch modifications.
"""

import sys
import os
import unittest
import subprocess
from pathlib import Path

# Add frontend directory to path
frontend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(frontend_dir))

def run_test_module(module_name, description):
    """Run a specific test module and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        # Import and run the test module
        module = __import__(module_name, fromlist=[''])
        
        if hasattr(module, 'run_comprehensive_target_generator_tests'):
            # Custom test runner
            success = module.run_comprehensive_target_generator_tests()
        elif hasattr(module, 'run_tests'):
            # Custom test runner
            success = module.run_tests()
        else:
            # Standard unittest runner
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            success = len(result.failures) == 0 and len(result.errors) == 0
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status}: {description}")
        return success
        
    except Exception as e:
        print(f"❌ ERROR running {module_name}: {e}")
        return False

def run_all_frontend_tests():
    """Run all frontend tests in order of importance."""
    print("🚀 Running Comprehensive Frontend Test Suite")
    print("Testing updated four-rule hue-based target generator system")
    
    # Test modules in order of importance
    test_modules = [
        ("test_four_rule_target_generator", "Four-Rule Target Generator Tests"),
        ("test_hue_optimization", "Hue Optimization System Tests"),
        ("test_4_pigment_system", "Four-Pigment System Tests"),
        ("test_color_space", "Color Space Conversion Tests"),
        ("test_ground_truth_calibration", "Ground Truth Calibration Tests"),
        ("test_optimization", "General Optimization Tests"),
        ("test_frontend_integration", "Frontend Integration Tests"),
    ]
    
    results = {}
    total_passed = 0
    
    for module_name, description in test_modules:
        try:
            success = run_test_module(module_name, description)
            results[module_name] = success
            if success:
                total_passed += 1
        except ImportError as e:
            print(f"⚠️  Skipping {module_name}: {e}")
            results[module_name] = None
    
    # Final summary
    print(f"\n{'='*80}")
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    
    for module_name, description in test_modules:
        status = results.get(module_name)
        if status is True:
            print(f"✅ {description}")
        elif status is False:
            print(f"❌ {description}")
        else:
            print(f"⚠️  {description} (skipped)")
    
    print(f"\nTotal: {total_passed}/{len(test_modules)} test modules passed")
    
    overall_success = total_passed == len([r for r in results.values() if r is not None])
    if overall_success:
        print("🎉 ALL TESTS PASSED! The four-rule target generator is working correctly.")
    else:
        print("⚠️  Some tests failed. Check individual test outputs for details.")
    
    return overall_success

def quick_validation_test():
    """Run a quick validation of the core functionality."""
    print("\n🔬 Quick Validation Test")
    print("-" * 40)
    
    try:
        from main import (
            generate_random_target_color, 
            ColorOptimizer, 
            _hue_gap_deg,
            PRIMARY_HUES,
            HUE_EXCLUSION,
            MAX_DIFFICULTY
        )
        
        # Test 1: Basic target generation
        print("1. Testing basic target generation...")
        for i in range(5):
            rgb = generate_random_target_color()
            print(f"   Target {i+1}: RGB{rgb}")
            assert isinstance(rgb, tuple) and len(rgb) == 3
        print("   ✅ Target generation working")
        
        # Test 2: Hue gap function
        print("2. Testing hue gap calculation...")
        gap = _hue_gap_deg(10, 350)
        assert abs(gap - 20) < 1, f"Expected ~20°, got {gap}°"
        print(f"   ✅ Hue gap 10° ↔ 350° = {gap}°")
        
        # Test 3: ColorOptimizer hue calculation
        print("3. Testing ColorOptimizer hue calculation...")
        optimizer = ColorOptimizer()
        hue = optimizer._hue_deg((255, 0, 0))  # Red
        print(f"   ✅ Red RGB(255,0,0) → {hue:.1f}° hue")
        
        # Test 4: Primary exclusion constants
        print("4. Testing configuration constants...")
        print(f"   Primary hues: {PRIMARY_HUES}")
        print(f"   Exclusion zone: {HUE_EXCLUSION}°")
        print(f"   Max difficulty: {MAX_DIFFICULTY}")
        print("   ✅ Constants loaded correctly")
        
        print("\n🎉 Quick validation PASSED - Core functionality working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Quick validation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Change to tests directory
    os.chdir(Path(__file__).parent)
    
    print("Starting Frontend Test Suite for Four-Rule Target Generator")
    print(f"Working directory: {os.getcwd()}")
    
    # Quick validation first
    if not quick_validation_test():
        print("❌ Quick validation failed - stopping")
        sys.exit(1)
    
    # Run comprehensive tests
    success = run_all_frontend_tests()
    
    if success:
        print("\n🎉 SUCCESS: All frontend tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  WARNING: Some tests failed!")
        sys.exit(1)
