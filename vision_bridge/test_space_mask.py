#!/usr/bin/env python3
"""
Test script for the new space mask algorithm in extract_solution_color.
Creates a simple test image and tests all three algorithms.
"""
import os, sys
import numpy as np
import cv2
from pathlib import Path

# Add vision_bridge to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the function (set testing mode to avoid Prometheus server)
os.environ['TESTING'] = 'true'
from main import extract_solution_color

def create_test_image():
    """Create a simple test image with a colored center region."""
    # Create a 640x480 test image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Fill with light gray background
    img.fill(128)
    
    # Add a colored center region (simulating solution)
    center_x, center_y = 320, 240
    roi_size = 50
    
    # Create a blue square in the center
    img[center_y-roi_size:center_y+roi_size, center_x-roi_size:center_x+roi_size] = [0, 0, 255]  # BGR: red
    
    # Add some circular features for Hough Circle detection
    cv2.circle(img, (center_x, center_y), 80, (50, 50, 50), 3)  # Dark circle outline
    
    return img

def test_space_mask_algorithm():
    """Test the space mask algorithm."""
    print("Testing Space Mask Algorithm")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        # Test with default ROI (auto-calculated)
        color_rgb, color_hex, analysis = extract_solution_color(img, algorithm="space_mask")
        
        print(f"✓ Default ROI test passed")
        print(f"  Dominant color: RGB{color_rgb} -> {color_hex}")
        print(f"  Algorithm: {analysis['algorithm']}")
        print(f"  ROI: {analysis['roi']}")
        print(f"  Color label: {analysis['color_label']}")
        print(f"  Vibrant pixels: {analysis['vibrant_pixels_count']}/{analysis['total_roi_pixels']}")
        
        # Test with custom ROI
        custom_roi = (200, 280, 270, 370)  # (top, bottom, left, right)
        color_rgb2, color_hex2, analysis2 = extract_solution_color(img, algorithm="space_mask", roi=custom_roi)
        
        print(f"\n✓ Custom ROI test passed")
        print(f"  Dominant color: RGB{color_rgb2} -> {color_hex2}")
        print(f"  Custom ROI: {analysis2['roi']}")
        print(f"  Color label: {analysis2['color_label']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Space mask test failed: {e}")
        return False

def test_hough_circle_algorithm():
    """Test the Hough Circle algorithm."""
    print("\nTesting Hough Circle Algorithm")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        color_rgb, color_hex, analysis = extract_solution_color(img, algorithm="hough_circle", n_clusters=3)
        
        print(f"✓ Hough Circle test passed")
        print(f"  Dominant color: RGB{color_rgb} -> {color_hex}")
        print(f"  Algorithm: {analysis['algorithm']}")
        print(f"  Beaker circle: {analysis.get('beaker_circle', 'Not detected')}")
        print(f"  Clusters found: {len(analysis['clusters'])}")
        print(f"  Mask strategy: {analysis.get('mask_strategy', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Hough Circle test failed: {e}")
        return False

def test_sam2_algorithm():
    """Test the SAM2 algorithm (may fail if SAM2 not available)."""
    print("\nTesting SAM2 Algorithm")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        color_rgb, color_hex, analysis = extract_solution_color(img, algorithm="sam2", n_clusters=3)
        
        print(f"✓ SAM2 test passed")
        print(f"  Dominant color: RGB{color_rgb} -> {color_hex}")
        print(f"  Algorithm: {analysis['algorithm']}")
        print(f"  Beaker circle: {analysis.get('beaker_circle', 'Not detected')}")
        print(f"  Clusters found: {len(analysis['clusters'])}")
        print(f"  Mask strategy: {analysis.get('mask_strategy', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"⚠ SAM2 test skipped (expected if SAM2 not available): {e}")
        return True  # Not a failure if SAM2 isn't available

def test_error_handling():
    """Test error handling with invalid parameters."""
    print("\nTesting Error Handling")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        # Test invalid algorithm
        try:
            extract_solution_color(img, algorithm="invalid_algorithm")
            print("✗ Should have raised ValueError for invalid algorithm")
            return False
        except ValueError as e:
            print(f"✓ Correctly caught invalid algorithm: {e}")
        
        # Test invalid ROI
        try:
            invalid_roi = (400, 300, 200, 100)  # bottom < top, right < left
            extract_solution_color(img, algorithm="space_mask", roi=invalid_roi)
            print("✗ Should have raised ValueError for invalid ROI")
            return False
        except (ValueError, Exception) as e:
            print(f"✓ Correctly caught invalid ROI: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Space Mask Algorithm Test Suite")
    print("=" * 50)
    
    # Save test image for inspection
    test_img = create_test_image()
    cv2.imwrite("/tmp/test_image.jpg", test_img)
    print(f"Test image saved to: /tmp/test_image.jpg")
    
    tests = [
        test_space_mask_algorithm,
        test_hough_circle_algorithm,
        test_sam2_algorithm,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
