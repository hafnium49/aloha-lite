#!/usr/bin/env python3
"""
Quick API test for 4-pigment system functionality.
Tests the key API endpoints to ensure 4-pigment ratios are returned correctly.
"""

import sys
import os
import json

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, color_optimizer
from fastapi.testclient import TestClient

def test_4_pigment_api():
    """Test that the API returns 4-pigment ratios correctly."""
    print("🧪 Testing 4-Pigment API Functionality")
    print("=" * 50)
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Get new target color
    print("\n🎯 Testing target color generation...")
    response = client.get("/api/target-color")
    assert response.status_code == 200
    data = response.json()
    assert "target_rgb" in data
    assert len(data["target_rgb"]) == 3  # RGB tuple
    print(f"✅ Target color: RGB{data['target_rgb']}")
    
    # Test 2: Get initial recommendation (should have 4 pigments)
    print("\n📋 Testing initial ratio recommendation...")
    response = client.post("/api/recommend-ratios")
    assert response.status_code == 200
    data = response.json()
    
    assert "recommended_ratios" in data
    ratios = data["recommended_ratios"]
    
    # Should have exactly 4 pigments
    expected_keys = {"red", "yellow", "blue", "white"}
    assert set(ratios.keys()) == expected_keys
    print(f"✅ Initial ratios: {ratios}")
    
    # All ratios should be positive
    for pigment, ratio in ratios.items():
        assert ratio >= 0, f"{pigment} ratio should be non-negative"
    
    # White should have minimum volume
    assert ratios["white"] >= 0.1, "White should have minimum volume of 0.1"
    print("✅ All ratios are valid (positive, white ≥ 0.1)")
    
    # Test 3: Add measurement and get updated recommendation
    print("\n🔬 Testing measurement feedback loop...")
    measurement_data = {
        "ratios": ratios,
        "measured_rgb": [150, 120, 100]  # Simulated measurement
    }
    
    response = client.post("/api/recommend-ratios", 
                          json=measurement_data,
                          headers={"content-type": "application/json"})
    assert response.status_code == 200
    data = response.json()
    
    new_ratios = data["recommended_ratios"]
    assert set(new_ratios.keys()) == expected_keys
    print(f"✅ Updated ratios: {new_ratios}")
    
    # Test 4: Check statistics - should now track hue-based distances
    print("\n📊 Testing optimization statistics...")
    assert "statistics" in data
    stats = data["statistics"]
    
    assert "total_attempts" in stats
    assert stats["total_attempts"] >= 1
    
    # With hue-based optimization, distances should be in degrees (0-180)
    if stats.get("current_distance") is not None:
        print(f"🎯 Current hue distance: {stats['current_distance']:.1f}° (should be 0-180°)")
        assert 0 <= stats["current_distance"] <= 180, "Hue distance should be 0-180°"
    
    print(f"✅ Statistics: {stats['total_attempts']} attempts, hue optimization active")
    
    # Test 5: Test multiple iterations
    print("\n🔄 Testing multiple optimization iterations...")
    for i in range(3):
        # Simulate measurement
        measurement_data = {
            "ratios": new_ratios,
            "measured_rgb": [160 + i*10, 130 + i*5, 110 + i*3]
        }
        
        response = client.post("/api/recommend-ratios", 
                              json=measurement_data,
                              headers={"content-type": "application/json"})
        assert response.status_code == 200
        data = response.json()
        new_ratios = data["recommended_ratios"]
        
        # Should still have 4 pigments
        assert set(new_ratios.keys()) == expected_keys
        print(f"✅ Iteration {i+1}: {new_ratios}")
    
    # Test 6: Get optimization history
    print("\n📚 Testing optimization history...")
    response = client.get("/api/optimization-history")
    assert response.status_code == 200
    data = response.json()
    
    assert "history" in data
    history = data["history"]
    assert len(history) >= 4  # Should have multiple measurements
    
    # Each history entry should have ratios with 4 pigments
    for entry in history:
        assert "ratios" in entry
        assert set(entry["ratios"].keys()) == expected_keys
    
    print(f"✅ History contains {len(history)} entries, all with 4-pigment ratios")
    
    # Test 5: Hue visualization data API endpoint
    print("\n🎨 Testing hue visualization data API...")
    response = client.get("/api/hue-visual-data")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "success"
    assert "available" in data
    
    if data["available"]:
        # If data is available, check structure
        assert "target_hue_deg" in data
        assert "hue_series_deg" in data
        assert "hue_error_deg" in data
        assert "rgb_series" in data
        
        # Verify data types
        assert isinstance(data["target_hue_deg"], (int, float))
        assert isinstance(data["hue_series_deg"], list)
        assert isinstance(data["hue_error_deg"], list)
        assert isinstance(data["rgb_series"], list)
        
        # If we have measurements, verify lengths match
        if len(data["hue_series_deg"]) > 0:
            assert len(data["hue_series_deg"]) == len(data["rgb_series"])
            assert len(data["hue_error_deg"]) == len(data["rgb_series"])
            
            print(f"✅ Hue data: target={data['target_hue_deg']:.1f}°, {len(data['hue_series_deg'])} measurements")
            
            # Check hue values are in valid range
            for i, hue in enumerate(data["hue_series_deg"]):
                assert 0 <= hue <= 360, f"Hue {i} should be in range 0-360°"
            
            # Check RGB values are valid
            for i, rgb in enumerate(data["rgb_series"]):
                assert len(rgb) == 3, f"RGB {i} should have 3 components"
                for component in rgb:
                    assert 0 <= component <= 255, f"RGB component should be in range 0-255"
        else:
            print("✅ Hue visualization API available but no measurement data yet")
    else:
        print("✅ Hue visualization API indicates no data available (expected for fresh optimizer)")
    
    print("\n" + "=" * 50)
    print("🎉 All 4-Pigment API tests passed!")
    print("✅ The system correctly handles 4-pigment ratios including white solvent")
    print("✅ Hue visualization data API is working correctly")
    return True

if __name__ == "__main__":
    try:
        test_4_pigment_api()
        print("\n✅ Test Suite PASSED")
    except AssertionError as e:
        print(f"\n❌ Test Suite FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test Suite ERROR: {e}")
        sys.exit(1)
