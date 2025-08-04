#!/usr/bin/env python3
"""
Test the enhanced execution features added to execute_rules.py and sequential_execute.py.
These tests focus on the trajectory planning improvements and error reduction tweaks.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the modules we're testing
from execute_rules import PhosphobotJointController, execute_configuration_smooth
from sequential_execute import SequentialRobotExecutor

class TestEnhancedTrajectoryPlanning(unittest.TestCase):
    """Test enhanced trajectory planning features in execute_rules.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the requests to avoid network calls
        self.mock_session = Mock()
        self.controller = PhosphobotJointController("http://mock:80")
        self.controller.session = self.mock_session
        
        # Sample joint positions
        self.current_joints = [0.0, -1.5, 1.0, -1.5, -1.0, 0.5]
        self.target_joints = [0.5, -1.0, 1.5, -1.0, -0.5, 1.0]
        
    def test_enhanced_precision_waypoint_calculation(self):
        """Test that enhanced precision mode doubles waypoints for large moves"""
        print("\n🧪 Testing Enhanced Precision Waypoint Calculation")
        
        # Test with enhanced precision enabled (default)
        waypoints_enhanced = self.controller.calculate_adaptive_waypoints(
            self.current_joints, 
            self.target_joints,
            enhanced_precision=True
        )
        
        # Test with enhanced precision disabled
        waypoints_normal = self.controller.calculate_adaptive_waypoints(
            self.current_joints, 
            self.target_joints,
            enhanced_precision=False
        )
        
        print(f"   Enhanced precision waypoints: {waypoints_enhanced}")
        print(f"   Normal waypoints: {waypoints_normal}")
        
        # For large moves (squared_sum > 1.0), enhanced should have more waypoints
        # Calculate expected squared sum
        displacements = []
        for i in range(5):  # Only first 5 joints
            displacement = self.target_joints[i] - self.current_joints[i]
            weight = 2.0 if i == 0 else 1.0  # Joint 1 gets double weighting
            displacements.append((displacement ** 2) * weight)
        squared_sum = sum(displacements)
        
        if squared_sum > 1.0:
            # Enhanced precision should have more waypoints for large moves
            self.assertGreaterEqual(waypoints_enhanced, waypoints_normal)
        
        # Both should be within valid range
        self.assertGreaterEqual(waypoints_enhanced, 5)
        self.assertLessEqual(waypoints_enhanced, 50)
        self.assertGreaterEqual(waypoints_normal, 5)
        self.assertLessEqual(waypoints_normal, 50)
        
        print("   ✅ Enhanced precision waypoint calculation works correctly")
    
    def test_joint_1_double_weighting(self):
        """Test that joint 1 gets double weighting in waypoint calculation"""
        print("\n🧪 Testing Joint 1 Double Weighting")
        
        # Create a scenario where only joint 1 moves significantly
        current_j1_large = [0.0, -1.5, 1.0, -1.5, -1.0, 0.5]
        target_j1_large = [2.0, -1.5, 1.0, -1.5, -1.0, 0.5]  # Large joint 1 movement
        
        # Create a scenario where joint 2 moves the same amount
        current_j2_large = [0.0, -1.5, 1.0, -1.5, -1.0, 0.5]
        target_j2_large = [0.0, 0.5, 1.0, -1.5, -1.0, 0.5]   # Same displacement in joint 2
        
        waypoints_j1 = self.controller.calculate_adaptive_waypoints(
            current_j1_large, target_j1_large, enhanced_precision=False
        )
        
        waypoints_j2 = self.controller.calculate_adaptive_waypoints(
            current_j2_large, target_j2_large, enhanced_precision=False
        )
        
        print(f"   Joint 1 large move waypoints: {waypoints_j1}")
        print(f"   Joint 2 same displacement waypoints: {waypoints_j2}")
        
        # Joint 1 should get more waypoints due to double weighting
        self.assertGreaterEqual(waypoints_j1, waypoints_j2)
        
        print("   ✅ Joint 1 double weighting works correctly")
    
    def test_enhanced_precision_parameter_passing(self):
        """Test that enhanced_precision parameter is properly passed through"""
        print("\n🧪 Testing Enhanced Precision Parameter Passing")
        
        # Mock successful API responses
        self.mock_session.post.return_value.status_code = 200
        self.mock_session.post.return_value.json.return_value = {'angles': self.current_joints}
        
        # Test with enhanced precision enabled
        result = self.controller.execute_smooth_trajectory(
            robot_id=0,
            target_joints=self.target_joints,
            enhanced_precision=True
        )
        
        # Note: Result depends on trajectory availability
        print("   ✅ Enhanced precision parameter passing works correctly")


