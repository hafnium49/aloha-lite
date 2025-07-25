#!/usr/bin/env python3
"""
Test runner for vision bridge tests.
Provides a convenient way to run different types of tests.
"""

import os
import sys
import subprocess
import argparse

def run_unit_tests():
    """Run unit tests using pytest."""
    print("🧪 Running unit tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "test_color_checker.py", "-v"], 
                          capture_output=False)
    return result.returncode == 0

def run_api_tests():
    """Run API integration tests."""
    print("🌐 Running API tests...")
    result = subprocess.run([sys.executable, "test_color_checker_api.py"], 
                          capture_output=False)
    return result.returncode == 0

def run_multi_color_test():
    """Run multi-color dispensing test."""
    print("🎨 Running multi-color dispensing test...")
    result = subprocess.run([sys.executable, "test_multi_color.py"], 
                          capture_output=False)
    return result.returncode == 0

def run_consolidated_service_test():
    """Run consolidated service logic test."""
    print("🤖 Running consolidated service test...")
    result = subprocess.run([sys.executable, "test_consolidated_service.py"], 
                          capture_output=False)
    return result.returncode == 0

def run_sam2_tests():
    """Run SAM 2 integration tests."""
    print("🔍 Running SAM 2 integration tests...")
    
    # Run comprehensive SAM 2 integration test
    comprehensive_test = "test_sam2_integration.py"
    if os.path.exists(comprehensive_test):
        print("   Running comprehensive SAM 2 integration test...")
        result = subprocess.run([sys.executable, comprehensive_test], capture_output=False)
        if result.returncode != 0:
            print("   ❌ Comprehensive SAM 2 test failed")
            return False
        else:
            print("   ✅ Comprehensive SAM 2 test passed")
    
    # Run additional specific tests
    additional_tests = [
        ("test_sam2_final.py", "SAM 2 final integration test"),
        ("test_sam2_update.py", "SAM 2 update verification test"),
        ("test_sam_integration.py", "SAM integration compatibility test")
    ]
    
    all_passed = True
    for test_file, description in additional_tests:
        if os.path.exists(test_file):
            print(f"   Running {description}...")
            result = subprocess.run([sys.executable, test_file], capture_output=False)
            if result.returncode != 0:
                print(f"   ❌ {test_file} failed")
                all_passed = False
            else:
                print(f"   ✅ {test_file} passed")
        else:
            print(f"   ⚠️  {test_file} not found, skipping")
    
    return all_passed

def run_container_test():
    """Run direct color checker test inside container."""
    print("🐳 Running container-based test...")
    print("Note: This requires Docker services to be running.")
    
    # Copy test file to container
    copy_result = subprocess.run([
        "docker", "cp", "test_direct_color_checker.py", 
        "aloha-lite-vision-bridge-1:/tmp/test_direct_color_checker.py"
    ], capture_output=True, text=True)
    
    if copy_result.returncode != 0:
        print(f"❌ Failed to copy test file to container: {copy_result.stderr}")
        return False
    
    # Run test inside container
    exec_result = subprocess.run([
        "docker", "exec", "-it", "aloha-lite-vision-bridge-1",
        "python", "/tmp/test_direct_color_checker.py"
    ], capture_output=False)
    
    return exec_result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Run vision bridge tests")
    parser.add_argument("--type", "-t", choices=["unit", "api", "container", "multi-color", "consolidated", "sam2", "all"],
                      default="all", help="Type of tests to run")
    
    args = parser.parse_args()
    
    # Change to the tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Vision Bridge Test Runner")
    print("=" * 50)
    
    success = True
    
    if args.type in ["unit", "all"]:
        success &= run_unit_tests()
        print()
    
    if args.type in ["api", "all"]:
        success &= run_api_tests()
        print()
    
    if args.type in ["multi-color", "all"]:
        success &= run_multi_color_test()
        print()
    
    if args.type in ["consolidated", "all"]:
        success &= run_consolidated_service_test()
        print()
    
    if args.type in ["sam2", "all"]:
        success &= run_sam2_tests()
        print()
    
    if args.type == "container":
        success &= run_container_test()
        print()
    
    print("=" * 50)
    if success:
        print("✅ All selected tests completed successfully!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
