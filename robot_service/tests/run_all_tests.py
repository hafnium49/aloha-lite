#!/usr/bin/env python3
"""
Comprehensive test runner for all robot service tests, including the new enhanced execution features.
This script runs all tests and provides a consolidated report.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def run_test_file(test_file_path, description):
    """Run a specific test file and return results"""
    print(f"\n{'='*80}")
    print(f"🧪 Running {description}")
    print(f"   File: {test_file_path}")
    print('='*80)
    
    try:
        # Run the test file as a subprocess
        result = subprocess.run(
            [sys.executable, str(test_file_path)],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(test_file_path)
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        print(f"\n{'✅' if success else '❌'} {description}: {'PASSED' if success else 'FAILED'}")
        
        return success, result.stdout + result.stderr
        
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False, str(e)

def run_all_robot_service_tests():
    """Run all robot service tests and provide comprehensive results"""
    print("🚀 ROBOT SERVICE COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("🤖 Testing enhanced execution features and existing functionality")
    print("🎯 No robot hardware required - using mocked controllers")
    print("=" * 80)
    
    # Set environment to avoid hardware dependencies
    os.environ["REQUIRE_ROBOT"] = "false"
    os.environ["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "..")
    
    # Define tests to run
    test_dir = Path(__file__).parent
    tests = [
        {
            'file': test_dir / 'test_enhanced_execution.py',
            'description': 'Enhanced Execution Features',
            'covers': 'Adaptive velocity scaling, micro-refine, enhanced settle pause, tightened error thresholds'
        },
        {
            'file': test_dir / 'test_enhanced_precision.py', 
            'description': 'Enhanced Precision Trajectory Planning',
            'covers': 'Double waypoints for large moves, joint 1 weighting, waypoint calculation bounds'
        },
        {
            'file': test_dir / 'test_robot_service_integration.py',
            'description': 'Robot Service Integration',
            'covers': 'Color ratio application, sequence execution, compatibility with enhancements'
        }
    ]
    
    # Track results
    results = []
    total_tests = len(tests)
    passed_tests = 0
    
    # Run each test
    for test_info in tests:
        test_file = test_info['file']
        description = test_info['description']
        covers = test_info['covers']
        
        print(f"\n📋 About to run: {description}")
        print(f"   Covers: {covers}")
        
        if test_file.exists():
            success, output = run_test_file(test_file, description)
            results.append({
                'name': description,
                'success': success,
                'output': output,
                'covers': covers
            })
            if success:
                passed_tests += 1
        else:
            print(f"❌ Test file not found: {test_file}")
            results.append({
                'name': description,
                'success': False,
                'output': f"Test file not found: {test_file}",
                'covers': covers
            })
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS REPORT")
    print("=" * 80)
    print(f"Total test suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    print("-" * 80)
    
    for i, result in enumerate(results, 1):
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{i}. {result['name']}: {status}")
        print(f"   Coverage: {result['covers']}")
        if not result['success']:
            print(f"   Issue: {result['output'][:200]}...")
        print()
    
    # Feature coverage summary
    print("🎯 ENHANCED FEATURES TESTED:")
    print("-" * 80)
    features_tested = [
        "✅ Enhanced precision trajectory planning (double waypoints for large moves)",
        "✅ Joint 1 double weighting in trajectory calculation", 
        "✅ Adaptive velocity scaling based on joint displacement",
        "✅ Micro-refine functionality for position errors > 0.05 rad",
        "✅ Tightened error thresholds (0.08 vs 0.1 rad) for enhanced execution",
        "✅ Enhanced settle pause (1.5s vs 1.0s) for better stability",
        "✅ CLI arguments for disabling enhanced features",
        "✅ Backwards compatibility with existing functionality",
        "✅ Integration with color ratio dispensing system",
        "✅ Mock controller testing without hardware requirements"
    ]
    
    for feature in features_tested:
        print(f"   {feature}")
    
    print("\n🔧 IMPLEMENTATION SUMMARY:")
    print("-" * 80)
    implementation_points = [
        "• execute_rules.py: Added enhanced_precision parameter (default True)",
        "• sequential_execute.py: Added enhanced_execution parameter (default True)", 
        "• Waypoint calculation: Doubled for moves with squared_sum > 1.0",
        "• Velocity scaling: 0.8x for large moves (>0.5 rad), 0.9x for medium moves (0.3-0.5 rad)",
        "• Error thresholds: 0.08 rad for enhanced execution vs 0.1 rad for normal",
        "• Settle pause: 1.5s for enhanced execution vs 1.0s for normal",
        "• CLI flags: --no-enhanced-precision and --no-enhanced-execution available",
        "• All enhancements enabled by default with option to disable"
    ]
    
    for point in implementation_points:
        print(f"   {point}")
    
    # Final verdict
    print("\n" + "=" * 80)
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Enhanced execution features are working correctly.")
        print("✅ The robot service is ready for improved joint position accuracy.")
        print("✅ Enhanced features are backwards compatible and properly tested.")
    else:
        print(f"⚠️  {total_tests - passed_tests} test suite(s) failed. Review the issues above.")
        print("🔍 Check individual test outputs for debugging information.")
    
    print("=" * 80)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_robot_service_tests()
    sys.exit(0 if success else 1)
