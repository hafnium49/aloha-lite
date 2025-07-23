#!/usr/bin/env python3
"""
Verify conda environment setup for aloha-lite.
This script checks that all required dependencies are available and working.
"""

import sys
import importlib
import traceback

def test_import(module_name, description=""):
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description} - Error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - {description} - Unexpected error: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 ALOHA-Lite Environment Verification")
    print("=" * 50)
    
    # Python version check
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor == 11:
        print("✅ Python 3.11 (recommended)")
    elif python_version.major == 3 and python_version.minor >= 10:
        print("⚠️  Python version acceptable but 3.11 is recommended")
    else:
        print("❌ Python version not recommended. Please use Python 3.11")
    
    print("\n📦 Core Dependencies:")
    print("-" * 30)
    
    core_deps = [
        ("numpy", "Numerical computing"),
        ("requests", "HTTP requests"),
        ("modern_robotics", "Robotics library"),
        ("typeguard", "Type checking")
    ]
    
    core_success = all(test_import(dep, desc) for dep, desc in core_deps)
    
    print("\n🛠️  Development Dependencies:")
    print("-" * 30)
    
    dev_deps = [
        ("pytest", "Testing framework"),
        ("matplotlib", "Plotting"),
        ("pandas", "Data manipulation"),
        ("scipy", "Scientific computing"),
        ("jupyter", "Notebooks"),
        ("black", "Code formatting"),
        ("flake8", "Linting"),
        ("mypy", "Type checking")
    ]
    
    dev_success = all(test_import(dep, desc) for dep, desc in dev_deps)
    
    print("\n🌐 Web Service Dependencies:")
    print("-" * 30)
    
    web_deps = [
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("httpx", "Async HTTP client"),
        ("boto3", "AWS SDK"),
        ("prometheus_client", "Metrics"),
        ("zmq", "ZeroMQ messaging"),
        ("pydantic", "Data validation")
    ]
    
    web_success = all(test_import(dep, desc) for dep, desc in web_deps)
    
    print("\n🖼️  Vision Dependencies:")
    print("-" * 30)
    
    vision_deps = [
        ("cv2", "OpenCV computer vision")
    ]
    
    vision_success = all(test_import(dep, desc) for dep, desc in vision_deps)
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"   Core dependencies: {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"   Development tools: {'✅ PASS' if dev_success else '❌ FAIL'}")
    print(f"   Web services: {'✅ PASS' if web_success else '❌ FAIL'}")
    print(f"   Vision processing: {'✅ PASS' if vision_success else '❌ FAIL'}")
    
    overall_success = core_success and dev_success and web_success and vision_success
    
    if overall_success:
        print("\n🎉 Environment setup is complete and working!")
        print("You can now run aloha-lite development tasks.")
    else:
        print("\n⚠️  Some dependencies are missing. Please check the installation guide.")
        print("Run: conda activate aloha-lite && pip install -r ../requirements-dev.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
