#!/usr/bin/env python3
"""
Robot Bottle Squeezing Module
Provides functions for dynamically squeezing bottles with temporal control.
"""

from squeeze_bottle import squeeze_washing_bottle


def quick_squeeze(config_name: str = "dispensing_red_to_beaker"):
    """Quick 1-second squeeze with default parameters."""
    return squeeze_washing_bottle(duration=1.0, config_name=config_name)


def gentle_squeeze(duration: float = 2.0, config_name: str = "dispensing_red_to_beaker"):
    """Gentle squeeze with lighter pressure (0.4 radians)."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=0.4, config_name=config_name)


def firm_squeeze(duration: float = 2.0, config_name: str = "dispensing_red_to_beaker"):
    """Firm squeeze with tighter pressure (0.1 radians)."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=0.1, config_name=config_name)


def custom_squeeze(duration: float, angle: float, config_name: str = "dispensing_red_to_beaker"):
    """Custom squeeze with specified duration and angle."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=angle, config_name=config_name)


# Example usage functions
def laboratory_procedure_with_washing():
    """Example procedure that includes bottle washing steps."""
    print("🧪 Starting laboratory procedure with washing steps...")
    
    # Step 1: Move to dispensing position
    print("📍 Step 1: Moving to dispensing position...")
    # This would be handled by the configuration loading in squeeze_washing_bottle
    
    # Step 2: Squeeze bottle to dispense washing solution
    print("💧 Step 2: Squeezing washing bottle...")
    success = firm_squeeze(duration=3.0)
    
    if success:
        print("✅ Laboratory washing procedure completed successfully!")
        return True
    else:
        print("❌ Laboratory washing procedure failed!")
        return False


if __name__ == "__main__":
    # Demo the different squeeze functions
    print("🧴 Demonstrating different squeeze functions...\n")
    
    print("1. Quick squeeze (1s, default angle):")
    quick_squeeze()
    
    print("\n2. Gentle squeeze (2s, 0.4 rad):")
    gentle_squeeze()
    
    print("\n3. Firm squeeze (2s, 0.1 rad):")
    firm_squeeze()
    
    print("\n4. Custom squeeze (1.5s, 0.25 rad):")
    custom_squeeze(1.5, 0.25)
