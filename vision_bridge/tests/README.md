# Vision Bridge Tests

This directory contains test scripts for the vision bridge service functionality, including comprehensive SAM 2 integration tests.

## Test Files Organization

### Core Vision Bridge Tests

#### 1. `test_color_checker.py`
- **Purpose**: Unit test using FastAPI TestClient 
- **Usage**: Run with `python -m pytest test_color_checker.py`
- **Description**: Tests the circle-colour endpoint with a sample image using the FastAPI test client
- **Updated**: Now tests the new `/circle-colour` endpoint instead of `/color-checker`

#### 2. `test_color_checker_api.py` 
- **Purpose**: Circle colour API integration test using HTTP requests
- **Usage**: Run with `python test_color_checker_api.py`
- **Description**: Tests the circle-colour endpoint via HTTP requests to the running service
- **Requirements**: Service must be running (via Docker Compose)
- **Updated**: Now tests the new `/circle-colour` endpoint for circle detection and color analysis

#### 3. `test_direct_color_checker.py`
- **Purpose**: Direct circle detection testing within container
- **Usage**: Run inside Docker container
- **Description**: Tests the circle detection directly using OpenCV HoughCircles algorithm
- **Requirements**: Must be run inside the vision-bridge container with proper dependencies
- **Updated**: Now uses OpenCV circle detection instead of colour-checker-detection library

#### 4. `test_multi_color.py`
- **Purpose**: Multi-color dispensing API test
- **Usage**: Run with `python test_multi_color.py`
- **Description**: Tests the multi-color dispensing robot API endpoints
- **Requirements**: Robot service must be running

#### 5. `test_consolidated_service.py`
- **Purpose**: Unit test for consolidated robot service logic
- **Usage**: Run with `python test_consolidated_service.py`
- **Description**: Tests the multi-color dispensing logic without requiring Docker
- **Requirements**: FastAPI dependencies (available in container or virtual environment)

#### 6. `test_beaker_analysis.py`
- **Purpose**: Beaker detection and color analysis testing
- **Usage**: Run with `python test_beaker_analysis.py`
- **Description**: Tests beaker detection algorithms and color clustering
- **Output**: Saves visualization to `test_results/beaker_analysis_visualization.jpg`

### SAM 2 Integration Tests

The following SAM 2 test files have been moved from `vision_bridge/` to this directory with proper import path resolution:

#### 7. `test_sam2_integration.py` - Comprehensive SAM 2 Integration Test Suite
- **Purpose**: Complete SAM 2 functionality testing using unittest framework
- **Usage**: Run with `python test_sam2_integration.py` or `python -m unittest test_sam2_integration.py`
- **Features**:
  - Tests imports, functionality, visualization, environment variables
  - Graceful fallback testing when SAM 2 is not available
  - Detailed test reporting and output validation
  - Saves test results to `test_results/sam2_test_visualization.jpg`

#### 8. `test_sam2_final.py` - Final SAM 2 Integration Verification
- **Purpose**: Final verification of SAM 2 integration
- **Usage**: Run with `python test_sam2_final.py`
- **Features**:
  - Tests SAM 2 imports and vision bridge integration
  - Verifies graceful fallback when SAM 2 is not configured
  - Provides detailed status reporting

#### 9. `test_sam2_update.py` - SAM 2 Package Update Verification
- **Purpose**: Verification of updated SAM 2 API integration
- **Usage**: Run with `python test_sam2_update.py`
- **Features**:
  - Tests sam2>=1.1.0 package compatibility
  - Verifies visualization and analysis functionality
  - Tests new SAM 2 API calls (build_sam2, SAM2ImagePredictor)

#### 10. `test_sam_integration.py` - Basic SAM Integration Compatibility
- **Purpose**: Quick SAM integration verification
- **Usage**: Run with `python test_sam_integration.py`
- **Features**:
  - Basic functionality and fallback behavior testing
  - Lightweight compatibility check

## Import Path Resolution

All moved SAM 2 test files use robust import path resolution to work from the tests directory:

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

The test runner (`run_tests.py`) includes all test categories:

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

