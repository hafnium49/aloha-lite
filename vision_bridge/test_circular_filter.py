#!/usr/bin/env python3
"""
Simple test script for the circular component filtering functionality.
"""

import numpy as np
import cv2
from main import filter_most_circular_component

def create_test_mask():
    """Create a test SAM mask with multiple disconnected components."""
    mask = np.zeros((400, 400), dtype=np.uint8)
    
    # Component 1: Circle near center (should be selected as most circular)
    cv2.circle(mask, (200, 180), 50, 255, -1)
    
    # Component 2: Rectangle (robot arm grip simulation)
    cv2.rectangle(mask, (50, 50), (120, 80), 255, -1)
    
    # Component 3: Irregular shape (sonicator edge simulation)
    pts = np.array([[300, 100], [350, 120], [380, 180], [320, 200], [290, 150]], np.int32)
    cv2.fillPoly(mask, [pts], 255)
    
    # Component 4: Small circular component (should have lower score due to distance)
    cv2.circle(mask, (100, 300), 20, 255, -1)
    
    return mask

def test_circular_filter():
    """Test the circular component filtering."""
    print("Testing circular component filtering...")
    
    # Create test mask
    test_mask = create_test_mask()
    
    # Hough circle parameters (should overlap with component 1)
    circle_x, circle_y, circle_radius = 200, 180, 60
    
    # Apply filtering
    filtered_mask = filter_most_circular_component(test_mask, circle_x, circle_y, circle_radius)
    
    # Count components in original vs filtered mask
    orig_components = cv2.connectedComponents(test_mask)[0] - 1  # Subtract background
    filtered_components = cv2.connectedComponents(filtered_mask)[0] - 1
    
    print(f"Original components: {orig_components}")
    print(f"Filtered components: {filtered_components}")
    
    # Check if filtering worked
    if filtered_components == 1:
        print("✅ Filtering successful: Reduced to single component")
    else:
        print("❌ Filtering failed: Should have exactly 1 component")
    
    # Check if the selected component is roughly circular and centered
    contours, _ = cv2.findContours(filtered_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter > 0:
            circularity = (4 * np.pi * area) / (perimeter * perimeter)
            print(f"Selected component circularity: {circularity:.3f} (1.0 = perfect circle)")
            
            # Check centroid
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                distance_to_target = np.sqrt((cx - circle_x)**2 + (cy - circle_y)**2)
                print(f"Selected component center: ({cx}, {cy}), distance from target: {distance_to_target:.1f}")
                
                if distance_to_target < 30 and circularity > 0.7:
                    print("✅ Selected component appears to be the correct circular beaker!")
                else:
                    print("❌ Selected component may not be the correct target")
    
    return test_mask, filtered_mask

if __name__ == "__main__":
    test_circular_filter()
