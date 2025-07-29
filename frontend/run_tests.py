#!/usr/bin/env python3
"""
Test runner for frontend color optimization tests
"""

import sys
import os
import subprocess

def run_tests():
    """Run all tests in the tests directory"""
    # Get the current directory (frontend)
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(frontend_dir, 'tests')
    
    if not os.path.exists(tests_dir):
        print("❌ Tests directory not found!")
        return False
    
    print("🧪 Running frontend color optimization tests...")
    print(f"📁 Tests directory: {tests_dir}")
    
    # Find all test files
    test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]
    
    if not test_files:
        print("⚠️  No test files found!")
        return False
    
    print(f"📋 Found {len(test_files)} test file(s): {', '.join(test_files)}")
    
    # Run each test file
    all_passed = True
    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        print(f"\n{'='*60}")
        print(f"🏃 Running {test_file}...")
        print(f"{'='*60}")
        
        try:
            # Run the test file
            result = subprocess.run([sys.executable, test_path], 
                                  cwd=frontend_dir, 
                                  capture_output=False, 
                                  check=False)
            
            if result.returncode == 0:
                print(f"✅ {test_file} PASSED")
            else:
                print(f"❌ {test_file} FAILED (exit code: {result.returncode})")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests PASSED!")
    else:
        print("❌ Some tests FAILED!")
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
