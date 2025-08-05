#!/usr/bin/env python3
"""Simple debug script to analyze yellow bias in color generation."""

import numpy as np
import json
from pathlib import Path
from math import atan2, degrees
import random

# Essential functions extracted from main.py
def _rgb_to_lab(rgb):
    """Convert RGB to CIELAB."""
    # Normalize RGB to [0, 1]
    r, g, b = np.array(rgb) / 255.0
    
    # sRGB to XYZ conversion
    def gamma_correct(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    
    r, g, b = map(gamma_correct, [r, g, b])
    
    # XYZ using sRGB matrix
    X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    # XYZ to CIELAB
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883  # D65 illuminant
    
    def f(t):
        return t ** (1/3) if t > 0.008856 else (7.787 * t + 16/116)
    
    fx = f(X / Xn)
    fy = f(Y / Yn)
    fz = f(Z / Zn)
    
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    
    return L, a, b

def _hue_deg(rgb):
    """Extract hue angle in degrees from RGB."""
    L, a, b = _rgb_to_lab(rgb)
    return degrees(atan2(b, a)) % 360

def _rgb_to_absorb(rgb):
    """Convert RGB to absorbance."""
    arr = np.asarray(rgb) / 255.0
    lin_rgb = np.power(arr, 2.2).clip(1e-4, 1)
    return -np.log10(lin_rgb)

def load_ground_truth_calibration():
    """Load ground truth calibration - simplified version."""
    ground_truth_dir = Path("/home/hafnium/aloha-lite/frontend/ground_truth_calibration")
    
    # Try to find RGB measurements for each color
    rgb_colors = {}
    colors = ["red", "yellow", "blue"]
    
    for color in colors:
        color_file = ground_truth_dir / f"{color}_solution_ground_truth.json"
        if color_file.exists():
            try:
                with open(color_file) as f:
                    data = json.load(f)
                rgb = data.get("color_measurement", {}).get("rgb")
                if rgb:
                    rgb_colors[color] = rgb
                    print(f"📊 Loaded {color}: RGB{rgb}")
            except Exception as e:
                print(f"⚠️ Error loading {color}: {e}")
    
    # Construct matrix from RGB measurements if available
    if len(rgb_colors) == 3:
        P_true = np.array([
            _rgb_to_absorb(rgb_colors["red"]) / 10.0,
            _rgb_to_absorb(rgb_colors["yellow"]) / 10.0,
            _rgb_to_absorb(rgb_colors["blue"]) / 10.0,
            np.array([0.0, 0.0, 0.0])  # white
        ])
        print("🔧 Constructed matrix from RGB measurements")
        print(f"Matrix:\n{P_true}")
        return P_true
    
    # Fallback matrix
    print("🎲 Using fallback matrix")
    np.random.seed(42)
    P_fallback = np.abs(np.random.normal(loc=0.3, scale=0.15, size=(3,3)))
    P_fallback = np.vstack([P_fallback, np.array([0.0, 0.0, 0.0])])
    return P_fallback

def test_color_generation():
    """Test color generation to find bias."""
    print("🔍 Loading calibration matrix...")
    P_matrix = load_ground_truth_calibration()
    
    print(f"\n🔬 Matrix Analysis:")
    print(f"Shape: {P_matrix.shape}")
    
    # Analyze pigment strengths
    pigments = ["red", "yellow", "blue", "white"]
    strengths = []
    for i, pigment in enumerate(pigments[:3]):  # Only colored pigments
        strength = np.linalg.norm(P_matrix[i, :])
        strengths.append(strength)
        print(f"{pigment:6}: strength={strength:.3f}, coeffs={P_matrix[i, :]}")
    
    # Check ratios
    print(f"\nRelative strengths:")
    print(f"  Yellow/Red ratio: {strengths[1]/strengths[0]:.2f}")
    print(f"  Yellow/Blue ratio: {strengths[1]/strengths[2]:.2f}")
    
    # Test color generation with this matrix
    print(f"\n🎨 Testing Color Generation:")
    hues = []
    
    for i in range(50):
        # Generate random pigment ratios (uniform distribution)
        raw_ratios = np.random.uniform(0.1, 5.0, 4)  # R, Y, B, W
        
        # Normalize (same logic as in main.py)
        ratio_dict = {pigments[j]: raw_ratios[j] for j in range(4)}
        coloured = {k: v for k, v in ratio_dict.items() if k != "white"}
        s = sum(coloured.values()) or 1.0
        f = min(1.0, 10.0 / s)
        normalized_dict = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
        normalized_dict["white"] = max(0.1, 10.0 - sum(normalized_dict.values()))
        
        # Convert to array and calculate RGB
        w = np.array([normalized_dict[p] for p in pigments])
        A = w @ P_matrix
        rgb_lin = 10 ** (-A)
        rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
        hue = _hue_deg(rgb8)
        hues.append(hue)
        
        if i < 10:  # Show first 10
            print(f"  Sample {i+1}: ratios={[f'{w[j]:.1f}' for j in range(3)]} -> RGB{rgb8} -> Hue {hue:.1f}°")
    
    # Analyze hue distribution
    print(f"\n📊 Hue Distribution (n=50):")
    print(f"  Range: {min(hues):.1f}° - {max(hues):.1f}°")
    print(f"  Mean: {np.mean(hues):.1f}°")
    print(f"  Std: {np.std(hues):.1f}°")
    
    # Count by sector
    sectors = [
        ("Red-Orange", 0, 60),
        ("Yellow-Green", 60, 120), 
        ("Green-Cyan", 120, 180),
        ("Cyan-Blue", 180, 240),
        ("Blue-Magenta", 240, 300),
        ("Magenta-Red", 300, 360)
    ]
    
    print(f"\n🎨 Sector Distribution:")
    for name, start, end in sectors:
        count = sum(1 for h in hues if start <= h < end or (start == 300 and h >= start))
        percentage = count / len(hues) * 100
        print(f"  {name:12} ({start:3}-{end:3}°): {count:2} colors ({percentage:4.1f}%)")
    
    return P_matrix, hues

if __name__ == "__main__":
    print("🚀 Simple Yellow Bias Debug Analysis\n")
    P_matrix, hues = test_color_generation()
    print("\n✅ Analysis complete!")
