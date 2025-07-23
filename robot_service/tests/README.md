# Robot Service Tests

This directory contains test files for the `robot_service` module.

## Structure

```
robot_service/tests/
├── __init__.py                      # Python package init
├── README.md                       # This file
├── run_tests.py                    # Test runner script
├── serve_tests.py                  # Test server for HTML tests
├── test_api.py                     # Tests for vision bridge API integration
├── test_beaker_analysis.py         # Tests for beaker analysis functionality
└── test_beaker_integration.html    # Frontend integration test for beaker analysis
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

### test_beaker_integration.html
- **Frontend Integration Test** for beaker analysis GUI display
- Tests the `displayAnalysisResults()` JavaScript function
- Validates data structure compatibility with robot service API
- Tests API endpoint integration (`/robot/{cmd_id}/beaker-analysis`)
- Interactive browser-based testing with sample and real data

#### Running the Frontend Integration Test
```bash
# Method 1: Use the included test server (recommended)
cd robot_service
python3 tests/serve_tests.py [port]
# Then visit: http://localhost:8080/tests/test_beaker_integration.html

# Method 2: Use Python's built-in server
cd robot_service
python3 -m http.server 8080
# Then visit: http://localhost:8080/tests/test_beaker_integration.html

# Method 3: Open directly in browser (limited functionality)
file:///path/to/robot_service/tests/test_beaker_integration.html
```

**Test Features:**
- 🎨 **Sample Data Test**: Test with synthetic beaker analysis data
- 🔬 **Real Data Test**: Test with actual robot service data structure
- 🌐 **API Integration Test**: Test API endpoints (requires robot service running)
- Interactive log display and result visualization
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
