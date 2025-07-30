# Ground Truth Calibrator Test Suite

This directory contains comprehensive tests for the `ground_truth_calibrator.py` utility. The tests are designed to validate all functionality without requiring actual robot hardware or user interaction.

## Test Files

### `test_ground_truth_calibrator.py`
Main test suite containing:
- **TestGroundTruthCalibrator**: Core functionality tests
- **TestGroundTruthCalibratorIntegration**: Integration tests with realistic scenarios  
- **MockScenarioTests**: Tests simulating typical user workflows

### `run_tests.py`
Test runner script that executes all tests and provides summary results.

### `mock_data.py`
Mock data generator providing:
- Realistic color values for testing
- Mock subprocess outputs
- Test scenario configurations
- Sample data file generation

## Running Tests

### Run All Tests
```bash
# From the utilities directory
python tests/run_tests.py

# Or directly run the test file
python tests/test_ground_truth_calibrator.py
```

### Run Specific Test Classes
```bash
python tests/run_tests.py --class TestGroundTruthCalibrator
python tests/run_tests.py --class TestGroundTruthCalibratorIntegration
python tests/run_tests.py --class MockScenarioTests
```

### List Available Tests
```bash
python tests/run_tests.py --list-tests
```

## Test Coverage

### Core Functionality Tests
- ✅ **Initialization**: Calibrator setup and directory creation
- ✅ **Color Parsing**: RGB, hex, and CSV format parsing
- ✅ **Sequence Execution**: Mocked subprocess calls for robot sequences
- ✅ **Data Storage**: Ground truth file creation and JSON structure
- ✅ **Error Handling**: Invalid inputs, file system errors, subprocess failures

### Integration Tests  
- ✅ **Complete Workflows**: End-to-end calibration processes
- ✅ **Mixed Scenarios**: Success/failure combinations
- ✅ **File System Operations**: Directory creation, file permissions
- ✅ **Color Format Accuracy**: Conversion between RGB/hex formats

### User Experience Tests
- ✅ **User Input Simulation**: Realistic user interaction patterns
- ✅ **Error Recovery**: Invalid input handling and retry logic
- ✅ **Batch Processing**: Multi-solution calibration workflows

## Mock Strategies

### Subprocess Mocking
Robot sequence execution is mocked using `unittest.mock.patch`:
```python
@patch('subprocess.run')
def test_sequence_execution(self, mock_subprocess):
    mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success")
    # Test continues without actual robot movement
```

### User Input Mocking
User interactions are simulated with pre-defined input sequences:
```python
@patch('builtins.input')
def test_color_input(self, mock_input):
    mock_input.side_effect = ["RGB(255, 0, 0)", "y"]
    # Test processes simulated user inputs
```

### File System Mocking
Temporary directories are used for safe file operations:
```python
def setUp(self):
    self.test_dir = tempfile.mkdtemp()
    self.calibrator = GroundTruthCalibrator(self.test_dir)
```

## Test Scenarios

### Happy Path Scenario
- All sequences execute successfully
- User provides valid color inputs
- All ground truth files are created correctly
- Summary file is generated with complete data

### Error Recovery Scenario  
- User initially provides invalid color formats
- User corrects inputs after validation errors
- System successfully recovers and completes calibration

### Mixed Results Scenario
- Some robot sequences succeed, others fail
- Partial calibration data is saved
- System provides accurate success/failure reporting

### File System Error Scenario
- Tests handling of permission errors
- Validates graceful error reporting
- Ensures no data corruption during failures

## Expected Test Results

When all tests pass, you should see output like:
```
======================================================================
GROUND TRUTH CALIBRATOR TEST SUITE
======================================================================

test_calibrate_all_solutions ... ok
test_calibrate_and_save_blue_solution ... ok
test_calibrate_and_save_red_solution ... ok
test_color_format_conversion_accuracy ... ok
test_get_color_measurement_hex_format ... ok
test_initialization ... ok
test_parse_color_metric_invalid_formats ... ok
test_parse_color_metric_rgb_format ... ok
test_run_calibration_sequence_success ... ok
test_typical_user_workflow ... ok
test_update_calibration_summary ... ok

----------------------------------------------------------------------
Ran 25 tests in 0.123s

OK

======================================================================
✅ ALL TESTS PASSED!
The ground truth calibrator is working correctly.
======================================================================
```

## Adding New Tests

To add new tests:

1. **Add test methods** to existing test classes in `test_ground_truth_calibrator.py`
2. **Create new test classes** for different aspects of functionality
3. **Add mock scenarios** to `mock_data.py` for complex test cases
4. **Update test runner** if needed for new test organization

### Example New Test
```python
def test_new_functionality(self):
    """Test description"""
    # Setup
    test_data = self.create_test_data()
    
    # Execute
    result = self.calibrator.new_method(test_data)
    
    # Verify
    self.assertTrue(result)
    self.assertEqual(expected_value, actual_value)
```

## Debugging Tests

### Verbose Output
```bash
python tests/test_ground_truth_calibrator.py -v
```

### Single Test Method
```bash
python -m unittest test_ground_truth_calibrator.TestGroundTruthCalibrator.test_initialization
```

### Debug with Print Statements
Add debug output in tests:
```python
def test_debug_example(self):
    result = self.calibrator.some_method()
    print(f"Debug: result = {result}")  # Visible in test output
    self.assertTrue(result)
```

The test suite ensures the ground truth calibrator works correctly in all scenarios without requiring robot hardware, making development and validation efficient and safe.
