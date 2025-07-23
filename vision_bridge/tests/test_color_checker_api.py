#!/usr/bin/env python3
"""
Circle colour API test script that uses requests to test the vision bridge API.
Updated for the new /circle-colour endpoint.
"""
import requests
import sys
import json
import os

def test_circle_colour(image_path, api_url):
    """Test the circle colour endpoint with an image file."""
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return False
        
    print(f"Testing circle colour detection with image: {image_path}")
    print(f"API URL: {api_url}")
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'file': (os.path.basename(image_path), img_file, 'image/jpeg')}
            response = requests.post(api_url, files=files, timeout=30)
            
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Circle colour API test successful!")
            print("Response:")
            print(json.dumps(result, indent=2))
            
            if 'circle' in result and 'mean_color' in result:
                circle = result['circle']
                color = result['mean_color']
                print(f"\n🎯 Circle detected!")
                print(f"  📍 Center: ({circle['center'][0]}, {circle['center'][1]})")
                print(f"  📏 Radius: {circle['radius']} pixels")
                print(f"  🎨 Average Color:")
                print(f"    BGR: {color['bgr']}")
                print(f"    RGB: {color['rgb']}")
                print(f"    HEX: {color['hex']}")
            else:
                print("\n⚠️ Unexpected response format")
            
            return True
        elif response.status_code == 422:
            result = response.json()
            print("ℹ️ No circle detected in the image.")
            print("Response:")
            print(json.dumps(result, indent=2))
            print("\nThis could mean:")
            print("- The image doesn't contain clear circular objects")
            print("- Circles are not in the left half of the image")
            print("- Circles are too small or too large for detection parameters")
            return True  # This is a valid response, not an error
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
    # Test image path - adjusted for new location
    image_path = "../../temporary_images/aloha_lite_20250723.jpg"
    
    # Try different possible API endpoints
    endpoints_to_try = [
        "http://localhost:8080/vision/circle-colour",  # Through Traefik proxy
        "http://localhost:8000/circle-colour",         # Direct to container (if exposed)
    ]
    
    success = False
    for api_url in endpoints_to_try:
        print(f"\n{'='*60}")
        print(f"Testing endpoint: {api_url}")
        print('='*60)
        
        success = test_circle_colour(image_path, api_url)
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
        print(f"\n✅ Circle colour test completed successfully!")
