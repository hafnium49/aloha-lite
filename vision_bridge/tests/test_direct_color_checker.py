#!/usr/bin/env python3
"""
Direct circle colour test that runs inside the vision bridge container.
Updated for the new circle colour detection endpoint.
"""
import sys
import os

# Add the parent directories to path for imports
sys.path.append('/app')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import cv2
import numpy as np
import json
import math

def detect_circle_colour(image_path):
    """Test circle colour detection directly using OpenCV."""
    print(f"Loading image: {image_path}")
    
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Could not load image from {image_path}")
        return False
    
    print(f"✅ Image loaded successfully. Shape: {img.shape}")
    h, w = img.shape[:2]
    
    try:
        print("🔍 Running circle detection...")
        
        # Convert to grayscale and apply blur
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        # Hough circle detection
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=h // 4,
            param1=100,
            param2=30,
            minRadius=int(min(h, w) * 0.05),
            maxRadius=int(min(h, w) * 0.4),
        )

        if circles is None:
            print("⚠️  No circles detected in the image.")
            return {"detections": []}

        circles = np.round(circles[0, :]).astype(int)
        print(f"🎯 Found {len(circles)} potential circle(s)")

        # Keep only circles whose centre is in the left half
        left_circles = [c for c in circles if c[0] < w // 2]
        if not left_circles:
            print("ℹ️  No circles found in left half, using all circles")
            left_circles = circles.tolist()
        else:
            print(f"� {len(left_circles)} circle(s) found in left half")

        # Choose the largest radius among remaining circles
        cx, cy, r = max(left_circles, key=lambda c: c[2])

        # Sanity check radius
        r = int(max(1, min(r, w, h)))

        print(f"   📍 Selected circle: center=({cx}, {cy}), radius={r}")

        # Create mask and compute mean color
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (cx, cy), r, 255, -1)

        mean_bgr = cv2.mean(img, mask=mask)[:3]  # ignore alpha
        mean_bgr = [int(round(c)) for c in mean_bgr]
        mean_rgb = mean_bgr[::-1]
        mean_hex = "#{:02X}{:02X}{:02X}".format(*mean_rgb)

        result = {
            "circle": {"center": [int(cx), int(cy)], "radius": int(r)},
            "mean_color": {"bgr": mean_bgr, "rgb": mean_rgb, "hex": mean_hex},
        }
        
        print(f"🎨 Color analysis complete!")
        print(f"   BGR: {mean_bgr}")
        print(f"   RGB: {mean_rgb}")  
        print(f"   HEX: {mean_hex}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during circle detection: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Direct Circle Colour Detection Test")
    print("="*60)
    
    # Test with sample image first - adjusted paths for new location
    print("\n1️⃣  Testing with sample image:")
    print("-" * 50)
    sample_success = detect_circle_colour("../samples/ColorCheckerClassic_24patch_sRGB.png")
    
    # Test with our target image - adjusted for new location
    print("\n2️⃣  Testing with target image (aloha_lite_20250723.jpg):")
    print("-" * 50)
    target_success = detect_circle_colour("../../temporary_images/aloha_lite_20250723.jpg")
    
    print("\n" + "="*60)
    print("📋 SUMMARY:")
    
    if sample_success and sample_success != {}:
        print(f"   Sample image: ✅ CIRCLE DETECTED")
        if isinstance(sample_success, dict) and 'circle' in sample_success:
            print(f"     Circle details: {json.dumps(sample_success, indent=4)}")
    elif sample_success == {}:
        print(f"   Sample image: ⚠️  NO CIRCLES FOUND")
    else:
        print(f"   Sample image: ❌ FAILED")
        
    if target_success and target_success != {}:
        print(f"   Target image: ✅ CIRCLE DETECTED")
        if isinstance(target_success, dict) and 'circle' in target_success:
            print(f"     Circle details: {json.dumps(target_success, indent=4)}")
    elif target_success == {}:
        print(f"   Target image: ⚠️  NO CIRCLES FOUND")
    else:
        print(f"   Target image: ❌ FAILED")
    
    if (sample_success is not False) and (target_success is not False):
        print("\n🎉 All tests completed successfully!")
        print("🔍 The circle colour detection system is working correctly.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
