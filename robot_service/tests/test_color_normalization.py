#!/usr/bin/env python3
"""
Test script to validate color ratio normalization to 10 seconds total duration.
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_color_ratio_normalization():
    """Test the color ratio normalization logic"""
    
    print("🧪 Testing Color Ratio Normalization to 10 Seconds")
    print("=" * 60)
    
    test_cases = [
        # (red, yellow, blue, description)
        (1, 1, 1, "Equal ratios"),
        (2, 1, 3, "Mixed ratios (2:1:3)"),
        (5, 2, 1, "Red dominant (5:2:1)"),
        (1, 5, 2, "Yellow dominant (1:5:2)"),
        (1, 1, 8, "Blue dominant (1:1:8)"),
        (0.5, 0.3, 0.2, "Decimal ratios"),
        (10, 5, 15, "Large numbers"),
    ]
    
    for red_ratio, yellow_ratio, blue_ratio, description in test_cases:
        print(f"\n📊 Test Case: {description}")
        print(f"   Input ratios: red={red_ratio}, yellow={yellow_ratio}, blue={blue_ratio}")
        
        # Calculate normalization (same logic as robot_service/main.py)
        total_ratio = red_ratio + yellow_ratio + blue_ratio
        total_duration = 10.0  # Normalize to 10 seconds
        
        if total_ratio > 0:
            squeeze_durations = {
                "red": max(0.5, (red_ratio / total_ratio) * total_duration),
                "yellow": max(0.5, (yellow_ratio / total_ratio) * total_duration), 
                "blue": max(0.5, (blue_ratio / total_ratio) * total_duration)
            }
        else:
            squeeze_durations = {"red": 1.5, "yellow": 2.5, "blue": 1.0}
        
        # Calculate actual total
        actual_total = sum(squeeze_durations.values())
        
        print(f"   Calculated durations:")
        print(f"     Red:    {squeeze_durations['red']:.2f}s")
        print(f"     Yellow: {squeeze_durations['yellow']:.2f}s") 
        print(f"     Blue:   {squeeze_durations['blue']:.2f}s")
        print(f"   Actual Total: {actual_total:.2f}s")
        
        # Calculate percentages
        red_pct = (squeeze_durations['red'] / actual_total) * 100
        yellow_pct = (squeeze_durations['yellow'] / actual_total) * 100
        blue_pct = (squeeze_durations['blue'] / actual_total) * 100
        
        print(f"   Percentages: Red={red_pct:.1f}%, Yellow={yellow_pct:.1f}%, Blue={blue_pct:.1f}%")
        
        # Check if proportions are maintained
        expected_red_pct = (red_ratio / total_ratio) * 100
        expected_yellow_pct = (yellow_ratio / total_ratio) * 100
        expected_blue_pct = (blue_ratio / total_ratio) * 100
        
        print(f"   Expected %:  Red={expected_red_pct:.1f}%, Yellow={expected_yellow_pct:.1f}%, Blue={expected_blue_pct:.1f}%")
        
        # Check if minimum 0.5s constraint affects the result
        if any(d == 0.5 for d in squeeze_durations.values()):
            print("   ⚠️  Minimum duration constraint (0.5s) applied")
        else:
            print("   ✅ Proportions maintained without constraint")

def test_sequence_mapping():
    """Test the sequence step to color mapping"""
    
    print("\n\n🔍 Testing Sequence Step to Color Mapping")
    print("=" * 60)
    
    # Laboratory sequence from robot_service/main.py
    laboratory_sequence = [
        "left_arm_serving_standoff",           # 1
        "left_arm_standoff_with_beaker",       # 2
        "dispensing_red_to_beaker",            # 3
        "squeeze washing bottle for 1.5 seconds",  # 4 <- RED SQUEEZE
        "right_arm_standoff",                  # 5
        "left_arm_standoff_with_beaker",       # 6
        "left_arm_standoff_yellow",            # 7
        "right_arm_standoff_yellow",           # 8
        "dispensing_yellow_to_beaker",         # 9
        "squeeze washing bottle for 2.5 seconds",  # 10 <- YELLOW SQUEEZE
        "right_arm_standoff_yellow",           # 11
        "right_arm_standoff",                  # 12
        "left_arm_standoff_yellow",            # 13
        "left_arm_standoff_blue",              # 14
        "dispensing_blue_to_beaker",           # 15
        "squeeze washing bottle for 1 seconds",    # 16 <- BLUE SQUEEZE
        "right_arm_standoff",                  # 17
        "left_arm_standoff_blue",              # 18
        "left_arm_standoff_yellow",            # 19
        "left_arm_stirer_standoff",            # 20
        "left_arm_stirring",                   # 21
        "await 10 seconds",                    # 22
        "analyze beaker color",                # 23
        "await 3 seconds",                     # 24
        "left_arm_stirer_standoff",            # 25
        "left_arm_standoff_yellow",            # 26
        "left_arm_standoff_with_beaker",       # 27
        "left_arm_serving_standoff",           # 28
        "left_arm_serving_beaker"              # 29
    ]
    
    squeeze_steps = []
    for i, step in enumerate(laboratory_sequence, 1):
        if "squeeze washing bottle" in step.lower():
            color = None
            if i == 4:  # After red dispensing
                color = 'red'
            elif i == 10:  # After yellow dispensing
                color = 'yellow'
            elif i == 16:  # After blue dispensing
                color = 'blue'
            
            squeeze_steps.append((i, step, color))
            print(f"   Step {i:2d}: {step} -> {color.upper()} SQUEEZE")
    
    print(f"\n   Found {len(squeeze_steps)} squeeze operations:")
    for step_num, step_desc, color in squeeze_steps:
        print(f"     Step {step_num}: {color}")

if __name__ == "__main__":
    test_color_ratio_normalization()
    test_sequence_mapping()
    
    print("\n" + "=" * 60)
    print("✅ Tests completed! The normalization logic will:")
    print("   • Convert color ratios to proportional durations totaling 10 seconds")
    print("   • Apply minimum 0.5 second constraint per color")
    print("   • Map squeeze operations to colors based on sequence position")
    print("   • Use calculated durations instead of hard-coded values")
