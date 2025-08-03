#!/usr/bin/env python3
"""
Test runner for frontend color optimization tests
Runs all tests in the current tests directory
"""

import sys
import os
import subprocess

def run_tests():
    """Run all tests in the current tests directory"""
    # Get the current directory (tests)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.dirname(tests_dir)  # Parent directory (frontend)
    
    print("🧪 Running frontend color optimization tests...")
    print(f"📁 Tests directory: {tests_dir}")
    print(f"📁 Frontend directory: {frontend_dir}")
    
    # Find all test files in current directory
    test_files = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]
    
    if not test_files:
        print("⚠️  No test files found!")
        return False
    
    print(f"📋 Found {len(test_files)} test file(s): {', '.join(test_files)}")
    
    # Prioritize core optimization tests first
    priority_tests = [
        'test_hue_optimization.py',
        'test_4_pigment_system.py', 
        'test_4_pigment_api.py',
        'test_optimization.py',
        'test_color_space.py'
    ]
    
    # Order tests with priority ones first
    ordered_tests = []
    for priority_test in priority_tests:
        if priority_test in test_files:
            ordered_tests.append(priority_test)
            test_files.remove(priority_test)
    
    # Add remaining tests
    ordered_tests.extend(sorted(test_files))
    
    print(f"🔄 Test execution order: {', '.join(ordered_tests)}")
    
    # Run each test file
    all_passed = True
    passed_count = 0
    failed_count = 0
    
    for test_file in ordered_tests:
        test_path = os.path.join(tests_dir, test_file)
        print(f"\n{'='*60}")
        print(f"🏃 Running {test_file}...")
        print(f"{'='*60}")
        
        try:
            # Run the test file with Python from tests directory context
            result = subprocess.run([sys.executable, test_path], 
                                  cwd=tests_dir,  # Run from tests directory
                                  capture_output=False, 
                                  check=False)
            
            if result.returncode == 0:
                print(f"✅ {test_file} PASSED")
                passed_count += 1
            else:
                print(f"❌ {test_file} FAILED (exit code: {result.returncode})")
                failed_count += 1
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            failed_count += 1
            all_passed = False
    
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(ordered_tests)}")
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("🎨 4-pigment hue-based optimization system is working correctly!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Check the failed tests above for details")
    print(f"{'='*60}")
    
    return all_passed

def run_specific_test_category():
    """Run specific categories of tests"""
    print("🎯 Available test categories:")
    print("1. Hue optimization tests (CIELAB color space)")
    print("2. 4-pigment system tests (white solvent)")
    print("3. API endpoint tests (FastAPI)")
    print("4. Integration tests (frontend-backend)")
    print("5. All tests (comprehensive)")
    
    choice = input("\nSelect category (1-5) or press Enter for all: ").strip()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    category_map = {
        '1': ['test_hue_optimization.py'],
        '2': ['test_4_pigment_system.py'],
        '3': ['test_4_pigment_api.py'],
        '4': ['test_frontend_integration.py', 'test_integration_simulation.py'],
        '5': None  # All tests
    }
    
    if choice in category_map:
        if choice == '5' or not choice:
            return run_tests()  # Run all tests
        
        target_tests = category_map[choice]
        available_tests = [f for f in os.listdir(tests_dir) if f.startswith('test_') and f.endswith('.py')]
        
        tests_to_run = [t for t in target_tests if t in available_tests]
        
        if not tests_to_run:
            print(f"❌ No tests found for category {choice}")
            return False
        
        print(f"\n🏃 Running {len(tests_to_run)} test(s) from category {choice}...")
        
        all_passed = True
        for test_file in tests_to_run:
            test_path = os.path.join(tests_dir, test_file)
            print(f"\n{'='*40}")
            print(f"🏃 Running {test_file}...")
            print(f"{'='*40}")
            
            try:
                result = subprocess.run([sys.executable, test_path], 
                                      cwd=tests_dir,
                                      capture_output=False, 
                                      check=False)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} PASSED")
                else:
                    print(f"❌ {test_file} FAILED")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                all_passed = False
        
        return all_passed
    else:
        print("❌ Invalid choice. Running all tests...")
        return run_tests()

if __name__ == "__main__":
    print("🚀 Frontend Color Optimization Test Runner")
    print("🎨 4-Pigment Hue-Based System")
    print("=" * 80)
    
    # Check if user wants specific category
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        success = run_specific_test_category()
    else:
        success = run_tests()
    
    exit(0 if success else 1)
    success = run_tests()
    exit(0 if success else 1)
