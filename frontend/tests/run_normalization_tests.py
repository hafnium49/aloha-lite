#!/usr/bin/env python3
"""
Comprehensive test runner for the updated frontend with 10.0 mL normalization.

This test runner executes all tests related to the normalization update from 3.0 to 10.0 mL
and validates the integration of all frontend changes.
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
        
        if hasattr(module, 'run_normalization_tests'):
            # Normalization-specific test runner
            success = module.run_normalization_tests()
        elif hasattr(module, 'run_comprehensive_target_generator_tests'):
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
        import traceback
        traceback.print_exc()
        return False

def run_all_normalization_tests():
    """Run all frontend tests including normalization updates."""
    print("🚀 Running Comprehensive Frontend Test Suite with 10.0 mL Normalization")
    print("Testing: Updated normalization, hue optimization, 4-pigment system, and target generation")
    print("=" * 80)
    
    # Test modules in order of importance
    test_modules = [
        ("test_normalization_update", "🎯 Normalization Factor Update (3.0 → 10.0 mL)"),
        ("test_4_pigment_system", "🧪 4-Pigment System with White Solvent"),
        ("test_ground_truth_calibration", "📊 Ground Truth Calibration System"),
        ("test_four_rule_target_generator", "🎨 Four-Rule Target Color Generator"),
        ("test_hue_optimization", "🌈 Hue-Based Color Optimization"),
        ("test_color_space", "🔬 Color Space and Optimization"),
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
        print("🎉 ALL TESTS PASSED!")
        print("✅ Frontend normalization successfully updated from 3.0 to 10.0 mL")
        print("✅ All optimization systems working correctly with new volume constraint")
        print("✅ 4-pigment system with white solvent integration verified")
    else:
        print("⚠️  Some tests failed. Check individual test outputs for details.")
    
    return overall_success

def run_specific_test(test_name):
    """Run a specific test by name."""
    test_map = {
        "normalization": ("test_normalization_update", "Normalization Factor Update"),
        "4pigment": ("test_4_pigment_system", "4-Pigment System"),
        "ground_truth": ("test_ground_truth_calibration", "Ground Truth Calibration"),
        "target_gen": ("test_four_rule_target_generator", "Target Generator"),
        "hue": ("test_hue_optimization", "Hue Optimization"),
        "color_space": ("test_color_space", "Color Space"),
    }
    
    if test_name in test_map:
        module_name, description = test_map[test_name]
        return run_test_module(module_name, description)
    else:
        print(f"❌ Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_map.keys())}")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_normalization_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
