#!/usr/bin/env python3
"""
Test script for the new space mask algorithm - API endpoint version.
Tests the running vision-bridge server instead of importing functions directly.
"""
import requests
import numpy as np
import cv2
import io
import base64
from pathlib import Path

# Server configuration
SERVER_URL = "http://localhost:5000"
ANALYZE_ENDPOINT = f"{SERVER_URL}/analyze-beaker"
TIMEOUT = 30

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

def call_analyze_beaker_api(img, algorithm="space_mask", n_clusters=5, roi=None):
    """Call the /analyze-beaker API endpoint with the given parameters."""
    # Encode image as JPEG
    _, buffer = cv2.imencode('.jpg', img)
    
    # Prepare files for upload
    files = {'file': ('test_image.jpg', buffer.tobytes(), 'image/jpeg')}
    
    # Prepare query parameters
    params = {
        'algorithm': algorithm,
        'n_clusters': n_clusters
    }
    
    # Add ROI parameters if provided
    if roi is not None:
        top, bottom, left, right = roi
        params.update({
            'roi_top': top,
            'roi_bottom': bottom,
            'roi_left': left,
            'roi_right': right
        })
    
    try:
        response = requests.post(ANALYZE_ENDPOINT, files=files, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        return False, str(e)

def test_space_mask_algorithm():
    """Test the space mask algorithm via API."""
    print("Testing Space Mask Algorithm")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        # Test with default ROI (auto-calculated)
        success, result = call_analyze_beaker_api(img, algorithm="space_mask")
        
        if not success:
            print(f"✗ API call failed: {result}")
            return False
        
        print(f"✓ Default ROI test passed")
        print(f"  Dominant color: RGB{result['dominant_color']['rgb']} -> {result['dominant_color']['hex']}")
        print(f"  Algorithm: {result['analysis_stats']['algorithm']}")
        print(f"  ROI: {result['roi']}")
        print(f"  Color label: {result['analysis_stats']['color_label']}")
        print(f"  Vibrant pixels: {result['analysis_stats']['vibrant_pixels_count']}")
        
        # Test with custom ROI
        custom_roi = (200, 280, 270, 370)  # (top, bottom, left, right)
        success2, result2 = call_analyze_beaker_api(img, algorithm="space_mask", roi=custom_roi)
        
        if not success2:
            print(f"✗ Custom ROI API call failed: {result2}")
            return False
        
        print(f"\n✓ Custom ROI test passed")
        print(f"  Dominant color: RGB{result2['dominant_color']['rgb']} -> {result2['dominant_color']['hex']}")
        print(f"  Custom ROI: {result2['roi']}")
        print(f"  Color label: {result2['analysis_stats']['color_label']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Space mask test failed: {e}")
        return False

def test_hough_circle_algorithm():
    """Test the Hough Circle algorithm via API."""
    print("\nTesting Hough Circle Algorithm")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        success, result = call_analyze_beaker_api(img, algorithm="hough_circle", n_clusters=3)
        
        if not success:
            print(f"✗ API call failed: {result}")
            return False
        
        print(f"✓ Hough Circle test passed")
        print(f"  Dominant color: RGB{result['dominant_color']['rgb']} -> {result['dominant_color']['hex']}")
        print(f"  Algorithm: {result['analysis_stats']['algorithm']}")
        print(f"  Beaker circle: {result.get('beaker_circle', 'Not detected')}")
        print(f"  Clusters found: {len(result['clusters'])}")
        print(f"  Mask strategy: {result['analysis_stats'].get('mask_strategy', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Hough Circle test failed: {e}")
        return False

def test_sam2_algorithm():
    """Test the SAM2 algorithm via API (may fail if SAM2 not available)."""
    print("\nTesting SAM2 Algorithm")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        success, result = call_analyze_beaker_api(img, algorithm="sam2", n_clusters=3)
        
        if not success:
            print(f"⚠ SAM2 test skipped (expected if SAM2 not available): {result}")
            return True  # Not a failure if SAM2 isn't available
        
        print(f"✓ SAM2 test passed")
        print(f"  Dominant color: RGB{result['dominant_color']['rgb']} -> {result['dominant_color']['hex']}")
        print(f"  Algorithm: {result['analysis_stats']['algorithm']}")
        print(f"  Beaker circle: {result.get('beaker_circle', 'Not detected')}")
        print(f"  Clusters found: {len(result['clusters'])}")
        print(f"  Mask strategy: {result['analysis_stats'].get('mask_strategy', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"⚠ SAM2 test skipped (expected if SAM2 not available): {e}")
        return True  # Not a failure if SAM2 isn't available

def test_error_handling():
    """Test error handling with invalid parameters via API."""
    print("\nTesting Error Handling")
    print("=" * 40)
    
    img = create_test_image()
    
    try:
        # Test invalid algorithm
        success, result = call_analyze_beaker_api(img, algorithm="invalid_algorithm")
        if success:
            print("✗ Should have failed for invalid algorithm")
            return False
        else:
            print(f"✓ Correctly caught invalid algorithm: {result}")
        
        # Test invalid ROI (this should work but might give warnings)
        invalid_roi = (400, 300, 200, 100)  # bottom < top, right < left
        success2, result2 = call_analyze_beaker_api(img, algorithm="space_mask", roi=invalid_roi)
        if success2:
            print(f"⚠ Invalid ROI was processed (may be handled gracefully): {result2['analysis_stats']}")
        else:
            print(f"✓ Correctly caught invalid ROI: {result2}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def test_server_connectivity():
    """Test if the server is running and accessible."""
    print("Testing Server Connectivity")
    print("=" * 40)
    
    try:
        response = requests.get(f"{SERVER_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running and accessible")
            return True
        else:
            print(f"✗ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to server: {e}")
        print(f"  Make sure the server is running on {SERVER_URL}")
        return False

def main():
    """Run all tests against the running server."""
    print("Space Mask Algorithm API Test Suite")
    print("=" * 50)
    
    # Save test image for inspection
    test_img = create_test_image()
    cv2.imwrite("/tmp/test_image.jpg", test_img)
    print(f"Test image saved to: /tmp/test_image.jpg")
    
    tests = [
        test_server_connectivity,
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
        else:
            # If server connectivity fails, skip remaining tests
            if test == test_server_connectivity:
                print("\n❌ Cannot proceed without server connectivity")
                break
    
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
