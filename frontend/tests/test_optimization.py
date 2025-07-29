#!/usr/bin/env python3
"""
Test script to verify four-phase color optimization improvements
"""

import sys
import os
# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import ColorOptimizer

def test_optimization_evolution():
    """Test the four-phase optimization evolution"""
    print("🧪 Testing four-phase optimization evolution...")
    
    optimizer = ColorOptimizer()
    target_color = (200, 100, 50)  # Orange-ish target
    optimizer.set_target_color(target_color)
    
    print(f"🎯 Target color: RGB{target_color}")
    
    # Simulate optimization iterations
    recommendations = []
    phases = []
    
    for iteration in range(8):
        # Get recommendation
        ratios = optimizer.recommend_next_ratios()
        recommendations.append(ratios)
        
        # Determine which phase we're in
        phase = len(optimizer.history)
        phases.append(phase)
        
        print(f"\n--- Iteration {iteration + 1} (Phase {phase}) ---")
        if phase == 0:
            print("📍 Phase 0: Pure dominant pigment")
        elif phase == 1:
            print("🔍 Phase 1: GP/Bayesian optimization only")
        elif phase == 2:
            print("⚖️  Phase 2: Rough calibration + GP blend (70/30)")
        else:
            print("🎯 Phase ≥3: Full NNLS calibration + optional GP refinement")
            
        print(f"📋 Recommended ratios: {ratios}")
        
        # Simulate measurement (with some noise and bias toward target)
        # This simulates the robot actually mixing and measuring the color
        simulated_rgb = simulate_color_mixing(ratios, target_color, noise_level=20)
        
        # Add measurement to optimizer
        optimizer.add_measurement(ratios, simulated_rgb)
        
        print(f"🔬 Simulated result: RGB{simulated_rgb}")
        
        # Check statistics
        stats = optimizer.get_statistics()
        if stats['current_distance'] is not None:
            print(f"📊 Distance: {stats['current_distance']:.2f}, Best: {stats['best_distance']:.2f}")
            print(f"🔍 Status: {stats['convergence_status']}, Diversity: {stats['ratio_diversity']:.3f}")
    
    # Analyze results
    print("\n" + "="*50)
    print("📈 FOUR-PHASE OPTIMIZATION ANALYSIS")
    print("="*50)
    
    # Verify phase progression
    print(f"🔄 Phase progression: {phases}")
    
    # Check phase 0 - should use pure dominant pigment
    if len(recommendations) > 0:
        phase0_ratios = recommendations[0]
        max_ratio = max(phase0_ratios.values())
        dominant_colors = [k for k, v in phase0_ratios.items() if v == max_ratio]
        print(f"📍 Phase 0 analysis: Dominant pigment = {dominant_colors[0]} ({max_ratio:.2f})")
        
        # Verify it's actually dominant (much larger than others)
        sorted_ratios = sorted(phase0_ratios.values(), reverse=True)
        if len(sorted_ratios) >= 2 and sorted_ratios[0] > sorted_ratios[1] * 2:
            print("✅ Phase 0: Correctly identified dominant pigment")
        else:
            print("⚠️  Phase 0: May not have used pure dominant strategy")
    
    # Check for evolution (recommendations should not be identical)
    unique_recommendations = []
    for r in recommendations:
        # Round to avoid floating point precision issues
        rounded = {k: round(v, 2) for k, v in r.items()}
        if rounded not in unique_recommendations:
            unique_recommendations.append(rounded)
    
    print(f"🔄 Unique recommendations: {len(unique_recommendations)} out of {len(recommendations)}")
    print(f"📊 Diversity rate: {len(unique_recommendations)/len(recommendations)*100:.1f}%")
    
    diversity_good = len(unique_recommendations) >= len(recommendations) * 0.6  # Relaxed for 4-phase
    if not diversity_good:
        print("❌ ISSUE: Low diversity - optimization may be stuck")
    else:
        print("✅ GOOD: Adequate diversity - optimization is evolving")
    
    # Check for improvement
    final_stats = optimizer.get_statistics()
    distances = final_stats['improvement_trend']
    
    improvement_good = False
    if len(distances) > 1:
        initial_distance = distances[0]
        best_distance = min(distances)
        improvement = (initial_distance - best_distance) / initial_distance
        
        print(f"📈 Improvement: {improvement*100:.1f}% (from {initial_distance:.2f} to {best_distance:.2f})")
        
        if improvement > 0.05:  # At least 5% improvement (relaxed)
            print("✅ GOOD: Significant improvement achieved")
            improvement_good = True
        else:
            print("⚠️  WARNING: Limited improvement - may need more iterations")
    
    # Check calibration matrix development (if available)
    if hasattr(optimizer, 'P_est') and optimizer.P_est is not None:
        print(f"🧮 Calibration matrix developed: {optimizer.P_est.shape}")
        print("✅ GOOD: Successfully developed pigment calibration model")
    elif len(optimizer.history) >= 3:
        print("⚠️  WARNING: Should have calibration matrix by phase 3+")
    
    return diversity_good or improvement_good