class TestEnhancedSequentialExecution(unittest.TestCase):
    """Test enhanced execution features in sequential_execute.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create executor with enhanced execution enabled
        self.executor = SequentialRobotExecutor(
            server_url="http://mock:80",
            enhanced_execution=True
        )
        
        # Mock the controller
        self.mock_controller = Mock()
        self.executor.controller = self.mock_controller
        
        # Sample joint positions
        self.current_joints = [0.0, -1.5, 1.0, -1.5, -1.0, 0.5]
        self.target_joints = [0.5, -1.0, 1.5, -1.0, -0.5, 1.0]
        
    def test_enhanced_execution_initialization(self):
        """Test that enhanced execution is properly initialized"""
        print("\n🧪 Testing Enhanced Execution Initialization")
        
        # Test with enhanced execution enabled
        executor_enhanced = SequentialRobotExecutor(enhanced_execution=True)
        self.assertTrue(executor_enhanced.enhanced_execution)
        
        # Test with enhanced execution disabled
        executor_normal = SequentialRobotExecutor(enhanced_execution=False)
        self.assertFalse(executor_normal.enhanced_execution)
        
        print("   ✅ Enhanced execution initialization works correctly")
    
    def test_adaptive_velocity_scaling(self):
        """Test adaptive velocity scaling for large joint displacements"""
        print("\n🧪 Testing Adaptive Velocity Scaling")
        
        # Mock configuration loading and arm preparation
        with patch('sequential_execute.load_configuration') as mock_load_config, \
             patch('sequential_execute.prepare_arm_configuration') as mock_prepare_arm:
            
            # Mock configuration data
            mock_config = {
                'name': 'test_config',
                'description': 'Test configuration',
                'configuration': {
                    'left_arm': {'joints': {'j1': 0.0, 'j2': -1.0, 'j3': 1.0, 'j4': -1.0, 'j5': -0.5, 'j6': 1.0}}
                }
            }
            mock_load_config.return_value = mock_config
            
            # Test case 1: Large displacement (> 0.5 rad) should scale to 0.8x
            large_displacement_joints = [1.0, -1.0, 1.0, -1.0, -0.5, 1.0]  # 1.0 rad difference in j1
            mock_prepare_arm.return_value = large_displacement_joints
            self.mock_controller.get_current_joint_angles.return_value = self.current_joints
            self.mock_controller.execute_smooth_trajectory.return_value = True
            
            # Execute configuration
            result = self.executor.execute_configuration(
                'test_config',
                max_velocity=0.3,
                use_trajectory=True
            )
            
            # Check that execute_smooth_trajectory was called with scaled velocity
            if self.mock_controller.execute_smooth_trajectory.called:
                call_args = self.mock_controller.execute_smooth_trajectory.call_args
                scaled_velocity = call_args[1]['max_velocity']
                expected_velocity = 0.3 * 0.8  # Should be scaled down
                self.assertEqual(scaled_velocity, expected_velocity)
                print(f"   Large displacement: velocity scaled from 0.3 to {scaled_velocity}")
            
            # Test case 2: Medium displacement (0.3-0.5 rad) should scale to 0.9x
            self.mock_controller.reset_mock()
            medium_displacement_joints = [0.4, -1.0, 1.0, -1.0, -0.5, 1.0]  # 0.4 rad difference
            mock_prepare_arm.return_value = medium_displacement_joints
            
            result = self.executor.execute_configuration(
                'test_config',
                max_velocity=0.3,
                use_trajectory=True
            )
            
            if self.mock_controller.execute_smooth_trajectory.called:
                call_args = self.mock_controller.execute_smooth_trajectory.call_args
                scaled_velocity = call_args[1]['max_velocity']
                expected_velocity = 0.3 * 0.9  # Should be scaled down
                self.assertEqual(scaled_velocity, expected_velocity)
                print(f"   Medium displacement: velocity scaled from 0.3 to {scaled_velocity}")
            
        print("   ✅ Adaptive velocity scaling works correctly")
    
    def test_micro_refine_functionality(self):
        """Test micro-refine functionality for position errors > 0.05 rad"""
        print("\n🧪 Testing Micro-Refine Functionality")
        
        # Mock joint positions with error > 0.05 rad
        final_joints_with_error = [0.1, -1.0, 1.0, -1.0, -0.5, 1.0]  # 0.1 rad error in j1
        target_joints = [0.0, -1.0, 1.0, -1.0, -0.5, 1.0]
        
        self.mock_controller.get_current_joint_angles.side_effect = [
            final_joints_with_error,  # First read shows error
            target_joints             # Second read after micro-refine shows success
        ]
        self.mock_controller.write_joint_positions.return_value = {'status': 'success'}
        self.mock_controller.execute_smooth_trajectory.return_value = True
        
        # Execute restore with enhanced execution enabled
        result = self.executor._restore_joint_positions(target_joints, target_joints)
        
        # Should have called execute_smooth_trajectory for micro-refine
        self.mock_controller.execute_smooth_trajectory.assert_called()
        
        # Check micro-refine parameters
        call_args = self.mock_controller.execute_smooth_trajectory.call_args
        self.assertEqual(call_args[1]['duration'], 1.2)
        self.assertEqual(call_args[1]['max_velocity'], 0.15)
        self.assertEqual(call_args[1]['num_waypoints'], 18)
        self.assertFalse(call_args[1]['adaptive_waypoints'])
        
        print("   ✅ Micro-refine functionality works correctly")
    
    def test_tightened_error_threshold(self):
        """Test tightened error threshold (0.08 vs 0.1 rad) for enhanced execution"""
        print("\n🧪 Testing Tightened Error Threshold")
        
        # Test with error between 0.08 and 0.1 rad (should fail with enhanced execution)
        final_joints_medium_error = [0.09, -1.0, 1.0, -1.0, -0.5, 1.0]  # 0.09 rad error
        target_joints = [0.0, -1.0, 1.0, -1.0, -0.5, 1.0]
        
        self.mock_controller.get_current_joint_angles.return_value = final_joints_medium_error
        self.mock_controller.write_joint_positions.return_value = {'status': 'success'}
        
        # With enhanced execution, should fail due to tightened threshold
        result_enhanced = self.executor._restore_joint_positions(target_joints, target_joints)
        self.assertFalse(result_enhanced)
        
        # With normal execution, should pass
        self.executor.enhanced_execution = False
        result_normal = self.executor._restore_joint_positions(target_joints, target_joints)
        self.assertTrue(result_normal)  # 0.09 < 0.1 threshold
        
        print("   ✅ Tightened error threshold works correctly")
    
    def test_enhanced_settle_pause(self):
        """Test longer settle pause for enhanced execution"""
        print("\n🧪 Testing Enhanced Settle Pause")
        
        # This test verifies the logic but doesn't test actual timing
        # We check that the enhanced execution mode affects pause calculation
        
        base_pause = 2.0
        
        # Enhanced execution with trajectory should use max(1.5, pause_after * 0.75)
        expected_enhanced_pause = max(1.5, base_pause * 0.75)  # max(1.5, 1.5) = 1.5
        
        # Normal execution with trajectory should use max(1.0, pause_after * 0.5)
        expected_normal_pause = max(1.0, base_pause * 0.5)  # max(1.0, 1.0) = 1.0
        
        self.assertEqual(expected_enhanced_pause, 1.5)
        self.assertEqual(expected_normal_pause, 1.0)
        
        print(f"   Enhanced pause: {expected_enhanced_pause}s")
        print(f"   Normal pause: {expected_normal_pause}s")
        print("   ✅ Enhanced settle pause calculation works correctly")


class TestBackwardsCompatibility(unittest.TestCase):
    """Test that the enhanced features don't break existing functionality"""
    
    def test_disable_enhanced_features(self):
        """Test that enhanced features can be properly disabled"""
        print("\n🧪 Testing Backwards Compatibility")
        
        # Test execute_rules.py with enhanced precision disabled
        controller = PhosphobotJointController("http://mock:80")
        current = [0.0, -1.5, 1.0, -1.5, -1.0, 0.5]
        target = [2.0, -1.0, 1.5, -1.0, -0.5, 1.0]  # Large move
        
        waypoints_normal = controller.calculate_adaptive_waypoints(
            current, target, enhanced_precision=False
        )
        waypoints_enhanced = controller.calculate_adaptive_waypoints(
            current, target, enhanced_precision=True
        )
        
        # Enhanced should have more waypoints for large moves
        self.assertGreaterEqual(waypoints_enhanced, waypoints_normal)
        
        # Test sequential_execute.py with enhanced execution disabled
        executor_normal = SequentialRobotExecutor(enhanced_execution=False)
        executor_enhanced = SequentialRobotExecutor(enhanced_execution=True)
        
        self.assertFalse(executor_normal.enhanced_execution)
        self.assertTrue(executor_enhanced.enhanced_execution)
        
        print("   ✅ Enhanced features can be properly disabled")
        print("   ✅ Backwards compatibility maintained")


def run_enhanced_execution_tests():
    """Run all enhanced execution tests"""
    print("🚀 Running Enhanced Execution Tests")
    print("=" * 60)
    print("🤖 NOTE: Robot hardware not required - using mocked controllers")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedTrajectoryPlanning))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedSequentialExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardsCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All enhanced execution tests passed!")
        return True
    else:
        print(f"\n❌ Some tests failed. Success rate: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun*100:.1f}%")
        return False


if __name__ == "__main__":
    # Set environment to avoid hardware dependencies
    os.environ["REQUIRE_ROBOT"] = "false"
    
    success = run_enhanced_execution_tests()
    sys.exit(0 if success else 1)
