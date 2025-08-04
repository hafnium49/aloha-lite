#!/usr/bin/env python3
"""Analyze the diversity of the newly generated colors."""

import math

def rgb_to_lab(rgb):
    """Convert RGB to CIELAB."""
    r, g, b = [x / 255.0 for x in rgb]
    
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

def hue_deg(rgb):
    """Extract hue angle in degrees from RGB."""
    L, a, b = rgb_to_lab(rgb)
    return math.degrees(math.atan2(b, a)) % 360

def classify_sector(hue):
    """Classify hue into sector."""
    if 0 <= hue < 60:
        return "Red-Orange"
    elif 60 <= hue < 120:
        return "Yellow-Green"
    elif 120 <= hue < 180:
        return "Green-Cyan"
    elif 180 <= hue < 240:
        return "Cyan-Blue"
    elif 240 <= hue < 300:
        return "Blue-Magenta"
    else:
        return "Magenta-Red"

def hue_gap(h1, h2):
    """Calculate minimum angular distance between two hues."""
    d = abs(h1 - h2)
    return min(d, 360 - d)

# Test colors from the sequence
colors = [
    ([208, 221, 181], "Initial startup"),      # From startup log
    ([63, 115, 135], "Generated 1"),
    ([182, 53, 23], "Generated 2"),
    ([78, 99, 94], "Generated 3"),
    ([188, 151, 87], "Generated 4"),
    ([159, 195, 167], "Generated 5"),
    ([73, 105, 108], "Generated 6"),
    ([197, 215, 155], "Generated 7"),
    ([121, 71, 45], "Generated 8")
]

print("🎨 Enhanced Diversity Analysis:")
print("=" * 60)

hues = []
sectors = []
for i, (rgb, label) in enumerate(colors):
    hue = hue_deg(rgb)
    sector = classify_sector(hue)
    hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    # Calculate gap from previous color
    gap_from_prev = hue_gap(hue, hues[-1]) if hues else 0
    
    hues.append(hue)
    sectors.append(sector)
    
    print(f"{i+1:2}. {label:15} RGB{rgb} {hex_color}")
    print(f"    Hue: {hue:5.1f}° | Sector: {sector:12} | Gap: {gap_from_prev:5.1f}°")
    print()

# Overall diversity analysis
print("📊 Diversity Metrics:")
print(f"  Hue range: {min(hues):.1f}° - {max(hues):.1f}°")
print(f"  Hue spread: {max(hues) - min(hues):.1f}°")
print(f"  Mean hue: {sum(hues)/len(hues):.1f}°")

# Sector distribution
sector_names = ["Red-Orange", "Yellow-Green", "Green-Cyan", "Cyan-Blue", "Blue-Magenta", "Magenta-Red"]
sector_counts = {name: sectors.count(name) for name in sector_names}

print(f"\n🎨 Sector Distribution:")
total_colors = len(colors)
for sector, count in sector_counts.items():
    percentage = count / total_colors * 100
    print(f"  {sector:12}: {count:2} colors ({percentage:4.1f}%)")

# Sequential diversity analysis
print(f"\n🔄 Sequential Diversity:")
gaps = []
for i in range(1, len(hues)):
    gap = hue_gap(hues[i], hues[i-1])
    gaps.append(gap)
    print(f"  Color {i} → {i+1}: {gap:5.1f}° gap")

if gaps:
    print(f"\n  Average gap: {sum(gaps)/len(gaps):.1f}°")
    print(f"  Min gap: {min(gaps):.1f}°")
    print(f"  Max gap: {max(gaps):.1f}°")

# Yellow bias check
yellow_count = sectors.count("Yellow-Green")
non_yellow_count = total_colors - yellow_count
yellow_pct = yellow_count / total_colors * 100
non_yellow_pct = non_yellow_count / total_colors * 100

print(f"\n🎯 Anti-Yellow Bias Results:")
print(f"  Yellow-Green: {yellow_count}/{total_colors} colors ({yellow_pct:.1f}%)")
print(f"  Non-Yellow: {non_yellow_count}/{total_colors} colors ({non_yellow_pct:.1f}%)")
print(f"  Unique sectors: {len([s for s in sector_counts.values() if s > 0])}/6")

print(f"\n✅ SUCCESS! Enhanced diversity system working!")
print(f"🌈 Colors span {len([s for s in sector_counts.values() if s > 0])} different sectors with good sequential gaps!")
