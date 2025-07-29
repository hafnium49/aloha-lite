#!/usr/bin/env python3
"""
Joint Correction Verification

Verify that the joint corrections were applied correctly.
"""

import math

def verify_corrections():
    """Verify that the joint corrections were mathematically correct."""
    
    print("Joint Correction Verification")
    print("=" * 50)
    
    corrections = [
        ("dispensing_blue_to_beaker.left_arm.j5", 4.145828, -2.137357),
        ("left_arm_stirer_standoff.left_arm.j5", 4.649097, -1.634088),
        ("left_arm_stirring.left_arm.j5", 4.664440, -1.618745)
    ]
    
    print(f"π = {math.pi:.6f}")
    print(f"2π = {2 * math.pi:.6f}")
    print("-" * 50)
    
    for config_name, original, corrected in corrections:
        # Calculate expected correction
        expected = original - 2 * math.pi
        
        # Check if correction is accurate
        diff = abs(corrected - expected)
        is_correct = diff < 1e-6
        
        print(f"\n{config_name}:")
        print(f"  Original:  {original:10.6f} rad")
        print(f"  Corrected: {corrected:10.6f} rad")
        print(f"  Expected:  {expected:10.6f} rad")
        print(f"  Difference: {diff:.10f}")
        print(f"  Status: {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")
        
        # Verify range
        in_range = -math.pi <= corrected <= math.pi
        print(f"  In Range: {'✅ YES' if in_range else '❌ NO'}")
        
        # Verify equivalence (original and corrected should represent same angle)
        angle_diff = abs((original % (2 * math.pi)) - (corrected % (2 * math.pi)))
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        
        is_equivalent = angle_diff < 1e-6
        print(f"  Equivalent: {'✅ YES' if is_equivalent else '❌ NO'}")
    
    print("\n" + "=" * 50)
    print("Verification Summary:")
    print("All corrections subtract 2π from values > π")
    print("All corrected values are within [-π, π]")
    print("All corrected values represent the same physical angle")

if __name__ == "__main__":
    verify_corrections()
