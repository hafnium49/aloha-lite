# Test Files Organization

This document describes the organization of test files in the vision_bridge/tests directory.

## Moved Test Files

The following test files have been moved from `vision_bridge/` to `vision_bridge/tests/` directory:

### SAM 2 Integration Tests

1. **`test_sam2_integration.py`** - Comprehensive SAM 2 integration test suite
   - Uses unittest framework for structured testing
   - Tests imports, functionality, visualization, environment variables, and graceful fallback
   - Includes detailed test reporting and output validation
   - Saves test results to `test_results/` subdirectory

2. **`test_sam2_final.py`** - Final SAM 2 integration verification
   - Tests SAM 2 imports and vision bridge integration
   - Verifies graceful fallback when SAM 2 is not configured
   - Provides detailed status reporting

3. **`test_sam2_update.py`** - SAM 2 package update verification
   - Tests the updated SAM 2 API integration
   - Verifies that sam2>=1.1.0 package works correctly
   - Tests visualization and analysis functionality

4. **`test_sam_integration.py`** - Basic SAM integration compatibility test
   - Quick verification of SAM integration
   - Tests basic functionality and fallback behavior

## Import Path Resolution

All moved test files have been updated with robust import path resolution:

```python
# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)
```

This approach:
- Works when files are executed directly or via unittest
- Handles cases where `__file__` is not available (e.g., python -c)
- Allows imports from the parent `vision_bridge/` directory

## Test Runner Integration

The test runner (`run_tests.py`) has been updated to include SAM 2 tests:

### Usage Examples

```bash
# Run all tests including SAM 2
python run_tests.py --type all

# Run only SAM 2 tests
python run_tests.py --type sam2

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type api
python run_tests.py --type container
```

### SAM 2 Test Execution

The SAM 2 tests are executed in this order:
1. **Comprehensive test** - `test_sam2_integration.py` (unittest suite)
2. **Final integration** - `test_sam2_final.py`
3. **Update verification** - `test_sam2_update.py`
4. **Basic compatibility** - `test_sam_integration.py`

## Test Results

Test results and visualizations are saved to:
- `test_results/sam2_test_visualization.jpg` - Test visualization output
- `beaker_analysis_result.jpg` - Legacy test result (maintained for compatibility)

## Environment Requirements

The tests work in both scenarios:
- **With SAM 2**: When `SAM_CHECKPOINT` and `SAM_CONFIG` environment variables are set
- **Without SAM 2**: Graceful fallback to circle detection with appropriate warnings

## Test Coverage

The SAM 2 tests cover:
- ✅ Import functionality from tests directory
- ✅ SAM 2 package availability detection
- ✅ Vision analysis with and without SAM 2
- ✅ Visualization generation
- ✅ Environment variable configuration
- ✅ Graceful fallback behavior
- ✅ Error handling and reporting

All tests maintain backward compatibility and provide clear status reporting for debugging and verification purposes.
