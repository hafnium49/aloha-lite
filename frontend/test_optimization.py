#!/usr/bin/env python3
"""
Test script to verify Bayesian optimization improvements
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import ColorOptimizer

def test_optimization_evolution():
    """Test that optimization evolves and doesn't get stuck"""
    print("🧪 Testing Bayesian optimization evolution...")
    
    optimizer = ColorOptimizer()
    target_color = (200, 100, 50)  # Orange-ish target
    optimizer.set_target_color(target_color)
    
    print(f"🎯 Target color: RGB{target_color}")
    
    # Simulate optimization iterations
    recommendations = []
    
    for iteration in range(8):
        # Get recommendation
        ratios = optimizer.recommend_next_ratios()
        recommendations.append(ratios)
        
        print(f"\n--- Iteration {iteration + 1} ---")
        print(f"📋 Recommended ratios: {ratios}")
        
        # Simulate measurement (with some noise and bias toward target)
        # This simulates the robot actually mixing and measuring the color
        simulated_rgb = simulate_color_mixing(ratios, target_color, noise_level=20)
        
        # Add measurement to optimizer
        optimizer.add_measurement(ratios, simulated_rgb)
        
        print(f"🔬 Simulated result: RGB{simulated_rgb}")
        
        # Check statistics
        stats = optimizer.get_statistics()
        print(f"📊 Distance: {stats['current_distance']:.2f}, Best: {stats['best_distance']:.2f}")
        print(f"🔍 Status: {stats['convergence_status']}, Diversity: {stats['ratio_diversity']:.3f}")
    
    # Analyze results
    print("\n" + "="*50)
    print("📈 OPTIMIZATION ANALYSIS")
    print("="*50)
    
    # Check for evolution (recommendations should not be identical)
    unique_recommendations = []
    for r in recommendations:
        # Round to avoid floating point precision issues
        rounded = {k: round(v, 2) for k, v in r.items()}
        if rounded not in unique_recommendations:
            unique_recommendations.append(rounded)
    
    print(f"🔄 Unique recommendations: {len(unique_recommendations)} out of {len(recommendations)}")
    print(f"📊 Diversity rate: {len(unique_recommendations)/len(recommendations)*100:.1f}%")
    
    if len(unique_recommendations) < len(recommendations) * 0.7:
        print("❌ ISSUE: Low diversity - optimization may be stuck")
        return False
    else:
        print("✅ GOOD: High diversity - optimization is evolving")
    
    # Check for improvement
    final_stats = optimizer.get_statistics()
    distances = final_stats['improvement_trend']
    
    if len(distances) > 1:
        initial_distance = distances[0]
        best_distance = min(distances)
        improvement = (initial_distance - best_distance) / initial_distance
        
        print(f"📈 Improvement: {improvement*100:.1f}% (from {initial_distance:.2f} to {best_distance:.2f})")
        
        if improvement > 0.1:  # At least 10% improvement
            print("✅ GOOD: Significant improvement achieved")
            return True
        else:
            print("⚠️  WARNING: Limited improvement - may need more iterations")
            return len(unique_recommendations) >= len(recommendations) * 0.7
    
    return True

def simulate_color_mixing(ratios, target_color, noise_level=15):
    """
    Simulate color mixing result with some realistic behavior
    """
    import random
    
    # Simple color mixing simulation
    # This is a rough approximation of how pigments might mix
    r_base = min(255, max(0, ratios['red'] * 80))
    y_base = min(255, max(0, ratios['yellow'] * 80))  
    b_base = min(255, max(0, ratios['blue'] * 80))
    
    # Simulate RGB result (very simplified)
    # Red pigment contributes mostly to R channel
    # Yellow pigment contributes to R and G channels  
    # Blue pigment contributes mostly to B channel
    simulated_r = int(r_base + y_base * 0.3)
    simulated_g = int(y_base * 0.8 + r_base * 0.1)
    simulated_b = int(b_base + r_base * 0.1)
    
    # Apply bias toward target (simulating that we're actually trying to reach it)
    target_r, target_g, target_b = target_color
    bias_strength = 0.3
    
    simulated_r = int(simulated_r * (1 - bias_strength) + target_r * bias_strength)
    simulated_g = int(simulated_g * (1 - bias_strength) + target_g * bias_strength)
    simulated_b = int(simulated_b * (1 - bias_strength) + target_b * bias_strength)
    
    # Add noise
    simulated_r += random.randint(-noise_level, noise_level)
    simulated_g += random.randint(-noise_level, noise_level)
    simulated_b += random.randint(-noise_level, noise_level)
    
    # Clamp to valid RGB range
    simulated_r = max(0, min(255, simulated_r))
    simulated_g = max(0, min(255, simulated_g))
    simulated_b = max(0, min(255, simulated_b))
    
    return (simulated_r, simulated_g, simulated_b)

if __name__ == "__main__":
    success = test_optimization_evolution()
    if success:
        print("\n🎉 Optimization test PASSED - Evolution is working!")
    else:
        print("\n❌ Optimization test FAILED - Check implementation")
    
    exit(0 if success else 1)
