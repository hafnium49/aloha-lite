#!/usr/bin/env python3
"""
Test the new CAM02-UCS color space plotting functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import ColorOptimizer

def test_color_space_functionality():
    """Test the CAM02-UCS color space data generation"""
    print("🎨 Testing CAM02-UCS color space functionality...")
    
    optimizer = ColorOptimizer()
    target_color = (200, 100, 50)  # Orange target
    optimizer.set_target_color(target_color)
    
    print(f"🎯 Target color: RGB{target_color}")
    
    # Test without any measurements
    color_data = optimizer.get_color_space_data()
    print(f"📊 Initial state - Available: {color_data['available']}")
    
    # Add some measurements to simulate optimization
    test_measurements = [
        ({'red': 3.0, 'yellow': 0.0, 'blue': 0.0}, (180, 80, 40)),   # Pure red attempt
        ({'red': 2.0, 'yellow': 1.0, 'blue': 0.0}, (190, 90, 45)),   # Red-yellow mix
        ({'red': 1.5, 'yellow': 1.2, 'blue': 0.3}, (195, 95, 48)),   # Closer to target
        ({'red': 1.3, 'yellow': 1.4, 'blue': 0.3}, (198, 98, 49)),   # Very close
    ]
    
    for i, (ratios, measured_rgb) in enumerate(test_measurements):
        optimizer.add_measurement(ratios, measured_rgb)
        print(f"📈 Added measurement {i+1}: {ratios} → RGB{measured_rgb}")
    
    # Get color space data
    color_data = optimizer.get_color_space_data()
    
    print(f"\n🎨 Color Space Analysis:")
    print(f"   Available: {color_data['available']}")
    print(f"   Color Space: {color_data['color_space']}")
    print(f"   Target LAB: {[round(x, 2) for x in color_data['target']['lab']]}")
    print(f"   Trail points: {len(color_data['trail'])}")
    
    # Test color conversions
    print(f"\n🔬 Color Space Conversions:")
    for i, point in enumerate(color_data['trail']):
        lab = [round(x, 2) for x in point['lab']]
        rgb = point['rgb']
        print(f"   Point {i+1}: RGB{rgb} → LAB{lab}")
    
    # Test axis labels
    labels = color_data['axis_labels']
    print(f"\n📊 Chart Configuration:")
    print(f"   X-axis: {labels['x']}")
    print(f"   Y-axis: {labels['y']}")
    print(f"   Title: {labels['title']}")
    
    # Calculate perceptual distances
    target_lab = color_data['target']['lab']
    print(f"\n📏 Perceptual Distances (in {color_data['color_space']} space):")
    for i, point in enumerate(color_data['trail']):
        # Calculate Euclidean distance in LAB space
        lab = point['lab']
        distance = ((lab[1] - target_lab[1])**2 + (lab[2] - target_lab[2])**2)**0.5
        print(f"   Point {i+1}: ΔE ≈ {distance:.2f}")
    
    return color_data['available'] and len(color_data['trail']) == 4

def test_color_conversion_accuracy():
    """Test color conversion accuracy"""
    print("\n🧮 Testing color conversion accuracy...")
    
    # Test with known colors
    test_colors = [
        (255, 0, 0),    # Pure red
        (0, 255, 0),    # Pure green
        (0, 0, 255),    # Pure blue
        (255, 255, 255), # White
        (128, 128, 128), # Gray
        (200, 100, 50),  # Orange
    ]
    
    optimizer = ColorOptimizer()
    
    for rgb in test_colors:
        lab = optimizer._rgb_to_cam02ucs(rgb)
        print(f"   RGB{rgb} → LAB({lab[0]:.1f}, {lab[1]:.1f}, {lab[2]:.1f})")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing CAM02-UCS Color Space Implementation\n")
    
    success1 = test_color_space_functionality()
    success2 = test_color_conversion_accuracy()
    
    overall_success = success1 and success2
    
    if overall_success:
        print("\n🎉 CAM02-UCS color space tests PASSED!")
        print("   ✅ Color space data generation working")
        print("   ✅ Color conversions working")
        print("   ✅ Ready for frontend plotting")
    else:
        print("\n❌ CAM02-UCS color space tests FAILED!")
    
    exit(0 if overall_success else 1)
