#!/usr/bin/env python3
"""
Demonstration script showing how the modified robot_service uses sequential_execute.py
with dynamic duration modification for squeeze bottle operations.
"""

import json
import tempfile
import os
from pathlib import Path

def create_example_modified_sequence():
    """Create an example of how the system modifies sequences dynamically."""
    
    # Load the original timed_laboratory_procedure
    sequences_file = Path(__file__).parent / "../temp_rules/sequential_sequences.json"
    
    try:
        with open(sequences_file, 'r') as f:
            sequences_data = json.load(f)
        
        original_sequence = sequences_data["predefined_sequences"]["timed_laboratory_procedure"]
        original_configs = original_sequence["configurations"]
        
        print("🔬 Original timed_laboratory_procedure sequence:")
        for i, step in enumerate(original_configs, 1):
            if "squeeze washing bottle" in step.lower():
                print(f"  {i:2d}. {step} ⬅️ Will be modified")
            else:
                print(f"  {i:2d}. {step}")
        
        # Simulate dynamic modification with custom color ratios
        color_ratios = {"red": 3.0, "yellow": 1.5, "blue": 0.5}  # Example ratios
        total_ratio = sum(color_ratios.values())
        
        # Calculate normalized durations (10 seconds total)
        squeeze_adjustments = {
            color: max(0.5, (ratio / total_ratio) * 10.0)
            for color, ratio in color_ratios.items()
        }
        
        print(f"\n📊 Example color ratios: {color_ratios}")
        print(f"📊 Normalized squeeze durations (10s total): {squeeze_adjustments}")
        
        # Create modified sequence
        modified_configs = []
        color_sequence = ["red", "yellow", "blue"]
        color_index = 0
        
        for step in original_configs:
            if "squeeze washing bottle" in step.lower():
                current_color = color_sequence[color_index] if color_index < len(color_sequence) else "red"
                dynamic_duration = squeeze_adjustments.get(current_color, 1.5)
                modified_step = f"squeeze washing bottle for {dynamic_duration} seconds"
                modified_configs.append(modified_step)
                color_index += 1
            else:
                modified_configs.append(step)
        
        print(f"\n🔧 Modified sequence (what gets sent to sequential_execute.py):")
        for i, step in enumerate(modified_configs, 1):
            if "squeeze washing bottle" in step.lower():
                print(f"  {i:2d}. {step} ⬅️ Modified!")
            else:
                print(f"  {i:2d}. {step}")
        
        # Create temporary sequence structure
        temp_sequence_data = {
            "predefined_sequences": {
                "temp_timed_laboratory_demo": {
                    "name": "temp_timed_laboratory_demo",
                    "description": "Temporary timed laboratory procedure with dynamic squeeze durations",
                    "configurations": modified_configs,
                    "execution_options": original_sequence.get("execution_options", {})
                }
            },
            "metadata": {
                "version": "1.0_temp",
                "description": "Temporary sequence with dynamic squeeze durations",
                "original_sequence": "timed_laboratory_procedure"
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_sequence_data, f, indent=2)
            temp_file_path = f.name
        
        print(f"\n📁 Temporary sequence file created: {temp_file_path}")
        print(f"\n🎯 The system would execute:")
        print(f"   python3 sequential_execute.py temp_timed_laboratory_demo --sequences-file {temp_file_path} --smooth")
        
        # Show the temporary file content
        print(f"\n📄 Temporary sequence file content (excerpt):")
        print("=" * 60)
        for i, step in enumerate(modified_configs[:10], 1):  # Show first 10 steps
            print(f"  {i:2d}. {step}")
        if len(modified_configs) > 10:
            print(f"   ... and {len(modified_configs) - 10} more steps")
        print("=" * 60)
        
        # Clean up
        os.unlink(temp_file_path)
        print(f"\n🧹 Cleaned up temporary file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_architecture_summary():
    """Show how the new architecture works."""
    
    print("\n" + "="*80)
    print("🏗️  NEW ARCHITECTURE SUMMARY")
    print("="*80)
    
    print("""
🔄 How the modified system works:

1. Frontend sends color ratios to robot_service/main.py
   └── POST /multi_color_dispensing with ColorRatios

2. main.py loads original sequence from sequential_sequences.json
   └── Loads "timed_laboratory_procedure" configurations

3. main.py calculates dynamic squeeze durations
   └── Normalizes to 10 seconds total based on color ratios
   └── red: 3.0s, yellow: 2.0s, blue: 1.0s (example)

4. main.py creates temporary modified sequence
   └── Replaces "squeeze washing bottle for X seconds" with dynamic values
   └── Saves as temp_sequence_{cmd_id}.json

5. main.py calls sequential_execute.py with temporary file
   └── python3 sequential_execute.py temp_timed_laboratory_{cmd_id} \\
       --sequences-file temp_sequence_{cmd_id}.json --smooth

6. sequential_execute.py loads and executes the modified sequence
   └── Uses dynamic squeeze durations instead of hardcoded values

7. Temporary file is cleaned up after execution
   └── temp_sequence_{cmd_id}.json is deleted

✅ Benefits:
   • Uses proven sequential_execute.py infrastructure
   • Dynamic squeeze duration modification based on color ratios
   • No modification of original sequential_sequences.json
   • Clean separation of concerns
   • Proper error handling and cleanup
""")

if __name__ == "__main__":
    print("🎭 Dynamic Squeeze Duration Modification Demo")
    print("="*50)
    
    success = create_example_modified_sequence()
    
    if success:
        show_architecture_summary()
        print("\n🎉 Demo completed successfully!")
        print("\n💡 To test with real robot:")
        print("   1. Start robot_service: REQUIRE_ROBOT=false python3 main.py")
        print("   2. Run test: python3 test_dynamic_squeeze.py")
    else:
        print("\n❌ Demo failed!")
