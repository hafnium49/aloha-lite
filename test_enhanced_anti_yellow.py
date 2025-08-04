#!/usr/bin/env python3
"""Test the enhanced anti-yellow bias color generation."""

import numpy as np
import json
from pathlib import Path
from math import atan2, degrees
import random

# Essential functions extracted from main.py (updated)
def _rgb_to_lab(rgb):
    """Convert RGB to CIELAB."""
    r, g, b = np.array(rgb) / 255.0
    
    def gamma_correct(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    
    r, g, b = map(gamma_correct, [r, g, b])
    
    X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
    
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883
    
    def f(t):
        return t ** (1/3) if t > 0.008856 else (7.787 * t + 16/116)
    
    fx, fy, fz = f(X / Xn), f(Y / Yn), f(Z / Zn)
    
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
    """Load ground truth calibration."""
    ground_truth_dir = Path("/home/hafnium/aloha-lite/frontend/ground_truth_calibration")
    
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
            except:
                pass
    
    if len(rgb_colors) == 3:
        P_true = np.array([
            _rgb_to_absorb(rgb_colors["red"]) / 10.0,
            _rgb_to_absorb(rgb_colors["yellow"]) / 10.0,
            _rgb_to_absorb(rgb_colors["blue"]) / 10.0,
            np.array([0.0, 0.0, 0.0])
        ])
        return P_true
    
    # Fallback
    np.random.seed(42)
    P_fallback = np.abs(np.random.normal(loc=0.3, scale=0.15, size=(3,3)))
    P_fallback = np.vstack([P_fallback, np.array([0.0, 0.0, 0.0])])
    return P_fallback

def test_enhanced_color_generation():
    """Test the enhanced anti-yellow bias color generation."""
    print("🚀 Testing Enhanced Anti-Yellow Bias Color Generation\n")
    
    P_matrix = load_ground_truth_calibration()
    pigments = ["red", "yellow", "blue", "white"]
    hues = []
    
    print("🔧 Using extreme sampling strategies to overcome matrix bias...")
    
    # Test each strategy separately
    strategies = [
        "Extreme red dominance", 
        "Extreme blue dominance", 
        "Red+Blue mix (purple)", 
        "High solvent dilution",
        "Targeted sector sampling",
        "Power-law extremes"
    ]
    
    for strategy_idx in range(6):
        print(f"\n🧪 Strategy {strategy_idx}: {strategies[strategy_idx]}")
        strategy_hues = []
        
        for i in range(20):  # 20 samples per strategy
            if strategy_idx == 0:
                # Extreme red dominance
                raw_ratios = np.array([
                    np.random.uniform(8.0, 20.0),  # Very high red
                    np.random.uniform(0.1, 1.0),   # Minimal yellow
                    np.random.uniform(0.1, 3.0),   # Low blue
                    np.random.uniform(0.1, 2.0)    # White
                ])
            elif strategy_idx == 1:
                # Extreme blue dominance
                raw_ratios = np.array([
                    np.random.uniform(0.1, 2.0),   # Low red
                    np.random.uniform(0.1, 1.0),   # Minimal yellow
                    np.random.uniform(8.0, 25.0),  # Very high blue
                    np.random.uniform(0.1, 2.0)    # White
                ])
            elif strategy_idx == 2:
                # Red+Blue mix avoiding yellow
                raw_ratios = np.array([
                    np.random.uniform(3.0, 12.0),  # High red
                    np.random.uniform(0.1, 0.5),   # Trace yellow only
                    np.random.uniform(3.0, 12.0),  # High blue
                    np.random.uniform(0.1, 2.0)    # White
                ])
            elif strategy_idx == 3:
                # High solvent dilution
                raw_ratios = np.array([
                    np.random.uniform(0.5, 3.0),   # Moderate red
                    np.random.uniform(0.1, 1.0),   # Low yellow
                    np.random.uniform(0.5, 3.0),   # Moderate blue
                    np.random.uniform(8.0, 15.0)   # Very high white
                ])
            elif strategy_idx == 4:
                # Anti-yellow sampling
                raw_ratios = np.array([
                    np.random.uniform(5.0, 15.0),  # High red
                    np.random.uniform(0.1, 1.0),   # Suppress yellow
                    np.random.uniform(5.0, 15.0),  # High blue
                    np.random.uniform(0.1, 3.0)    # White
                ])
            else:
                # Power-law extremes
                alpha = 0.5
                raw_ratios = np.array([
                    np.random.power(alpha) * 20.0 + 0.1,  # Red
                    np.random.power(2.0) * 3.0 + 0.1,     # Yellow (suppressed)
                    np.random.power(alpha) * 20.0 + 0.1,  # Blue
                    np.random.uniform(0.1, 5.0)           # White
                ])
            
            # Normalize with higher max_total
            ratio_dict = {pigments[j]: raw_ratios[j] for j in range(4)}
            coloured = {k: v for k, v in ratio_dict.items() if k != "white"}
            s = sum(coloured.values()) or 1.0
            max_total = 15.0  # Increased limit
            f = min(1.0, max_total / s)
            normalized_dict = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
            normalized_dict["white"] = max(0.1, max_total - sum(normalized_dict.values()))
            
            if normalized_dict["white"] < 0.1:
                deficit = 0.1 - normalized_dict["white"]
                scale = (sum(normalized_dict.values()) - deficit) / sum(normalized_dict.values())
                for k in ('red', 'yellow', 'blue'):
                    normalized_dict[k] *= scale
                normalized_dict["white"] = 0.1
                
            # Calculate RGB
            w = np.array([normalized_dict[p] for p in pigments])
            A = w @ P_matrix
            rgb_lin = 10 ** (-A)
            rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
            hue = _hue_deg(rgb8)
            
            strategy_hues.append(hue)
            hues.append(hue)
            
            if i < 3:  # Show first 3 examples per strategy
                print(f"  Sample {i+1}: ratios=[{w[0]:.1f}, {w[1]:.1f}, {w[2]:.1f}] -> RGB{rgb8} -> Hue {hue:.1f}°")
        
        # Analyze this strategy
        yellow_count = sum(1 for h in strategy_hues if 60 <= h < 120)
        non_yellow_count = len(strategy_hues) - yellow_count
        print(f"  Results: {non_yellow_count}/20 non-yellow colors ({non_yellow_count/20*100:.1f}%)")
        print(f"  Hue range: {min(strategy_hues):.1f}° - {max(strategy_hues):.1f}°")
    
    # Overall analysis
    print(f"\n📊 Overall Results (n={len(hues)}):")
    print(f"  Range: {min(hues):.1f}° - {max(hues):.1f}°")
    print(f"  Mean: {np.mean(hues):.1f}°")
    print(f"  Std: {np.std(hues):.1f}°")
    
    # Sector distribution
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
    
    yellow_green_pct = sum(1 for h in hues if 60 <= h < 120) / len(hues) * 100
    non_yellow_pct = 100 - yellow_green_pct
    
    print(f"\n🎯 Anti-Yellow Bias Results:")
    print(f"  Yellow-Green sector: {yellow_green_pct:.1f}%")
    print(f"  Non-Yellow colors: {non_yellow_pct:.1f}%")
    print(f"  Improvement: {'✅ SUCCESS' if yellow_green_pct < 40 else '⚠️ NEEDS MORE WORK'}")

if __name__ == "__main__":
    test_enhanced_color_generation()
