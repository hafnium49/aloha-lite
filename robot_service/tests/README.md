# Robot Service Tests

This directory contains test files for the `robot_service` module.

## Structure

```
robot_service/tests/
├── __init__.py              # Python package init
├── README.md               # This file
├── run_tests.py            # Test runner script
├── test_api.py             # Tests for vision bridge API integration
└── test_beaker_analysis.py # Tests for beaker analysis functionality
```

## Running Tests

### Run All Tests
```bash
# From robot_service directory
python3 tests/run_tests.py

# Or from tests directory
cd tests && python3 run_tests.py
```

### Run Individual Tests
```bash
# From robot_service directory
python3 tests/test_api.py
python3 tests/test_beaker_analysis.py

# Or from tests directory
cd tests
python3 test_api.py
python3 test_beaker_analysis.py
```

## Test Descriptions

### test_api.py
- Tests the vision bridge API connection
- Validates beaker analysis endpoint functionality
- Requires vision bridge server running on `localhost:8000`
- Uses sample images from `../../temporary_images/`

### test_beaker_analysis.py
- Tests the beaker analysis special function recognition
- Tests the `SequentialRobotExecutor` beaker analysis execution
- Tests pattern matching for beaker analysis commands
- Mock test (uses dummy server URL for safety)

## Dependencies

Tests require:
- `requests` library for API calls
- Access to the parent `robot_service` module
- Vision bridge server (for `test_api.py`)
- Sample test images (for image-based tests)

## Path Resolution

All tests use absolute path resolution based on `__file__` location to ensure they work correctly regardless of execution directory:

```python
# Example pattern used in tests
image_path = Path(os.path.dirname(__file__)) / "../../temporary_images/test_image.jpg"
```

This ensures tests work when run from:
- `robot_service/tests/` directory  
- `robot_service/` directory
- Any parent directory
