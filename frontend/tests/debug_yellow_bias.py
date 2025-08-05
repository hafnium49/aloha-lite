#!/usr/bin/env python3
"""Debug script to analyze yellow bias in color generation."""

import sys
import os
import numpy as np
import json
from pathlib import Path
from math import atan2, degrees
import random

# Add the frontend directory to path
sys.path.append('/home/hafnium/aloha-lite/frontend')

# Mock missing imports to avoid FastAPI dependency
class MockFastAPI:
    pass
class MockRequest:
    pass
class MockHTTPException:
    pass

sys.modules['fastapi'] = MockFastAPI()
sys.modules['fastapi.responses'] = MockFastAPI()
sys.modules['fastapi.middleware.cors'] = MockFastAPI()

# Set mock objects
import builtins
builtins.FastAPI = MockFastAPI
builtins.Request = MockRequest
builtins.HTTPException = MockHTTPException
builtins.HTMLResponse = object
builtins.CORSMiddleware = object

# Import the main module functions
from main import generate_random_target_color, bottle_model, ColorOptimizer, load_ground_truth_calibration

def analyze_color_generation(n_samples=50):
    """Generate colors and analyze their hue distribution."""
    print("🔍 Analyzing color generation bias...")
    
    # Generate colors and collect hues
    hues = []
    colors = []
    
    for i in range(n_samples):
        rgb = generate_random_target_color()
        hue = ColorOptimizer._hue_deg(rgb)
        hues.append(hue)
        colors.append(rgb)
        if i < 10:  # Show first 10 examples
            print(f"  Sample {i+1}: RGB{rgb} -> Hue {hue:.1f}°")
    
    # Analyze hue distribution
    print(f"\n📊 Hue Analysis (n={n_samples}):")
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
        percentage = count / n_samples * 100
        print(f"  {name:12} ({start:3}-{end:3}°): {count:2} colors ({percentage:4.1f}%)")
    
    return hues, colors

def analyze_calibration_matrix():
    """Analyze the ground truth calibration matrix for bias."""
    print("\n🔬 Calibration Matrix Analysis:")
    P = bottle_model.P_est
    print(f"Matrix shape: {P.shape}")
    print(f"Matrix:\n{P}")
    
    # Analyze each pigment's contribution
    pigments = ["red", "yellow", "blue", "white"]
    for i, pigment in enumerate(pigments):
        row = P[i, :]
        strength = np.linalg.norm(row)
        print(f"{pigment:6}: strength={strength:.3f}, coeffs={row}")
    
    # Check if yellow is disproportionately strong
    yellow_strength = np.linalg.norm(P[1, :])  # Yellow is index 1
    red_strength = np.linalg.norm(P[0, :])
    blue_strength = np.linalg.norm(P[2, :])
    
    print(f"\nRelative strengths:")
    print(f"  Yellow/Red ratio: {yellow_strength/red_strength:.2f}")
    print(f"  Yellow/Blue ratio: {yellow_strength/blue_strength:.2f}")
    
    return P

def test_sampling_strategies():
    """Test different sampling strategies to see which creates bias."""
    print("\n🧪 Testing Sampling Strategies:")
    
    n_test = 100
    strategies = ["uniform", "beta", "lognormal", "targeted"]
    
    for strategy_idx in range(4):
        print(f"\n  Strategy {strategy_idx} ({strategies[strategy_idx]}):")
        hues = []
        
        for _ in range(n_test):
            # Manually replicate the sampling logic from generate_random_target_color
            if strategy_idx == 0:
                # Strategy 1: Uniform distribution
                raw_ratios = np.random.uniform(0.1, 8.0, 4)  # 4 pigments
            elif strategy_idx == 1:
                # Strategy 2: Beta distribution
                raw_ratios = np.random.beta(1.5, 1.5, 4) * 6.0 + 0.2
            elif strategy_idx == 2:
                # Strategy 3: Log-normal
                raw_ratios = np.random.lognormal(0.5, 0.8, 4)
                raw_ratios = np.clip(raw_ratios, 0.1, 12.0)
            else:
                # Strategy 4: Uniform fallback
                raw_ratios = np.random.uniform(0.1, 6.0, 4)
            
            # Apply normalization (same as in generate_random_target_color)
            pigments = ["red", "yellow", "blue", "white"]
            ratio_dict = {pigments[i]: raw_ratios[i] for i in range(4)}
            coloured = {k: v for k, v in ratio_dict.items() if k != "white"}
            s = sum(coloured.values()) or 1.0
            f = min(1.0, 10.0 / s)
            normalized_dict = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
            normalized_dict["white"] = max(0.1, 10.0 - sum(normalized_dict.values()))
            
            # Enforce minimum solvent
            if normalized_dict["white"] < 0.1:
                deficit = 0.1 - normalized_dict["white"]
                scale = (sum(normalized_dict.values()) - deficit) / sum(normalized_dict.values())
                for k in ('red', 'yellow', 'blue'):
                    normalized_dict[k] *= scale
                normalized_dict["white"] = 0.1
            
            # Convert to array and calculate RGB
            w = np.array([normalized_dict[p] for p in pigments])
            A = w @ bottle_model.P_est
            rgb_lin = 10 ** (-A)
            rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
            hue = ColorOptimizer._hue_deg(rgb8)
            hues.append(hue)
        
        # Analyze this strategy's results
        print(f"    Range: {min(hues):.1f}° - {max(hues):.1f}°")
        print(f"    Mean: {np.mean(hues):.1f}°")
        print(f"    Yellow sector (60-120°): {sum(1 for h in hues if 60 <= h < 120)} colors ({sum(1 for h in hues if 60 <= h < 120)/len(hues)*100:.1f}%)")

def check_ground_truth_files():
    """Check what ground truth files are available."""
    print("\n📁 Ground Truth Files:")
    gt_dir = Path("/home/hafnium/aloha-lite/frontend/ground_truth_calibration")
    
    if gt_dir.exists():
        for file in gt_dir.iterdir():
            if file.is_file():
                print(f"  {file.name}")
                if file.suffix == '.json':
                    try:
                        with open(file) as f:
                            data = json.load(f)
                        print(f"    Keys: {list(data.keys())}")
                    except Exception as e:
                        print(f"    Error reading: {e}")
    else:
        print("  Ground truth directory not found")

if __name__ == "__main__":
    print("🚀 Starting Color Generation Debug Analysis\n")
    
    # Check ground truth files
    check_ground_truth_files()
    
    # Analyze calibration matrix
    analyze_calibration_matrix()
    
    # Test sampling strategies individually
    test_sampling_strategies()
    
    # Analyze overall color generation
    hues, colors = analyze_color_generation(50)
    
    print("\n✅ Analysis complete!")
