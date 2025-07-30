# Ground Truth Calibration Utility

This utility h## Output Files

The utility creates the following files in `frontend/ground_truth_calibration/` directory:

- `red_solution_ground_truth.json` - Red solution calibration data
- `yellow_solution_ground_truth.json` - Yellow solution calibration data  
- `blue_solution_ground_truth.json` - Blue solution calibration data
- `calibration_summary.json` - Summary of all calibrationspare ground-truth calibration instances for the ColorOptimizer by automating the process of:
1. Running calibration sequences for red, yellow, and blue solutions
2. Converting measured color metrics to ColorOptimizer format  
3. Calibrating solutions and saving ground truth data

## Usage

### Calibrate Individual Solutions

```bash
# Calibrate red solution
python utilities/ground_truth_calibrator.py --solution red

# Calibrate yellow solution  
python utilities/ground_truth_calibrator.py --solution yellow

# Calibrate blue solution
python utilities/ground_truth_calibrator.py --solution blue
```

### Calibrate All Solutions

```bash
# Calibrate all solutions automatically
python utilities/ground_truth_calibrator.py --all

# Calibrate all solutions with manual sequence execution
python utilities/ground_truth_calibrator.py --all --no-auto-run
```

## Process Overview

For each solution, the utility follows this 3-step process:

### Step 1: Run Calibration Sequence
- **Red**: `python sequential_execute.py calibration_red_solution --smooth`
- **Yellow**: `python sequential_execute.py calibration_yellow_solution --smooth`  
- **Blue**: `python sequential_execute.py calibration_blue_solution --smooth`

### Step 2: Convert Color Measurement
The utility accepts color measurements in multiple formats:
- `RGB(201, 236, 38)` 
- `#c9ec26`
- `201, 236, 38`

### Step 3: Save Ground Truth Data
Calibration data is saved in JSON format to `frontend/ground_truth_calibration/` directory.

## Output Files

The utility creates the following files in `frontend/ground_truth_calibration/`:

- `red_solution_ground_truth.json` - Red solution calibration data
- `yellow_solution_ground_truth.json` - Yellow solution calibration data  
- `blue_solution_ground_truth.json` - Blue solution calibration data
- `calibration_summary.json` - Summary of all calibrations

## Ground Truth Data Structure

Each solution's ground truth file contains:

```json
{
  "solution": "red",
  "color_measurement": {
    "rgb": [201, 236, 38],
    "hex": "#c9ec26",
    "format": "RGB(201, 236, 38)"
  },
  "calibration_sequence": "calibration_red_solution",
  "timestamp": "2025-07-30T12:34:56.789",
  "description": "Red solution calibration",
  "notes": {
    "squeeze_time": "10 seconds",
    "stir_time": "10 seconds", 
    "analysis_wait": "3 seconds"
  }
}
```

## Calibration Sequences

The utility uses these predefined sequences from `temp_rules/sequential_sequences.json`:

### Red Solution (`calibration_red_solution`)
1. Position arms and beaker
2. Dispense red solution
3. Squeeze washing bottle for 10 seconds
4. Return to standoff positions
5. Stir solution for 10 seconds
6. Analyze beaker color
7. Return to serving position

### Yellow Solution (`calibration_yellow_solution`)  
1. Position arms and beaker
2. Dispense yellow solution
3. Squeeze washing bottle for 10 seconds
4. Return to standoff positions
5. Stir solution for 10 seconds
6. Analyze beaker color
7. Return to serving position

### Blue Solution (`calibration_blue_solution`)
1. Position arms and beaker
2. Dispense red solution (1.5 second squeeze)
3. Position for blue dispensing
4. Dispense blue solution
5. Squeeze washing bottle for 10 seconds
6. Return to standoff positions
7. Stir solution for 10 seconds
8. Analyze beaker color
9. Return to serving position

## Options

- `--solution {red,yellow,blue}` - Calibrate a specific solution
- `--all` - Calibrate all solutions
- `--no-auto-run` - Don't automatically run sequences (manual execution)
- `--base-dir PATH` - Specify project base directory

## Examples

```bash
# Quick calibration of all solutions
python utilities/ground_truth_calibrator.py --all

# Manual control over sequence execution
python utilities/ground_truth_calibrator.py --all --no-auto-run

# Calibrate just the red solution
python utilities/ground_truth_calibrator.py --solution red

# Use custom base directory
python utilities/ground_truth_calibrator.py --all --base-dir /path/to/project
```

## Integration with ColorOptimizer

The generated ground truth data can be used to initialize the ColorOptimizer's BottleModel with known calibration values, providing a baseline for the dual-state calibration architecture. The files are saved directly in the `frontend/ground_truth_calibration/` directory for immediate access by the frontend ColorOptimizer system.

## Error Handling

The utility includes comprehensive error handling for:
- Invalid color format inputs
- Failed sequence executions
- File I/O errors
- Missing directories or dependencies

Progress is reported at each step, and calibration can be resumed if interrupted.