### SAM 2 Test Execution Order

The SAM 2 tests are executed in this sequence:
1. **Comprehensive test** - `test_sam2_integration.py` (unittest suite)
2. **Final integration** - `test_sam2_final.py`
3. **Update verification** - `test_sam2_update.py`
4. **Basic compatibility** - `test_sam_integration.py`

## Test Results and Output

Test results and visualizations are organized in the `test_results/` subdirectory:
- `test_results/sam2_test_visualization.jpg` - SAM 2 test visualization output
- `test_results/beaker_analysis_result.jpg` - Beaker analysis visualization
- `test_results/beaker_analysis_visualization.jpg` - Additional beaker test output
- `test_results/beaker_analysis_results.json` - Detailed analysis data

## Environment Requirements

### SAM 2 Configuration

The SAM 2 tests work in both scenarios:
- **With SAM 2**: When `SAM_CHECKPOINT` and `SAM_CONFIG` environment variables are set
- **Without SAM 2**: Graceful fallback to circle detection with appropriate warnings

### Docker Services

For API and integration tests, ensure Docker services are running:
```bash
docker-compose up -d
```

## Running Tests

### Prerequisites
Make sure the Docker services are running:
```bash
docker-compose up -d
```

### Individual Test Execution

1. **Unit tests (pytest)**:
   ```bash
   cd vision_bridge/tests
   python -m pytest test_color_checker.py -v
   ```

2. **Circle colour API integration tests**:
   ```bash
   cd vision_bridge/tests
   python test_color_checker_api.py
   ```

3. **Direct circle detection testing** (inside container):
   ```bash
   docker cp test_direct_color_checker.py aloha-lite-vision-bridge-1:/tmp/
   docker exec -it aloha-lite-vision-bridge-1 python /tmp/test_direct_color_checker.py
   ```

4. **Multi-color dispensing test**:
   ```bash
   cd vision_bridge/tests
   python test_multi_color.py
   ```

5. **Consolidated service logic test**:
   ```bash
   cd vision_bridge/tests
   python test_consolidated_service.py
   ```

6. **Beaker analysis test**:
   ```bash
   cd vision_bridge/tests
   python test_beaker_analysis.py
   ```

7. **SAM 2 integration tests**:
   ```bash
   cd vision_bridge/tests
   # Comprehensive unittest suite
   python test_sam2_integration.py
   
   # Individual SAM 2 tests
   python test_sam2_final.py
   python test_sam2_update.py
   python test_sam_integration.py
   ```

### All Tests
To run all pytest-compatible tests:
```bash
cd vision_bridge/tests
python -m pytest -v
```

To run all tests including SAM 2 via the test runner:
```bash
cd vision_bridge/tests
python run_tests.py --type all
```

## Test Coverage

### Core Vision Bridge Tests Cover:
- ✅ Circle detection and color analysis endpoints
- ✅ FastAPI integration and HTTP API functionality
- ✅ Multi-color dispensing robot logic
- ✅ Direct OpenCV circle detection algorithms
- ✅ Beaker detection and color clustering

### SAM 2 Integration Tests Cover:
- ✅ Import functionality from tests directory
- ✅ SAM 2 package availability detection
- ✅ Vision analysis with and without SAM 2
- ✅ Visualization generation
- ✅ Environment variable configuration
- ✅ Graceful fallback behavior
- ✅ Error handling and reporting

## Test Data
- Sample images are located in `../samples/`
- Test images are located in `../../temporary_images/`
- Test results and visualizations are saved to `test_results/`

## Notes
- The import errors in `test_direct_color_checker.py` for cv2 are expected since these dependencies are only available inside the Docker container
- The new `/circle-colour` endpoint detects circles in the left half of images and returns color information
- API tests require the services to be running and accessible
- Path adjustments have been made to account for the new test location within the vision_bridge directory structure
- Tests now focus on circle detection and color analysis rather than color checker patterns
- All SAM 2 tests maintain backward compatibility and provide clear status reporting for debugging and verification purposes
- Test visualizations are organized in the `test_results/` subdirectory for better file management
