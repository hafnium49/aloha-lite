#!/usr/bin/env python3
"""
Test runner for robot_service tests
"""
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests in the tests directory."""
    print("🤖 Robot Service Test Runner")
    print("=" * 50)
    
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found")
        return False
    
    print(f"📋 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   • {test_file.name}")
    
    print("\n🚀 Running tests...")
    success_count = 0
    
    for test_file in test_files:
        print(f"\n📝 Running {test_file.name}...")
        print("-" * 30)
        
        try:
            # Change to tests directory to run test
            original_dir = os.getcwd()
            os.chdir(tests_dir)
            
            # Execute the test file
            exit_code = os.system(f"python3 {test_file.name}")
            
            if exit_code == 0:
                print(f"✅ {test_file.name} passed")
                success_count += 1
            else:
                print(f"❌ {test_file.name} failed (exit code: {exit_code})")
            
        except Exception as e:
            print(f"❌ Error running {test_file.name}: {e}")
        finally:
            os.chdir(original_dir)
    
    print(f"\n🎉 Test Results: {success_count}/{len(test_files)} tests passed")
    return success_count == len(test_files)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
