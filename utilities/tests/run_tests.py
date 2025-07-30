#!/usr/bin/env python3
"""
Test runner for ground truth calibrator tests

This script runs all tests for the ground truth calibrator utility
without requiring actual robot hardware or user interaction.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests for the ground truth calibrator"""
    
    # Get the test directory
    test_dir = Path(__file__).parent
    test_file = test_dir / "test_ground_truth_calibrator.py"
    
    print("=" * 60)
    print("GROUND TRUTH CALIBRATOR TEST SUITE")
    print("=" * 60)
    print(f"Running tests from: {test_file}")
    print()
    
    # Run the tests
    try:
        result = subprocess.run([
            sys.executable, str(test_file)
        ], cwd=test_dir.parent, capture_output=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("The ground truth calibrator is working correctly.")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED!")
            print("Check the output above for details.")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_test_class(test_class_name):
    """Run a specific test class"""
    test_dir = Path(__file__).parent
    test_file = test_dir / "test_ground_truth_calibrator.py"
    
    print(f"Running test class: {test_class_name}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            f"test_ground_truth_calibrator.{test_class_name}"
        ], cwd=test_dir, capture_output=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running test class {test_class_name}: {e}")
        return False

def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run ground truth calibrator tests")
    parser.add_argument(
        "--class", 
        dest="test_class",
        help="Run specific test class (TestGroundTruthCalibrator, TestGroundTruthCalibratorIntegration, MockScenarioTests)"
    )
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List available test classes"
    )
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("Available test classes:")
        print("- TestGroundTruthCalibrator")
        print("- TestGroundTruthCalibratorIntegration") 
        print("- MockScenarioTests")
        return
    
    if args.test_class:
        success = run_specific_test_class(args.test_class)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
