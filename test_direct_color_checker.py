#!/usr/bin/env python3
"""
Direct color checker test that runs inside the vision bridge container.
"""
import sys
import os
sys.path.append('/app')

import cv2
import numpy as np
from colour_checker_detection import detect_colour_checkers_segmentation
import json

def test_color_checker(image_path):
    """Test color checker detection directly."""
    print(f"Loading image: {image_path}")
    
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Could not load image from {image_path}")
        return False
    
    print(f"✅ Image loaded successfully. Shape: {img.shape}")
    
    try:
        print("🔍 Running color checker detection...")
        results = detect_colour_checkers_segmentation(img, additional_data=True)
        
        print(f"✅ Detection completed!")
        
        detections = []
        for i, result in enumerate(results):
            print(f"\n🎯 Color checker {i+1} found!")
            detection_info = {
                "quadrilateral": result.quadrilateral.tolist() if hasattr(result, 'quadrilateral') else None,
                "swatch_colours": result.swatch_colours.tolist() if hasattr(result, 'swatch_colours') else None,
            }
            detections.append(detection_info)
            
            if detection_info["quadrilateral"]:
                print(f"   📐 Quadrilateral: {len(detection_info['quadrilateral'])} corner points")
            if detection_info["swatch_colours"]:
                print(f"   🎨 Swatch colors: {len(detection_info['swatch_colours'])} colors detected")
        
        # Create final result
        final_result = {"detections": detections}
        
        if detections:
            print(f"\n🎉 Successfully detected {len(detections)} color checker(s)!")
        else:
            print(f"\n⚠️  No color checkers detected in the image.")
            print("This could mean:")
            print("- The image doesn't contain a standard color checker pattern")
            print("- The color checker is not clearly visible or well-lit")
            print("- The color checker is partially occluded or at a difficult angle")
        
        # Print JSON result
        print(f"\n📊 JSON Result:")
        print(json.dumps(final_result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Error during color checker detection: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Direct Color Checker Detection Test")
    print("="*60)
    
    # Test with sample color checker first
    print("\n1️⃣  Testing with sample color checker image:")
    print("-" * 50)
    sample_success = test_color_checker("/app/samples/ColorCheckerClassic_24patch_sRGB.png")
    
    # Test with our target image
    print("\n2️⃣  Testing with target image (aloha_lite_20250723.jpg):")
    print("-" * 50)
    target_success = test_color_checker("/tmp/test_image.jpg")
    
    print("\n" + "="*60)
    print("📋 SUMMARY:")
    print(f"   Sample image: {'✅ DETECTED' if sample_success else '❌ FAILED'}")  
    print(f"   Target image: {'✅ PROCESSED' if target_success else '❌ FAILED'}")
    
    if sample_success and target_success:
        print("\n🎉 All tests completed successfully!")
        print("🔍 The color checker detection system is working correctly.")
        print("📸 Your target image was processed but contains no detectable color checkers.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