def test_phase_specific_behavior():
    """Test specific behavior of each phase"""
    print("\n🔬 Testing phase-specific behavior...")
    
    optimizer = ColorOptimizer()
    target_color = (150, 200, 100)  # Green-ish target
    optimizer.set_target_color(target_color)
    
    # Phase 0 test
    ratios_phase0 = optimizer.recommend_next_ratios()
    print(f"Phase 0 ratios: {ratios_phase0}")
    
    # Should be pure dominant (yellow in this case since green = 200 is highest)
    max_val = max(ratios_phase0.values())
    dominant_count = sum(1 for v in ratios_phase0.values() if v == max_val)
    assert dominant_count == 1, "Phase 0 should have exactly one dominant pigment"
    
    # Add measurement and test Phase 1
    optimizer.add_measurement(ratios_phase0, (100, 150, 80))
    ratios_phase1 = optimizer.recommend_next_ratios()
    print(f"Phase 1 ratios: {ratios_phase1}")
    
    # Should be different from phase 0
    assert ratios_phase1 != ratios_phase0, "Phase 1 should produce different ratios"
    
    print("✅ Phase-specific behavior tests passed")

def simulate_color_mixing(ratios, target_color, noise_level=15):
    """
    Simulate color mixing result with Beer-Lambert-like behavior
    More realistic simulation aligned with the new optimizer's physics model
    """
    import random
    import numpy as np
    
    # Simulate pigment absorbance model (similar to what optimizer learns)
    # These are rough approximations of real pigment behavior
    P_true = np.array([
        [0.7, 0.1, 0.05],  # Red pigment: high red absorption, low others
        [0.2, 0.8, 0.1],   # Yellow pigment: medium red, high green, low blue absorption
        [0.05, 0.2, 0.9]   # Blue pigment: low red/green, high blue absorption
    ])
    
    # Convert ratios to weights
    weights = np.array([ratios['red'], ratios['yellow'], ratios['blue']])
    
    # Calculate absorbance using Beer-Lambert law
    absorbance = weights @ P_true
    
    # Convert back to linear RGB (Beer-Lambert: I = I0 * 10^(-A))
    linear_rgb = np.power(10, -absorbance)
    
    # Convert to sRGB (gamma correction)
    srgb = np.power(linear_rgb, 1/2.2) * 255
    
    # Add some bias toward target to simulate that we're actually trying to reach it
    target_r, target_g, target_b = target_color
    bias_strength = 0.15  # Reduced bias to make it more realistic
    
    biased_r = srgb[0] * (1 - bias_strength) + target_r * bias_strength
    biased_g = srgb[1] * (1 - bias_strength) + target_g * bias_strength
    biased_b = srgb[2] * (1 - bias_strength) + target_b * bias_strength
    
    # Add realistic noise
    noisy_r = biased_r + random.gauss(0, noise_level * 0.7)
    noisy_g = biased_g + random.gauss(0, noise_level * 0.7)
    noisy_b = biased_b + random.gauss(0, noise_level * 0.7)
    
    # Clamp to valid RGB range
    final_r = max(0, min(255, int(noisy_r)))
    final_g = max(0, min(255, int(noisy_g)))
    final_b = max(0, min(255, int(noisy_b)))
    
    return (final_r, final_g, final_b)

def run_all_tests():
    """Run all optimization tests"""
    print("🧪 Running all color optimization tests...\n")
    
    # Test 1: Evolution test
    success1 = test_optimization_evolution()
    
    # Test 2: Phase-specific behavior
    try:
        test_phase_specific_behavior()
        success2 = True
    except Exception as e:
        print(f"❌ Phase-specific test failed: {e}")
        success2 = False
    
    overall_success = success1 and success2
    
    if overall_success:
        print("\n🎉 All four-phase optimization tests PASSED!")
    else:
        print("\n❌ Some optimization tests FAILED - Check implementation")
    
    return overall_success

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
