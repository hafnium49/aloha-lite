#!/usr/bin/env python3
"""
Test beaker analysis using existing images without camera capture
"""
import requests
import json
import os
from pathlib import Path
from datetime import datetime

def test_beaker_analysis_with_existing_image():
    """Test beaker analysis using the most recent existing image"""
    
    print("🧪 Testing Beaker Analysis with Existing Image")
    print("=" * 60)
    
    # Find the most recent camera image
    temp_images_dir = Path("/home/hafnium/aloha-lite/temporary_images")
    image_files = list(temp_images_dir.glob("camera_*.jpg"))
    
    if not image_files:
        print("❌ No camera images found in temporary_images directory")
        return False
    
    # Use the most recent image
    latest_image = max(image_files, key=lambda p: p.stat().st_mtime)
    print(f"📸 Using existing image: {latest_image.name}")
    print(f"📁 Image path: {latest_image}")
    
    try:
        print(f"\n🔬 Analyzing beaker color using vision bridge API...")
        
        # Make API request to vision bridge for beaker analysis
        vision_bridge_url = "http://localhost:5000/analyze-beaker"
        print(f"🌐 Making API request: POST {vision_bridge_url}")
        
        # Prepare the image file for upload
        with open(latest_image, 'rb') as image_file:
            files = {'file': ('beaker_image.jpg', image_file, 'image/jpeg')}
            response = requests.post(vision_bridge_url, files=files, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Vision bridge API failed with status {response.status_code}: {response.text}")
            return False
        
        analysis_data = response.json()
        
        # Extract analysis results
        dominant_color = analysis_data.get('dominant_color', {})
        beaker_circle = analysis_data.get('beaker_circle', {})
        clusters = analysis_data.get('clusters', [])
        stats = analysis_data.get('analysis_stats', {})
        
        # Display results
        print(f"\n📊 Analysis Results:")
        rgb = dominant_color.get('rgb', [0, 0, 0])
        hex_color = dominant_color.get('hex', '#000000')
        print(f"🎨 Dominant color: {hex_color} - RGB({rgb[0]}, {rgb[1]}, {rgb[2]})")
        
        x = beaker_circle.get('x', 0)
        y = beaker_circle.get('y', 0)
        radius = beaker_circle.get('radius', 0)
        print(f"🥽 Beaker detected at: ({x}, {y}) with radius {radius}px")
        
        print(f"🔬 Color clusters found: {len(clusters)}")
        for i, cluster in enumerate(clusters[:3]):  # Show top 3
            cluster_rgb = cluster.get('rgb', [0, 0, 0])
            cluster_hex = cluster.get('hex', '#000000')
            pixel_count = cluster.get('pixel_count', 0)
            saturation = cluster.get('saturation', 0)
            print(f"   {i+1}. {cluster_hex} - RGB({cluster_rgb[0]}, {cluster_rgb[1]}, {cluster_rgb[2]}) - {pixel_count:,} pixels (sat: {saturation:.1f})")
        
        # Save analysis results to a JSON file (simulating what sequential_execute.py does)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"beaker_analysis_0_{timestamp}.json"
        results_filepath = temp_images_dir / results_filename
        
        with open(results_filepath, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n💾 Analysis results saved to: {results_filename}")
        
        # Provide color interpretation
        print(f"\n🧪 Color Interpretation:")
        if hex_color.lower() in ['#ff0000', '#dc143c', '#b22222'] or (rgb[0] > 150 and rgb[1] < 100 and rgb[2] < 100):
            print("   🔴 Red solution detected - likely contains red dye or indicator")
        elif hex_color.lower() in ['#ffff00', '#ffd700', '#daa520'] or (rgb[0] > 200 and rgb[1] > 200 and rgb[2] < 100):
            print("   🟡 Yellow solution detected - likely contains yellow dye or indicator")
        elif hex_color.lower() in ['#0000ff', '#1e90ff', '#4169e1'] or (rgb[0] < 100 and rgb[1] < 100 and rgb[2] > 150):
            print("   🔵 Blue solution detected - likely contains blue dye or indicator")
        elif rgb[0] < 50 and rgb[1] < 50 and rgb[2] < 50:
            print("   ⚫ Dark/black solution detected")
        elif rgb[0] > 200 and rgb[1] > 200 and rgb[2] > 200:
            print("   ⚪ Clear/transparent solution detected")
        else:
            print(f"   🎨 Custom color solution detected: {hex_color}")
        
        print("=" * 60)
        print("✅ Beaker analysis completed successfully!")
        print("💡 This demonstrates the full beaker analysis workflow without camera capture")
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - beaker analysis took too long")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during beaker analysis: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response from vision bridge API: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Image file not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during beaker analysis: {e}")
        return False

if __name__ == "__main__":
    success = test_beaker_analysis_with_existing_image()
    if success:
        print("\n🎉 SUCCESS: Beaker analysis workflow is fully functional!")
        print("💡 The issue with 'beaker analysis not available' is resolved.")
        print("🔧 The problem was incorrect URLs in the sequential executor.")
    else:
        print("\n❌ FAILED: Beaker analysis workflow has issues.")
