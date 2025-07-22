#!/usr/bin/env python3
"""
Simple color checker test script that uses requests to test the vision bridge API.
"""
import requests
import sys
import json
import os

def test_color_checker(image_path, api_url):
    """Test the color checker endpoint with an image file."""
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return False
        
    print(f"Testing color checker with image: {image_path}")
    print(f"API URL: {api_url}")
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'file': (os.path.basename(image_path), img_file, 'image/jpeg')}
            response = requests.post(api_url, files=files, timeout=30)
            
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Color checker API test successful!")
            print("Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('detections'):
                print(f"\n🎯 Found {len(result['detections'])} color checker(s)!")
                for i, detection in enumerate(result['detections']):
                    print(f"  Detection {i+1}:")
                    if 'quadrilateral' in detection:
                        print(f"    Quadrilateral points: {len(detection['quadrilateral'])} corners")
                    if 'swatch_colours' in detection:
                        print(f"    Swatch colors: {len(detection['swatch_colours'])} colors detected")
            else:
                print("\n⚠️  No color checkers detected in the image.")
                print("This could mean:")
                print("- The image doesn't contain a standard color checker pattern")
                print("- The color checker is not clearly visible or well-lit")
                print("- The color checker is partially occluded or at a difficult angle")
            
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - check if the vision bridge service is running")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test image path
    image_path = "temporary_images/aloha_lite_20250723.jpg"
    
    # Try different possible API endpoints
    endpoints_to_try = [
        "http://localhost:8080/vision/color-checker",  # Through Traefik proxy
        "http://localhost:8000/color-checker",         # Direct to container (if exposed)
    ]
    
    success = False
    for api_url in endpoints_to_try:
        print(f"\n{'='*60}")
        print(f"Testing endpoint: {api_url}")
        print('='*60)
        
        success = test_color_checker(image_path, api_url)
        if success:
            break
        print(f"Failed to connect to {api_url}, trying next endpoint...")
    
    if not success:
        print(f"\n❌ Could not connect to any endpoint. Make sure:")
        print("1. The vision bridge service is running (docker ps)")
        print("2. The Traefik gateway is configured correctly") 
        print("3. The services are healthy (docker-compose logs)")
        sys.exit(1)
    else:
        print(f"\n✅ Color checker test completed successfully!")
