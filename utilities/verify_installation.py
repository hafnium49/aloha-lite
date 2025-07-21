#!/usr/bin/env python3
"""
Installation verification script for ALOHA-Lite trajectory planner
"""

def verify_installation():
    """Verify that all required packages are installed and working."""
    
    print("🔍 ALOHA-Lite Installation Verification")
    print("=" * 50)
    
    # Test numpy
    try:
        import numpy as np
        print(f"✅ numpy {np.__version__} - OK")
    except ImportError as e:
        print(f"❌ numpy - FAILED: {e}")
        return False
    
    # Test requests
    try:
        import requests
        print(f"✅ requests {requests.__version__} - OK")
    except ImportError as e:
        print(f"❌ requests - FAILED: {e}")
        return False
    
    # Test ModernRobotics
    try:
        import modern_robotics as mr
        print(f"✅ modern_robotics {mr.__version__} - OK")
        
        # Test basic functionality
        test_matrix = np.eye(3)
        result = mr.RotInv(test_matrix)
        if np.allclose(result, test_matrix):
            print("  ✓ ModernRobotics basic functionality verified")
        else:
            print("  ⚠️  ModernRobotics functionality test failed")
            
    except ImportError as e:
        print(f"❌ modern_robotics - FAILED: {e}")
        print("  💡 Try: pip install modern_robotics")
        return False
    
    # Test trajectory planner
    try:
        from trajectory_planner import JointTrajectoryPlanner
        planner = JointTrajectoryPlanner()
        print("✅ trajectory_planner - OK")
    except ImportError as e:
        print(f"❌ trajectory_planner - FAILED: {e}")
        return False
    
    # Test trajectory executor
    try:
        from trajectory_executor import TrajectoryExecutor
        print("✅ trajectory_executor - OK")
    except ImportError as e:
        print(f"❌ trajectory_executor - FAILED: {e}")
        return False
    
    # Test execute_rules
    try:
        from execute_rules import PhosphobotJointController
        print("✅ execute_rules - OK")
    except ImportError as e:
        print(f"❌ execute_rules - FAILED: {e}")
        return False
    
    print("\n🎉 All components verified successfully!")
    print("\n🚀 Ready to use ALOHA-Lite trajectory planner:")
    print("   python3 trajectory_example.py")
    print("   python3 trajectory_executor.py --help")
    
    return True

if __name__ == "__main__":
    success = verify_installation()
    exit(0 if success else 1)
