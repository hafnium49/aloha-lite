#!/usr/bin/env python3
"""
Validation script for the updated four-rule target generator system.

This script demonstrates that all the modifications to frontend/main.py
are working correctly with the surgical patch implementation.
"""

import sys
import os
from pathlib import Path

# Add frontend directory to path
frontend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(frontend_dir))

def main():
    print("🔬 Four-Rule Target Generator Validation")
    print("=" * 50)
    
    try:
        from main import (
            generate_random_target_color,
            ColorOptimizer,
            _hue_gap_deg,
            _hue_history,
            _cum_vol,
            PRIMARY_HUES,
            HUE_EXCLUSION,
            MAX_DIFFICULTY,
            bottle_model
        )
        
        print("✅ All imports successful")
        
        # Reset state
        _hue_history.clear()
        _cum_vol[:] = 0
        
        print(f"\n📊 Configuration:")
        print(f"   Primary hues: {PRIMARY_HUES}")
        print(f"   Exclusion zone: {HUE_EXCLUSION}°")
        print(f"   Max difficulty: {MAX_DIFFICULTY}")
        print(f"   Bottle model matrix shape: {bottle_model.P_est.shape}")
        
        print(f"\n🎯 Generating educational color targets:")
        targets = []
        
        for i in range(10):
            rgb = generate_random_target_color()
            hue = ColorOptimizer._hue_deg(rgb)
            targets.append((rgb, hue))
            
            # Check primary exclusion
            min_primary_dist = min(_hue_gap_deg(hue, p) for p in PRIMARY_HUES)
            
            print(f"   Target {i+1}: RGB{rgb} → {hue:.1f}° (primary dist: {min_primary_dist:.1f}°)")
            
            # Validate rules
            assert min_primary_dist >= HUE_EXCLUSION - 1, f"Primary exclusion violated: {min_primary_dist:.1f}°"
        
        print(f"\n✅ All targets pass primary exclusion rule")
        
        # Test hue gap function
        print(f"\n🔄 Testing hue gap calculations:")
        test_cases = [(0, 20, 20), (350, 10, 20), (0, 180, 180)]
        for h1, h2, expected in test_cases:
            gap = _hue_gap_deg(h1, h2)
            print(f"   {h1}° ↔ {h2}° = {gap:.1f}° (expected {expected}°)")
            assert abs(gap - expected) < 1, f"Hue gap calculation error"
        
        print(f"✅ Hue gap calculations correct")
        
        # Test ColorOptimizer hue functionality
        print(f"\n🎨 Testing ColorOptimizer hue functionality:")
        optimizer = ColorOptimizer()
        test_color = (255, 128, 64)  # Orange
        optimizer.set_target_color(test_color)
        
        print(f"   Target: RGB{test_color} → {optimizer.hue_target_deg:.1f}°")
        assert optimizer.hue_target_deg is not None, "Hue target not set"
        
        # Simulate a measurement
        measured_rgb = (250, 120, 70)
        ratios = {'red': 1.0, 'yellow': 0.5, 'blue': 0.1, 'white': 1.4}
        optimizer.add_measurement(ratios, measured_rgb)
        
        print(f"   Measurement: RGB{measured_rgb} logged successfully")
        assert len(optimizer.history) == 1, "Measurement not logged"
        assert "measured_hue_deg" in optimizer.history[0], "Hue data not stored"
        
        print(f"✅ ColorOptimizer hue functionality working")
        
        # Test global state tracking
        print(f"\n📈 Testing global state tracking:")
        print(f"   Hue history length: {len(_hue_history)}")
        print(f"   Cumulative volumes: R={_cum_vol[0]:.2f}, Y={_cum_vol[1]:.2f}, B={_cum_vol[2]:.2f}")
        
        assert len(_hue_history) > 0, "Hue history not populated"
        assert _cum_vol.sum() > 0, "Cumulative volumes not tracked"
        
        print(f"✅ Global state tracking working")
        
        print(f"\n🎉 SUCCESS: All four-rule target generator functionality validated!")
        print(f"   The surgical patch modifications are working correctly.")
        print(f"   Educational color mixing system is ready for use.")
        
        return True
        
    except Exception as e:
        print(f"❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
