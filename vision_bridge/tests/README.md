# Vision Bridge Tests

This directory contains test scripts for the vision bridge service functionality.

## Test Files

### 1. `test_color_checker.py`
- **Purpose**: Unit test using FastAPI TestClient 
- **Usage**: Run with `python -m pytest test_color_checker.py`
- **Description**: Tests the circle-colour endpoint with a sample image using the FastAPI test client
- **Updated**: Now tests the new `/circle-colour` endpoint instead of `/color-checker`

### 2. `test_color_checker_api.py` 
- **Purpose**: Circle colour API integration test using HTTP requests
- **Usage**: Run with `python test_color_checker_api.py`
- **Description**: Tests the circle-colour endpoint via HTTP requests to the running service
- **Requirements**: Service must be running (via Docker Compose)
- **Updated**: Now tests the new `/circle-colour` endpoint for circle detection and color analysis

### 3. `test_direct_color_checker.py`
- **Purpose**: Direct circle detection testing within container
- **Usage**: Run inside Docker container
- **Description**: Tests the circle detection directly using OpenCV HoughCircles algorithm
- **Requirements**: Must be run inside the vision-bridge container with proper dependencies
- **Updated**: Now uses OpenCV circle detection instead of colour-checker-detection library

### 4. `test_multi_color.py`
- **Purpose**: Multi-color dispensing API test
- **Usage**: Run with `python test_multi_color.py`
- **Description**: Tests the multi-color dispensing robot API endpoints
- **Requirements**: Robot service must be running

### 5. `test_consolidated_service.py`
- **Purpose**: Unit test for consolidated robot service logic
- **Usage**: Run with `python test_consolidated_service.py`
- **Description**: Tests the multi-color dispensing logic without requiring Docker
- **Requirements**: FastAPI dependencies (available in container or virtual environment)

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

### All Tests
To run all pytest-compatible tests:
```bash
cd vision_bridge/tests
python -m pytest -v
```

## Test Data
- Sample images are located in `../samples/`
- Test images are located in `../../temporary_images/`

## Notes
- The import errors in `test_direct_color_checker.py` for cv2 are expected since these dependencies are only available inside the Docker container
- The new `/circle-colour` endpoint detects circles in the left half of images and returns color information
- API tests require the services to be running and accessible
- Path adjustments have been made to account for the new test location within the vision_bridge directory structure
- Tests now focus on circle detection and color analysis rather than color checker patterns
