#!/usr/bin/env python3
"""
Run all frontend tests including washing bottle calibration tests.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_test_file(test_file_path, description):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, str(test_file_path)
        ], cwd=os.path.dirname(test_file_path), capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run comprehensive frontend tests."""
    print("🚀 Running All Frontend Tests with Washing Bottle Calibration")
    print("=" * 80)
    
    tests_dir = Path(__file__).parent
    results = []
    
    # Test files to run in order
    test_files = [
        ("test_all_updates.py", "Comprehensive Frontend Updates (including washing bottle status)"),
        ("test_washing_bottle_calibration.py", "Washing Bottle Calibration Functionality"),
        ("test_api_endpoints.py", "API Endpoints with 10.0 mL Normalization"),
        ("test_normalization_10.py", "10.0 mL Normalization Tests"),
    ]
    
    # Run each test file
    for test_file, description in test_files:
        test_path = tests_dir / test_file
        if test_path.exists():
            success = run_test_file(test_path, description)
            results.append((description, success))
        else:
            print(f"⚠️ Test file not found: {test_file}")
            results.append((description, False))
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    total = len(results)
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {description}")
        if success:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All frontend tests passed!")
        print("✅ Normalization updates working correctly")
        print("✅ Washing bottle calibration implemented successfully")
        print("✅ API endpoints functioning properly")
        return True
    else:
        print("❌ Some tests failed - please review the output above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
