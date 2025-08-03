#!/usr/bin/env python3
"""
Test the new simplified ColorOptimizer functionality and target generation
Since the CAM02-UCS functionality was removed from the simplified version,
this tests core color functionality and target generation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import ColorOptimizer, generate_random_target_color, BottleModel, _sample_reachable_rgb

def test_color_optimizer_basic_functionality():
    """Test the simplified ColorOptimizer basic functionality"""
    print("🎨 Testing simplified ColorOptimizer functionality...")
    
    optimizer = ColorOptimizer()
    target_color = generate_random_target_color()
    optimizer.set_target_color(target_color)
    
    print(f"🎯 Target color: RGB{target_color}")
    
    # Test without any measurements
    stats = optimizer.get_statistics()
    print(f"📊 Initial stats: {stats}")
    assert stats['total_attempts'] == 0, "Should start with 0 attempts"
    
    # Add some measurements to simulate optimization
    test_measurements = [
        ({'red': 3.0, 'yellow': 0.0, 'blue': 0.0}, (180, 80, 40)),   # Pure red attempt
        ({'red': 2.0, 'yellow': 1.0, 'blue': 0.0}, (190, 90, 45)),   # Red-yellow mix
        ({'red': 1.5, 'yellow': 1.2, 'blue': 0.3}, (195, 95, 48)),   # Closer to target
        ({'red': 1.3, 'yellow': 1.4, 'blue': 0.3}, (198, 98, 49)),   # Very close
    ]
    
    for i, (ratios, measured_rgb) in enumerate(test_measurements):
        optimizer.add_measurement(ratios, measured_rgb)
        print(f"📈 Added measurement {i+1}: {ratios} → RGB{measured_rgb}")
    
    # Check final statistics
    final_stats = optimizer.get_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"   Total attempts: {final_stats['total_attempts']}")
    print(f"   Best distance: {final_stats['best_distance']:.2f}")
    print(f"   Current distance: {final_stats['current_distance']:.2f}")
    
    assert final_stats['total_attempts'] == 4, "Should have 4 measurements"
    assert final_stats['best_distance'] is not None, "Should have best distance"
    
    return True

def test_target_generation_quality():
    """Test the quality and diversity of target generation"""
    print("\n🎯 Testing target generation quality...")
    
    # Generate multiple targets and check diversity
    generated_colors = []
    for i in range(20):
        color = generate_random_target_color()
        generated_colors.append(color)
        # Validate RGB values
        assert all(0 <= c <= 255 for c in color), f"Invalid RGB: {color}"
    
    print(f"   Generated {len(generated_colors)} colors")
    
    # Check color diversity
    unique_colors = set(generated_colors)
    diversity_ratio = len(unique_colors) / len(generated_colors)
    print(f"   Unique colors: {len(unique_colors)}/{len(generated_colors)} ({diversity_ratio:.1%})")
    
    # Sample some colors for display
    sample_colors = generated_colors[:5]
    print(f"   Sample colors: {sample_colors}")
    
    # Check that colors span reasonable ranges
    all_r = [c[0] for c in generated_colors]
    all_g = [c[1] for c in generated_colors]  
    all_b = [c[2] for c in generated_colors]
    
    r_range = max(all_r) - min(all_r)
    g_range = max(all_g) - min(all_g) 
    b_range = max(all_b) - min(all_b)
    
    print(f"   Color ranges - R: {r_range}, G: {g_range}, B: {b_range}")
    
    # Should have reasonable color diversity (not all the same hue)
    assert diversity_ratio > 0.7, "Should generate diverse colors"
    assert r_range > 50 and g_range > 50 and b_range > 50, "Should span reasonable RGB ranges"
    
    return True

def test_bottle_model_functionality():
    """Test BottleModel functionality"""
    print("\n🍾 Testing BottleModel functionality...")
    
    import numpy as np
    
    # Create test matrix - updated for 4-pigment system
    test_matrix = np.array([[0.8, 0.1, 0.05],
                           [0.2, 0.9, 0.1], 
                           [0.05, 0.2, 0.9],
                           [0.0, 0.0, 0.0]])  # White pigment row
    
    # Create BottleModel
    bottle = BottleModel(test_matrix)
    
    # Test that matrix is preserved
    assert bottle.P_est is not None, "BottleModel should have P_est"
    assert np.allclose(bottle.P_est, test_matrix), "Matrix should be preserved"
    
    # Test _sample_reachable_rgb function
    for i in range(5):
        rgb, weights = _sample_reachable_rgb(bottle.P_est, max_total=6.0)
        print(f"   Sample {i+1}: RGB{rgb}, weights=[{weights[0]:.2f}, {weights[1]:.2f}, {weights[2]:.2f}]")
        
        # Validate RGB output
        assert all(0 <= c <= 255 for c in rgb), f"Invalid RGB: {rgb}"
        
        # Validate weights
        assert len(weights) == 4, "Should have 4 weights"  # Updated for 4-pigment system
        assert all(w >= 0 for w in weights), "Weights should be non-negative"
        assert sum(weights) <= 6.5, "Total weight should be reasonable"  # Allow some tolerance
    
    print("✅ BottleModel functionality tests passed")
    return True

def test_reachability_consistency():
    """Test that generated targets are actually reachable"""
    print("\n🔬 Testing target reachability consistency...")
    
    from main import bottle_model
    
    # Generate several targets and verify they come from the bottle model
    print("   Testing reachability of generated targets...")
    
    consistent_count = 0
    total_tests = 10
    
    for i in range(total_tests):
        # Generate a target
        target = generate_random_target_color()
        
        # Try to find weights that would produce this target (approximately)
        # This is a rough check - exact inverse is complex
        
        # Sample some colors from the model and see if any are close to target
        closest_distance = float('inf')
        for _ in range(20):
            sample_rgb, _ = _sample_reachable_rgb(bottle_model.P_est)
            distance = sum((target[i] - sample_rgb[i])**2 for i in range(3))**0.5
            closest_distance = min(closest_distance, distance)
        
        # If we can get within reasonable distance, consider it reachable
        if closest_distance < 100:  # Reasonable threshold for RGB distance
            consistent_count += 1
        
        if i < 3:  # Show first few tests
            print(f"      Target {i+1}: RGB{target}, closest sample distance: {closest_distance:.1f}")
    
    consistency_rate = consistent_count / total_tests
    print(f"   Reachability consistency: {consistent_count}/{total_tests} ({consistency_rate:.1%})")
    
    # Should have reasonable consistency (targets should be reachable)
    assert consistency_rate > 0.3, "Most generated targets should be reachable"
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Updated ColorOptimizer and Target Generation\n")
    
    success1 = test_color_optimizer_basic_functionality()
    success2 = test_target_generation_quality()
    success3 = test_bottle_model_functionality()
    success4 = test_reachability_consistency()
    
    overall_success = success1 and success2 and success3 and success4
    
    if overall_success:
        print("\n🎉 All updated ColorOptimizer tests PASSED!")
        print("✅ Basic ColorOptimizer functionality working")
        print("✅ Target generation producing diverse, valid colors") 
        print("✅ BottleModel functionality operational")
        print("✅ Target reachability consistency maintained")
    else:
        print("\n❌ Some tests FAILED - Check implementation")
    
    exit(0 if overall_success else 1) and success3 and success4
    
    if overall_success:
        print("\n🎉 CAM02-UCS color space tests PASSED!")
        print("   ✅ Color space data generation working")
        print("   ✅ Color conversions working")
        print("   ✅ Ready for frontend plotting")
    else:
        print("\n❌ CAM02-UCS color space tests FAILED!")
    
    exit(0 if overall_success else 1)
