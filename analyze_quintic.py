#!/usr/bin/env python3
"""
Analyze quintic time scaling to find peak velocity multiplier
"""
import numpy as np
import matplotlib.pyplot as plt

def quintic_time_scaling(t, Tf):
    """Quintic time scaling function s(t)"""
    tau = t / Tf
    return 10 * tau**3 - 15 * tau**4 + 6 * tau**5

def quintic_velocity_scaling(t, Tf):
    """Derivative of quintic time scaling - velocity scaling"""
    tau = t / Tf
    return (30 * tau**2 - 60 * tau**3 + 30 * tau**4) / Tf

def analyze_quintic_scaling():
    """Find the peak velocity multiplier for quintic time scaling"""
    
    Tf = 1.0  # Normalized time
    t_values = np.linspace(0, Tf, 1000)
    
    # Calculate velocity scaling
    vel_scaling = [quintic_velocity_scaling(t, Tf) for t in t_values]
    
    # Find peak velocity
    max_vel_scaling = max(vel_scaling)
    
    print(f"Peak velocity scaling factor: {max_vel_scaling:.3f}")
    print(f"This means peak velocity = {max_vel_scaling:.3f} * (total_displacement / total_time)")
    
    return max_vel_scaling

if __name__ == "__main__":
    peak_factor = analyze_quintic_scaling()
    print(f"\nFor safe trajectory planning:")
    print(f"Required duration = {peak_factor:.3f} * max_displacement / max_velocity")
