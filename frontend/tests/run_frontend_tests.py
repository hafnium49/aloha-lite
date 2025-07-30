#!/usr/bin/env python3
"""
Test runner for frontend ground truth calibration tests.

Usage:
    python run_frontend_tests.py              # Run all tests
    python run_frontend_tests.py -v           # Run with verbose output
    python run_frontend_tests.py TestClass    # Run specific test class
"""

import sys
import os
import unittest
from pathlib import Path

# Add the frontend directory to the path
frontend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(frontend_dir))

# Import test modules
from tests.test_ground_truth_calibration import (
    TestGroundTruthCalibration,
    TestColorOptimizationIntegration,
    TestEndToEndIntegration
)

def main():
    """Main test runner function."""
    # Parse command line arguments
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    
    # Check if specific test class is requested
    test_class_name = None
    for arg in sys.argv[1:]:
        if not arg.startswith('-') and arg != 'run_frontend_tests.py':
            test_class_name = arg
            break
    
    # Create test suite
    if test_class_name:
        # Run specific test class
        test_classes = {
            'TestGroundTruthCalibration': TestGroundTruthCalibration,
            'TestColorOptimizationIntegration': TestColorOptimizationIntegration,
            'TestEndToEndIntegration': TestEndToEndIntegration
        }
        
        if test_class_name in test_classes:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_classes[test_class_name])
            print(f"Running tests from {test_class_name}...")
        else:
            print(f"Unknown test class: {test_class_name}")
            print(f"Available classes: {', '.join(test_classes.keys())}")
            return 1
    else:
        # Run all tests
        suite = unittest.TestSuite()
        test_classes = [
            TestGroundTruthCalibration,
            TestColorOptimizationIntegration,
            TestEndToEndIntegration
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        print("Running all ground truth calibration tests...")
    
    # Run tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 GROUND TRUTH CALIBRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"📈 Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            # Print first line of failure message
            failure_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            if failure_msg:
                print(f"   → {failure_msg}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            # Print error type and message
            error_lines = traceback.strip().split('\n')
            if error_lines:
                error_msg = error_lines[-1] if error_lines[-1] else error_lines[-2]
                print(f"   → {error_msg}")
    
    if result.wasSuccessful():
        print(f"\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == '__main__':
    exit(main())
