#!/usr/bin/env python3
"""
Robot Bottle Squeezing Module
Provides functions for dynamically squeezing bottles with temporal control using the enhanced partial configuration system.
"""

from squeeze_bottle import squeeze_washing_bottle, squeeze_washing_bottle_simple


def quick_squeeze(base_config_name: str = "dispensing_red_to_beaker"):
    """Quick 1-second squeeze with default parameters using simple method."""
    return squeeze_washing_bottle_simple(duration=1.0)


def gentle_squeeze(duration: float = 2.0, base_config_name: str = "dispensing_red_to_beaker"):
    """Gentle squeeze with lighter pressure (0.4 radians)."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=0.4, base_config_name=base_config_name)


def firm_squeeze(duration: float = 2.0, base_config_name: str = "dispensing_red_to_beaker"):
    """Firm squeeze with tighter pressure (0.1 radians)."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=0.1, base_config_name=base_config_name)


def custom_squeeze(duration: float, angle: float, base_config_name: str = "dispensing_red_to_beaker", release_config_name: str = None):
    """Custom squeeze with specified duration and angle."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=angle, base_config_name=base_config_name, release_config_name=release_config_name)


def ultra_gentle_squeeze(duration: float = 2.0, base_config_name: str = "dispensing_red_to_beaker"):
    """Ultra gentle squeeze with very light pressure (0.5 radians)."""
    return squeeze_washing_bottle(duration=duration, squeeze_angle=0.5, base_config_name=base_config_name)


def precision_squeeze(duration: float = 1.5, base_config_name: str = "dispensing_red_to_beaker"):
    """Precision squeeze using predefined partial configuration."""
    return squeeze_washing_bottle_simple(duration=duration)


# Enhanced laboratory procedures using partial configuration system
def laboratory_procedure_with_washing():
    """Example procedure that includes bottle washing steps using enhanced system."""
    print("🧪 Starting laboratory procedure with washing steps using partial configuration system...")
    
    # Step 1: Move to dispensing position (handled automatically by base configuration)
    print("📍 Step 1: Using base configuration positioning...")
    
    # Step 2: Squeeze bottle to dispense washing solution
    print("💧 Step 2: Squeezing washing bottle with firm pressure...")
    success = firm_squeeze(duration=3.0)
    
    if success:
        print("✅ Laboratory washing procedure completed successfully!")
        return True
    else:
        print("❌ Laboratory washing procedure failed!")
        return False


def multi_step_bottle_procedure():
    """Multi-step procedure demonstrating different squeeze types."""
    print("🔬 Starting multi-step bottle procedure...")
    
    # Step 1: Precision squeeze for initial setup
    print("🎯 Step 1: Precision squeeze for setup...")
    if not precision_squeeze(duration=1.0):
        return False
    
    # Step 2: Gentle squeeze for main operation
    print("🤲 Step 2: Gentle squeeze for main operation...")
    if not gentle_squeeze(duration=2.5):
        return False
    
    # Step 3: Quick final squeeze
    print("⚡ Step 3: Quick final squeeze...")
    if not quick_squeeze():
        return False
    
    print("✅ Multi-step bottle procedure completed successfully!")
    return True


def advanced_bottle_workflow(base_config: str = "dispensing_red_to_beaker", release_config: str = "standoff_configuration_stage1"):
    """Advanced workflow with custom base and release configurations."""
    print(f"🚀 Starting advanced bottle workflow...")
    print(f"📋 Base config: {base_config}")
    print(f"🔄 Release config: {release_config}")
    
    # Custom squeeze with different release position
    success = custom_squeeze(
        duration=2.0, 
        angle=0.25, 
        base_config_name=base_config,
        release_config_name=release_config
    )
    
    if success:
        print("✅ Advanced bottle workflow completed successfully!")
        return True
    else:
        print("❌ Advanced bottle workflow failed!")
        return False


if __name__ == "__main__":
    # Demo the different squeeze functions using enhanced partial configuration system
    print("🧴 Demonstrating enhanced squeeze functions with partial configuration system...\n")
    
    print("1. Precision squeeze (simple method with predefined config):")
    precision_squeeze(duration=1.0)
    
    print("\n2. Quick squeeze (simple method, 1s):")
    quick_squeeze()
    
    print("\n3. Gentle squeeze (2s, 0.4 rad):")
    gentle_squeeze()
    
    print("\n4. Firm squeeze (2s, 0.1 rad):")
    firm_squeeze()
    
    print("\n5. Ultra gentle squeeze (2s, 0.5 rad):")
    ultra_gentle_squeeze()
    
    print("\n6. Custom squeeze (1.5s, 0.25 rad):")
    custom_squeeze(1.5, 0.25)
    
    print("\n7. Advanced workflow with custom configurations:")
    advanced_bottle_workflow(
        base_config="dispensing_red_to_beaker",
        release_config="standoff_configuration_stage1"
    )
    
    print("\n8. Multi-step bottle procedure:")
    multi_step_bottle_procedure()
    
    print("\n9. Laboratory procedure with washing:")
    laboratory_procedure_with_washing()
