#!/usr/bin/env python3
"""
Quick test to verify the test setup is working correctly
"""

import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Test that we can import the required modules"""
    try:
        from main import ColorOptimizer
        print("✅ Successfully imported ColorOptimizer from main.py")
        
        # Test basic functionality
        optimizer = ColorOptimizer()
        optimizer.set_target_color((255, 0, 0))
        ratios = optimizer.recommend_next_ratios()
        
        print(f"✅ Basic functionality test passed")
        print(f"   Target: RGB(255, 0, 0)")
        print(f"   Phase 0 recommendation: {ratios}")
        
        # Verify it's pure dominant (red should be 3.0, others 0.0)
        if ratios['red'] == 3.0 and ratios['yellow'] == 0.0 and ratios['blue'] == 0.0:
            print("✅ Phase 0 dominant pigment strategy working correctly")
            return True
        else:
            print("❌ Phase 0 strategy not working as expected")
            return False
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running quick setup verification test...")
    print(f"📁 Running from: {os.getcwd()}")
    print(f"📂 Tests directory: {os.path.dirname(__file__)}")
    print(f"📂 Frontend directory: {os.path.dirname(os.path.dirname(__file__))}")
    
    success = test_imports()
    
    if success:
        print("\n🎉 Test setup verification PASSED!")
        print("   You can now run: python test_optimization.py")
    else:
        print("\n❌ Test setup verification FAILED!")
        print("   Check your Python path and main.py location")
    
    exit(0 if success else 1)
