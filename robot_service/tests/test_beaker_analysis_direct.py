#!/usr/bin/env python3
"""
Direct test of beaker analysis using existing images - no robot arm movement required
"""
import requests
import os
from pathlib import Path

def test_beaker_analysis_direct():
    """Test beaker analysis directly with existing images"""
    print("🧪 Testing Beaker Analysis (Direct API Test)")
    print("=" * 60)
    
    # Path to existing test images
    temp_images_dir = Path("/home/hafnium/aloha-lite/temporary_images")
    test_images = list(temp_images_dir.glob("camera_*.jpg"))
    
    if not test_images:
        print("❌ No test images found in temporary_images directory")
        return False
    
    # Use the most recent image
    test_image = sorted(test_images)[-1]
    print(f"📸 Using test image: {test_image.name}")
    print(f"📍 Image path: {test_image}")
    
    # Test the vision bridge analyze-beaker endpoint directly
    vision_bridge_url = "http://localhost:5000"
    analyze_url = f"{vision_bridge_url}/analyze-beaker"
    
    print(f"🌐 Testing API endpoint: POST {analyze_url}")
    
    try:
        # Open and send the image file
        with open(test_image, 'rb') as image_file:
            files = {'file': ('test_image.jpg', image_file, 'image/jpeg')}
            response = requests.post(analyze_url, files=files, timeout=30)
        
        if response.status_code == 200:
            analysis_data = response.json()
            
            print("✅ Beaker analysis successful!")
            print("\n📊 Analysis Results:")
            
            # Display dominant color
            if 'dominant_color' in analysis_data:
                dominant = analysis_data['dominant_color']
                print(f"🎨 Dominant color: {dominant.get('hex', 'unknown')} RGB{dominant.get('rgb', [0,0,0])}")
            
            # Display beaker detection
            if 'beaker_circle' in analysis_data:
                circle = analysis_data['beaker_circle']
                print(f"🥽 Beaker detected at: ({circle.get('x', 0)}, {circle.get('y', 0)}) radius: {circle.get('radius', 0)}px")
            
            # Display cluster information
            if 'clusters' in analysis_data:
                clusters = analysis_data['clusters']
                print(f"🔬 Color clusters found: {len(clusters)}")
                for i, cluster in enumerate(clusters[:3]):  # Show top 3
                    print(f"   Cluster {i+1}: {cluster.get('hex', 'unknown')} ({cluster.get('pixel_count', 0)} pixels)")
            
            # Display analysis stats
            if 'analysis_stats' in analysis_data:
                stats = analysis_data['analysis_stats']
                print(f"📈 Analysis stats: {stats.get('total_pixels_analyzed', 0)} pixels analyzed")
            
            print("\n🎉 Beaker analysis test completed successfully!")
            print("💡 This confirms the vision bridge and beaker analysis system is working")
            return True
            
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - beaker analysis took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - vision bridge service may not be running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_beaker_analysis_direct()
    if success:
        print("\n✅ CONCLUSION: Beaker analysis system is working correctly!")
        print("💡 The reason beaker analysis appears 'not available' is likely:")
        print("   - No recent laboratory procedures have been executed")
        print("   - Sequential execution failed for other reasons (not beaker analysis)")
        print("   - Camera capture timeout during actual procedures")
    else:
        print("\n❌ CONCLUSION: Beaker analysis system has issues that need to be resolved.")
