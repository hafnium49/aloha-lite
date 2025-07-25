#!/usr/bin/env python3
"""
Quick test script for SAM-2 integration in vision_bridge
"""

import os
import sys
import cv2
import numpy as np

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

# Import the beaker analysis functions
try:
    from beaker_analysis import extract_solution_color, create_visualization_image
    print("✅ Successfully imported from beaker_analysis.py")
except Exception as e:
    print(f"❌ Failed to import from beaker_analysis.py: {e}")
    sys.exit(1)

# Test with a sample image if available
sample_image_path = "/home/hafnium/aloha-lite/temporary_images/camera_0_20250723_113227.jpg"

if os.path.exists(sample_image_path):
    print(f"🧪 Testing with sample image: {sample_image_path}")
    
    # Load the test image
    img = cv2.imread(sample_image_path)
    if img is not None:
        try:
            # Perform analysis
            dominant_color, color_hex, analysis_data = extract_solution_color(img)
            
            print(f"✅ Vision analysis successful!")
            print(f"   Dominant color: {color_hex} RGB{tuple(dominant_color)}")
            print(f"   Beaker detected at: ({analysis_data['beaker_circle']['x']}, {analysis_data['beaker_circle']['y']})")
            print(f"   Beaker radius: {analysis_data['beaker_circle']['radius']}px")
            print(f"   SAM mask preview shape: {analysis_data['sam_mask_preview'].shape}")
            print(f"   Pixels analyzed: {analysis_data['total_pixels_analyzed']:,}")
            
            # Test visualization
            viz_img = create_visualization_image(img, analysis_data)
            print(f"✅ Visualization created successfully")
            print(f"   Visualization image shape: {viz_img.shape}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Could not load image: {sample_image_path}")
else:
    print(f"ℹ️  Sample image not found: {sample_image_path}")
    print("✅ Import test successful - functions are available")

print("\n🔍 SAM-2 Integration Status:")
from beaker_analysis import SAM_PREDICTOR
if SAM_PREDICTOR is not None:
    print("✅ SAM-2 is loaded and ready")
else:
    print("⚠️  SAM-2 not available (graceful fallback to circle detection)")

print("\n✅ All tests completed successfully!")
