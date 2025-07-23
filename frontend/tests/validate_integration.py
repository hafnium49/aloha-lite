#!/usr/bin/env python3
"""
Integration Validation Script

Validates that the robot_service/main.py and frontend/index.html
have the correct beaker analysis integration code.
"""

import os
import re

def validate_robot_service():
    """Validate robot service integration"""
    robot_service_path = "/home/hafnium/aloha-lite/robot_service/main.py"
    
    print("🤖 Validating robot_service/main.py...")
    
    if not os.path.exists(robot_service_path):
        print("   ❌ robot_service/main.py not found")
        return False
    
    with open(robot_service_path, 'r') as f:
        content = f.read()
    
    checks = [
        ("beaker_analysis_results field", r"beaker_analysis_results.*Optional\[Dict\]"),
        ("parse_beaker_analysis_results function", r"def parse_beaker_analysis_results"),
        ("beaker-analysis endpoint", r"@app\.get.*beaker-analysis"),
        ("execute_special_function with cmd_id", r"def execute_special_function.*cmd_id"),
        ("beaker analysis result storage", r"tasks\[cmd_id\]\.beaker_analysis_results"),
    ]
    
    all_passed = True
    for check_name, pattern in checks:
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_passed = False
    
    return all_passed

def validate_frontend():
    """Validate frontend integration"""
    frontend_path = "/home/hafnium/aloha-lite/frontend/index.html"
    
    print("\n🌐 Validating frontend/index.html...")
    
    if not os.path.exists(frontend_path):
        print("   ❌ frontend/index.html not found")
        return False
    
    with open(frontend_path, 'r') as f:
        content = f.read()
    
    checks = [
        ("beaker analysis section", r"beaker-analysis"),
        ("displayAnalysisResults function", r"function displayAnalysisResults"),
        ("beaker analysis detection", r"beaker_analysis_results"),
        ("beaker-analysis endpoint call", r"beaker-analysis"),
        ("analysis results display", r"analysis-results"),
        ("color percentages display", r"color.*percentages"),
    ]
    
    all_passed = True
    for check_name, pattern in checks:
        if re.search(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE):
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_passed = False
    
    return all_passed

def validate_test_infrastructure():
    """Validate test infrastructure"""
    print("\n🧪 Validating test infrastructure...")
    
    test_files = [
        "/home/hafnium/aloha-lite/robot_service/tests/test_beaker_integration.html",
        "/home/hafnium/aloha-lite/robot_service/tests/serve_tests.py",
        "/home/hafnium/aloha-lite/robot_service/tests/README.md",
        "/home/hafnium/aloha-lite/frontend/tests/mock_robot_service.py",
        "/home/hafnium/aloha-lite/frontend/tests/integration_test_server.py",
        "/home/hafnium/aloha-lite/frontend/tests/simple_test.py",
        "/home/hafnium/aloha-lite/frontend/tests/test_integration_simulation.py",
        "/home/hafnium/aloha-lite/frontend/tests/validate_integration.py",
        "/home/hafnium/aloha-lite/frontend/tests/INTEGRATION_TEST_RESULTS.md",
    ]
    
    all_exist = True
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"   ✅ {os.path.basename(test_file)}")
        else:
            print(f"   ❌ {os.path.basename(test_file)}")
            all_exist = False
    
    return all_exist

def main():
    print("🔍 Integration Validation Report")
    print("=" * 50)
    
    robot_ok = validate_robot_service()
    frontend_ok = validate_frontend()
    tests_ok = validate_test_infrastructure()
    
    print("\n📊 Summary:")
    print(f"   Robot Service: {'✅ PASS' if robot_ok else '❌ FAIL'}")
    print(f"   Frontend:      {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"   Tests:         {'✅ PASS' if tests_ok else '❌ FAIL'}")
    
    if robot_ok and frontend_ok and tests_ok:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("   The integration is ready for testing.")
        print()
        print("🚀 Next Steps:")
        print("   1. Install dependencies: pip install -r robot_service/requirements.txt")
        print("   2. Start robot service: cd robot_service && python3 main.py")
        print("   3. Open frontend in browser: frontend/index.html")
        print("   4. Test beaker analysis integration!")
    else:
        print("\n⚠️  Some validations failed. Please check the implementation.")
    
    return robot_ok and frontend_ok and tests_ok

if __name__ == '__main__':
    main()
