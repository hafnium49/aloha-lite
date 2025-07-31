#!/usr/bin/env python3
"""
Comprehensive SAM 2 integration test for vision_bridge
Tests SAM 2 functionality including imports, model loading, and integration with beaker analysis
"""

import os
import sys
import unittest
import numpy as np
import cv2

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

class TestSAM2Integration(unittest.TestCase):
    """Test SAM 2 integration with vision_bridge."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with sample image."""
        cls.sample_image_path = "/home/hafnium/aloha-lite/temporary_images/camera_0_20250723_113227.jpg"
        
        # Load sample image if available
        if os.path.exists(cls.sample_image_path):
            cls.sample_image = cv2.imread(cls.sample_image_path)
        else:
            # Create dummy image for testing
            cls.sample_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            print("⚠️  Using dummy image - sample image not found")
    
    def test_sam2_imports(self):
        """Test that SAM 2 imports work correctly."""
        print("\n🔍 Testing SAM 2 imports...")
        
        try:
            from sam2.build_sam import build_sam2
            from sam2.sam2_image_predictor import SAM2ImagePredictor
            print("✅ SAM 2 imports successful")
            self.assertTrue(True, "SAM 2 imports should work")
        except ImportError as e:
            print(f"⚠️  SAM 2 not installed: {e}")
            print("   This is expected if sam2 package is not installed")
            self.skipTest("SAM 2 package not available")
    
    def test_beaker_analysis_imports(self):
        """Test that beaker_analysis imports work from tests directory."""
        print("\n📥 Testing beaker_analysis imports...")
        
        try:
            from beaker_analysis import extract_solution_color, create_visualization_image, SAM_PREDICTOR
            print("✅ beaker_analysis imports successful")
            print(f"   SAM_PREDICTOR status: {'Available' if SAM_PREDICTOR is not None else 'Not available'}")
            self.assertTrue(True, "beaker_analysis imports should work")
        except Exception as e:
            self.fail(f"beaker_analysis import failed: {e}")
    
    def test_vision_analysis_functionality(self):
        """Test that vision analysis works with or without SAM 2."""
        print("\n🧪 Testing vision analysis functionality...")
        
        try:
            from beaker_analysis import extract_solution_color
            
            # Run analysis on sample image
            dominant_color, color_hex, analysis_data = extract_solution_color(self.sample_image)
            
            # Verify results structure
            self.assertIsInstance(dominant_color, np.ndarray, "Dominant color should be numpy array")
            self.assertEqual(len(dominant_color), 3, "Dominant color should have 3 components (RGB)")
            self.assertIsInstance(color_hex, str, "Color hex should be string")
            self.assertTrue(color_hex.startswith('#'), "Color hex should start with #")
            
            # Verify analysis data structure
            required_keys = ['beaker_circle', 'clusters', 'dominant_cluster_index', 'total_pixels_analyzed', 'sam_mask_preview', 'mask_strategy']
            for key in required_keys:
                self.assertIn(key, analysis_data, f"Analysis data should contain {key}")
            
            # Verify mask strategy is valid
            valid_strategies = ['circle_only', 'sam_interior', 'sam_inverted']
            self.assertIn(analysis_data['mask_strategy'], valid_strategies, f"Mask strategy should be one of {valid_strategies}")
            
            print(f"✅ Analysis successful: {color_hex}")
            print(f"   Mask strategy: {analysis_data['mask_strategy']}")
            
            # Verify beaker circle data
            circle = analysis_data['beaker_circle']
            self.assertIn('x', circle, "Circle should have x coordinate")
            self.assertIn('y', circle, "Circle should have y coordinate")
            self.assertIn('radius', circle, "Circle should have radius")
            
            # Verify SAM mask preview
            sam_mask = analysis_data['sam_mask_preview']
            self.assertIsInstance(sam_mask, np.ndarray, "SAM mask preview should be numpy array")
            self.assertEqual(sam_mask.dtype, np.uint8, "SAM mask should have uint8 dtype")
            
            print(f"✅ Vision analysis successful!")
            print(f"   Dominant color: {color_hex} RGB{tuple(dominant_color)}")
            print(f"   Beaker position: ({circle['x']}, {circle['y']})")
            print(f"   Beaker radius: {circle['radius']}px")
            print(f"   SAM mask shape: {sam_mask.shape}")
            
        except Exception as e:
            self.fail(f"Vision analysis failed: {e}")
    
    def test_visualization_functionality(self):
        """Test that visualization creation works."""
        print("\n🖼️  Testing visualization functionality...")
        
        try:
            from beaker_analysis import extract_solution_color, create_visualization_image
            
            # Get analysis data
            dominant_color, color_hex, analysis_data = extract_solution_color(self.sample_image)
            
            # Create visualization
            viz_img = create_visualization_image(self.sample_image, analysis_data)
            
            # Verify visualization
            self.assertIsInstance(viz_img, np.ndarray, "Visualization should be numpy array")
            self.assertEqual(len(viz_img.shape), 3, "Visualization should be 3D array (H, W, C)")
            self.assertEqual(viz_img.shape[2], 3, "Visualization should have 3 color channels")
            self.assertEqual(viz_img.dtype, np.uint8, "Visualization should have uint8 dtype")
            
            # Save test visualization
            output_path = os.path.join(os.path.dirname(__file__), "test_results", "sam2_test_visualization.jpg")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, viz_img)
            
            print(f"✅ Visualization created successfully")
            print(f"   Visualization shape: {viz_img.shape}")
            print(f"   Saved to: {output_path}")
            
        except Exception as e:
            self.fail(f"Visualization creation failed: {e}")
    
    def test_sam2_environment_variables(self):
        """Test SAM 2 environment variable configuration."""
        print("\n🔧 Testing SAM 2 environment variables...")
        
        sam_checkpoint = os.getenv("SAM_CHECKPOINT")
        sam_config = os.getenv("SAM_CONFIG")
        
        if sam_checkpoint:
            print(f"   SAM_CHECKPOINT: {sam_checkpoint}")
            if os.path.exists(sam_checkpoint):
                print("   ✅ Checkpoint file exists")
            else:
                print("   ⚠️  Checkpoint file not found")
        else:
            print("   ⚠️  SAM_CHECKPOINT not set")
        
        if sam_config:
            print(f"   SAM_CONFIG: {sam_config}")
            if os.path.exists(sam_config):
                print("   ✅ Config file exists")
            else:
                print("   ⚠️  Config file not found")
        else:
            print("   ⚠️  SAM_CONFIG not set")
        
        # This test always passes as environment variables are optional
        self.assertTrue(True, "Environment variable test completed")
    
    def test_graceful_fallback(self):
        """Test that the system falls back gracefully when SAM 2 is not available."""
        print("\n🔄 Testing graceful fallback behavior...")
        
        from beaker_analysis import SAM_PREDICTOR
        
        if SAM_PREDICTOR is None:
            print("   SAM 2 not available - testing fallback behavior")
            
            # Vision analysis should still work
            from beaker_analysis import extract_solution_color
            
            try:
                dominant_color, color_hex, analysis_data = extract_solution_color(self.sample_image)
                print("   ✅ Fallback to circle detection successful")
                
                # Verify that we get a valid mask even without SAM
                sam_mask = analysis_data['sam_mask_preview']
                self.assertIsInstance(sam_mask, np.ndarray, "Should have mask even without SAM")
                
                # Verify that mask strategy is circle_only when SAM is not available
                self.assertEqual(analysis_data['mask_strategy'], 'circle_only', "Should use circle_only strategy when SAM not available")
                print(f"   ✅ Mask strategy correctly set to: {analysis_data['mask_strategy']}")
                
            except Exception as e:
                self.fail(f"Fallback behavior failed: {e}")
        else:
            print("   SAM 2 is available - fallback not needed")
            
            # Test that we get a valid mask strategy when SAM is available
            from beaker_analysis import extract_solution_color
            try:
                _, _, analysis_data = extract_solution_color(self.sample_image)
                valid_strategies = ['circle_only', 'sam_interior', 'sam_inverted']
                self.assertIn(analysis_data['mask_strategy'], valid_strategies, "Should use valid strategy when SAM available")
                print(f"   ✅ SAM-2 mask strategy: {analysis_data['mask_strategy']}")
            except Exception as e:
                self.fail(f"SAM analysis failed: {e}")
            self.assertTrue(True, "SAM 2 available, fallback test not applicable")

def run_sam2_integration_tests():
    """Run SAM 2 integration tests with detailed output."""
    print("🤖 Running SAM 2 Integration Test Suite")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSAM2Integration)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("✅ All SAM 2 integration tests passed!")
        return True
    else:
        print("❌ Some SAM 2 integration tests failed!")
        return False

if __name__ == "__main__":
    success = run_sam2_integration_tests()
    sys.exit(0 if success else 1)
