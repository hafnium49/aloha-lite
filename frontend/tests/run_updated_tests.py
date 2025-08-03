#!/usr/bin/env python3
"""
Comprehensive test runner for updated frontend functionality.

Runs all tests to verify:
1. 4-pigment system functionality
2. Hue-only optimization (CIELAB color space)
3. API endpoints with new optimization
4. Color space handling
5. Ground truth calibration updates
"""

import sys
import os
import subprocess
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_test_file(test_file, description):
    """Run a specific test file and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📁 File: {test_file}")
    print('='*60)
    
    try:
        # Run the test file
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print("❌ STDERR:")
            print(result.stderr)
        
        success = result.returncode == 0
        if success:
            print(f"✅ {description} - PASSED")
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
        
        return success
        
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all updated frontend tests."""
    print("🎨 ALOHA-LITE FRONTEND COMPREHENSIVE TEST SUITE")
    print("Testing updated 4-pigment hue-based optimization system")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test suite
    tests = [
        ("test_hue_optimization.py", "Hue-Only Optimization System (NEW)"),
        ("test_4_pigment_system.py", "4-Pigment System Functionality"),
        ("test_4_pigment_api.py", "4-Pigment API Endpoints"),
        ("test_optimization.py", "Updated Phase-Based Optimization"),
        ("test_color_space.py", "Color Space Functionality"),
        ("test_ground_truth_calibration.py", "Ground Truth Calibration"),
    ]
    
    # Track results
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    # Run each test
    for test_file, description in tests:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        
        if os.path.exists(test_path):
            success = run_test_file(test_path, description)
            results[description] = success
            if success:
                passed_tests += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[description] = False
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 COMPREHENSIVE TEST RESULTS SUMMARY")
    print('='*80)
    
    print(f"🎯 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📊 Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    print(f"\n📝 Detailed Results:")
    for description, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {description}")
    
    # Key functionality verification
    print(f"\n🔍 Key Functionality Verification:")
    
    hue_optimization = results.get("Hue-Only Optimization System (NEW)", False)
    four_pigment = results.get("4-Pigment System Functionality", False)
    api_endpoints = results.get("4-Pigment API Endpoints", False)
    optimization = results.get("Updated Phase-Based Optimization", False)
    
    if hue_optimization:
        print("   ✅ Hue-based optimization (CIELAB color space) working")
    else:
        print("   ❌ Hue-based optimization issues detected")
    
    if four_pigment:
        print("   ✅ 4-pigment system (red, yellow, blue, white) operational")
    else:
        print("   ❌ 4-pigment system issues detected")
    
    if api_endpoints:
        print("   ✅ API endpoints returning 4-pigment ratios with hue optimization")
    else:
        print("   ❌ API endpoint issues detected")
    
    if optimization:
        print("   ✅ Phase-based optimization with updated schedule working")
    else:
        print("   ❌ Optimization system issues detected")
    
    # Overall assessment
    critical_tests = [hue_optimization, four_pigment, api_endpoints]
    critical_passed = sum(critical_tests)
    
    print(f"\n🏆 OVERALL ASSESSMENT:")
    if critical_passed == len(critical_tests):
        print("   🎉 ALL CRITICAL SYSTEMS OPERATIONAL")
        print("   📱 Frontend ready for hue-based color optimization")
        print("   🧪 4-pigment mixing system fully functional")
        overall_success = True
    elif critical_passed >= 2:
        print("   ⚠️  MOSTLY FUNCTIONAL - Some issues need attention")
        print("   🔧 Core systems working but optimization needed")
        overall_success = False
    else:
        print("   ❌ CRITICAL ISSUES DETECTED")
        print("   🚨 Major functionality problems need immediate attention")
        overall_success = False
    
    print(f"\n🕐 Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
