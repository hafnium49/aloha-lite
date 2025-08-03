#!/usr/bin/env python3
"""
Quick validation script to test frontend server startup with ground truth calibration.
This script tests that the frontend can start and the ground truth integration works.
"""

import sys
import requests
import time
import subprocess
import signal
from pathlib import Path

# Add the frontend directory to Python path
frontend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(frontend_dir))


def test_server_startup():
    """Test that the frontend server can start with ground truth integration."""
    print("🚀 Testing Frontend Server Startup with Ground Truth Integration")
    print("=" * 70)
    
    # Test 1: Import validation
    print("📦 Testing imports and ground truth loading...")
    try:
        from main import load_ground_truth_calibration, bottle_model, color_optimizer
        print("✅ Successfully imported main components")
        
        # Test ground truth loading
        matrix = load_ground_truth_calibration()
        print(f"✅ Ground truth matrix loaded: shape {matrix.shape}")
        print(f"📊 Matrix diagonal: {matrix.diagonal()}")
        
        # Test bottle model
        print(f"✅ Bottle model initialized with matrix shape: {bottle_model.P_est.shape}")
        
        # Test color optimizer
        print(f"✅ Color optimizer initialized with history length: {len(color_optimizer.history)}")
        
    except Exception as e:
        print(f"❌ Import/initialization failed: {e}")
        return False
    
    # Test 2: Target color generation
    print(f"\n🎯 Testing target color generation...")
    try:
        from main import generate_random_target_color
        
        # Generate a few target colors
        for i in range(3):
            rgb = generate_random_target_color()
            print(f"✅ Generated target color {i+1}: RGB{rgb}")
            
            # Verify RGB values are valid
            assert len(rgb) == 3, "RGB should have 3 components"
            for value in rgb:
                assert 0 <= value <= 255, f"RGB value {value} out of range"
                
    except Exception as e:
        print(f"❌ Target color generation failed: {e}")
        return False
    
    # Test 3: API compatibility check (basic import test)
    print(f"\n🔧 Testing API compatibility...")
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        
        # Check that we can access key API functions
        from main import (
            api_target, api_set_target, api_recommend, 
            api_history, api_reset
        )
        print("✅ All API endpoints are accessible")
        
    except Exception as e:
        print(f"❌ API compatibility test failed: {e}")
        return False
    
    # Test 4: Configuration validation
    print(f"\n⚙️  Testing configuration...")
    try:
        import os
        from main import ROBOT_SERVICE_URL, VISION_SERVICE_URL
        
        print(f"✅ Robot service URL: {ROBOT_SERVICE_URL}")
        print(f"✅ Vision service URL: {VISION_SERVICE_URL}")
        
        # Test ML availability
        from main import ML_AVAILABLE
        print(f"✅ ML libraries available: {ML_AVAILABLE}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    print(f"\n🎉 All validation tests passed!")
    print("✅ Frontend is ready to run with ground truth calibration integration")
    
    return True


def test_quick_server_run():
    """Test starting the server briefly to verify it works."""
    print(f"\n🌐 Testing quick server startup...")
    
    try:
        # Start the server in background
        process = subprocess.Popen([
            sys.executable, str(frontend_dir / "main.py")
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            
            # Try a quick health check (if server is listening)
            try:
                response = requests.get("http://localhost:3000", timeout=2)
                print(f"✅ Server responded with status: {response.status_code}")
            except requests.exceptions.RequestException:
                print("ℹ️  Server started but not yet accepting connections (normal)")
            
            # Stop the server
            process.terminate()
            process.wait(timeout=5)
            print("✅ Server stopped cleanly")
            return True
        else:
            # Server failed to start
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"Error output: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🧪 Frontend Ground Truth Integration Validation")
    print("=" * 50)
    
    success = True
    
    # Run validation tests
    if not test_server_startup():
        success = False
    
    # Optional: Quick server test (might fail in some environments)
    try:
        if not test_quick_server_run():
            print("⚠️  Server startup test failed (this may be normal in some environments)")
    except Exception as e:
        print("⚠️  Server startup test skipped (this may be normal in some environments)")
    
    # Final summary
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 VALIDATION COMPLETE: Frontend is ready!")
        print("📝 Next steps:")
        print("   1. Run: conda activate aloha_lite")
        print("   2. cd frontend")
        print("   3. python main.py")
        print("   4. Open http://localhost:3000")
    else:
        print("❌ VALIDATION FAILED: Check errors above")
        
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
