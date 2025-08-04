#!/usr/bin/env python3
"""
Test script to verify the color generation produces diverse colors.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import generate_random_target_color, ColorOptimizer
import numpy as np

# Reset global state
from main import _hue_history, _cum_vol
_hue_history.clear()
_cum_vol[:] = 0

print("🎨 Testing color generation diversity...")
print("=" * 60)

hues = []
colors = []

for i in range(20):
    rgb = generate_random_target_color()
    hue = ColorOptimizer._hue_deg(rgb)
    hues.append(hue)
    colors.append(rgb)
    
    # Convert to hex for display
    hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    print(f"{i+1:2d}. RGB{rgb} → {hex_color} → Hue: {hue:6.1f}°")

print("\n" + "=" * 60)
print(f"📊 Hue Statistics:")
print(f"   Range: {min(hues):.1f}° to {max(hues):.1f}°")
print(f"   Mean: {np.mean(hues):.1f}°")
print(f"   Std Dev: {np.std(hues):.1f}°")

# Check distribution across color ranges
red_range = sum(1 for h in hues if (h >= 330 or h <= 30))
orange_range = sum(1 for h in hues if 30 < h <= 60)
yellow_range = sum(1 for h in hues if 60 < h <= 120)
green_range = sum(1 for h in hues if 120 < h <= 180)
cyan_range = sum(1 for h in hues if 180 < h <= 240)
blue_range = sum(1 for h in hues if 240 < h <= 300)
magenta_range = sum(1 for h in hues if 300 < h < 330)

print(f"\n🌈 Color Distribution:")
print(f"   Red (330-30°):     {red_range:2d} colors")
print(f"   Orange (30-60°):   {orange_range:2d} colors")
print(f"   Yellow (60-120°):  {yellow_range:2d} colors")
print(f"   Green (120-180°):  {green_range:2d} colors")
print(f"   Cyan (180-240°):   {cyan_range:2d} colors")
print(f"   Blue (240-300°):   {blue_range:2d} colors")
print(f"   Magenta (300-330°): {magenta_range:2d} colors")

if yellow_range > 15:
    print("⚠️  Still heavily biased toward yellow!")
else:
    print("✅ Better color diversity achieved!")
