#!/usr/bin/env python3
import requests
import json
from pathlib import Path

print("🧪 Testing beaker analysis API directly...")

# Test if vision bridge is responding
try:
    response = requests.get("http://localhost:8000/docs", timeout=5)
    print("✅ Vision bridge server is responding")
except:
    print("❌ Vision bridge server not responding")
    exit(1)

# Test with our sample image  
image_path = Path("../temporary_images/camera_0_20250723_113227.jpg")
if image_path.exists():
    print(f"✅ Test image found: {image_path}")
    
    # Test the beaker analysis endpoint
    with open(image_path, 'rb') as f:
        files = {"file": (image_path.name, f, "image/jpeg")}
        response = requests.post("http://localhost:8000/analyze-beaker", files=files, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        color = result.get("dominant_color", {})
        print(f"✅ Beaker analysis successful!")
        print(f"🎨 Dominant color: {color.get('hex', 'unknown')}")
        print(f"📊 Analysis completed")
    else:
        print(f"❌ API error: {response.status_code}")
else:
    print("❌ Test image not found")
