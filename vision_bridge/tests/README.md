# Vision Bridge Tests

This directory contains test scripts for the vision bridge service functionality.

## Test Files

### 1. `test_color_checker.py`
- **Purpose**: Unit test using FastAPI TestClient 
- **Usage**: Run with `python -m pytest test_color_checker.py`
- **Description**: Tests the color checker endpoint with a sample image using the FastAPI test client

### 2. `test_color_checker_api.py` 
- **Purpose**: API integration test using HTTP requests
- **Usage**: Run with `python test_color_checker_api.py`
- **Description**: Tests the color checker endpoint via HTTP requests to the running service
- **Requirements**: Service must be running (via Docker Compose)

### 3. `test_direct_color_checker.py`
- **Purpose**: Direct library testing within container
- **Usage**: Run inside Docker container
- **Description**: Tests the color checker detection directly using the colour-checker-detection library
- **Requirements**: Must be run inside the vision-bridge container with proper dependencies

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

2. **API integration tests**:
   ```bash
   cd vision_bridge/tests
   python test_color_checker_api.py
   ```

3. **Direct library testing** (inside container):
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
- The import errors in `test_direct_color_checker.py` for cv2 and colour_checker_detection are expected since these dependencies are only available inside the Docker container
- API tests require the services to be running and accessible
- Path adjustments have been made to account for the new test location within the vision_bridge directory structure
