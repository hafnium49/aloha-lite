#!/usr/bin/env python3
"""
Test API endpoints to ensure they work correctly with 10.0 mL normalization.
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from main import color_optimizer
    API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import API components: {e}")
    API_AVAILABLE = False

def test_api_logic():
    """Test core API logic with new normalization."""
    if not API_AVAILABLE:
        print("❌ API components not available")
        return False
    
    print("🧪 Testing API Logic with 10.0 mL Normalization")
    print("=" * 50)
    
    # Test 1: Initial recommendation
    print("1. Testing initial recommendation...")
    color_optimizer.set_target_color((200, 150, 100))
    
    initial_ratios = color_optimizer.recommend_next_ratios()
    total1 = sum(initial_ratios.values())
    assert abs(total1 - 10.0) < 0.01, f"Expected 10.0 mL, got {total1}"
    print(f"   ✅ Initial recommendation total: {total1:.2f} mL")
    print(f"   📊 Ratios: {initial_ratios}")
    
    # Test 2: Add measurement and get new recommendation
    print("2. Testing recommendation after measurement...")
    color_optimizer.add_measurement(initial_ratios, (180, 160, 140))
    
    second_ratios = color_optimizer.recommend_next_ratios()
    total2 = sum(second_ratios.values())
    assert abs(total2 - 10.0) < 0.01, f"Expected 10.0 mL, got {total2}"
    print(f"   ✅ Second recommendation total: {total2:.2f} mL")
    print(f"   📊 Ratios: {second_ratios}")
    
    # Test 3: Statistics
    stats = color_optimizer.get_statistics()
    print(f"   📈 Total attempts: {stats.get('total_attempts', 0)}")
    print(f"   🎯 Best distance: {stats.get('best_distance', 'N/A')}")
    
    # Test 4: Multiple iterations to verify consistency
    print("3. Testing multiple iterations...")
    for i in range(3):
        color_optimizer.add_measurement(second_ratios, (190 + i*5, 150 + i*3, 130 + i*2))
        ratios = color_optimizer.recommend_next_ratios()
        total = sum(ratios.values())
        assert abs(total - 10.0) < 0.01, f"Iteration {i+1}: Expected 10.0 mL, got {total}"
        print(f"   ✅ Iteration {i+1} total: {total:.2f} mL")
    
    print("\n🎉 All API logic tests PASSED!")
    print("✅ Core logic correctly uses 10.0 mL normalization")
    return True

if __name__ == "__main__":
    success = test_api_logic()
    sys.exit(0 if success else 1)
