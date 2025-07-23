# Frontend Tests

This directory contains test files and utilities for testing the frontend integration with the robot service.

## 📁 Files Overview

### Core Test Files

- **`mock_robot_service.py`** - Mock robot service that simulates API endpoints for testing
- **`integration_test_server.py`** - Full integration test server that serves frontend and proxies to mock service
- **`simple_test.py`** - Simple test runner for basic frontend validation
- **`test_integration_simulation.py`** - Simulation script that shows API call flow

### Utilities

- **`serve_frontend.py`** - Basic HTTP server for serving frontend files with CORS support
- **`validate_integration.py`** - Validation script to check if integration code is properly implemented

### Documentation

- **`INTEGRATION_TEST_RESULTS.md`** - Comprehensive integration test results and status
- **`README.md`** - This file

## 🚀 Quick Start

### Option 1: Full Integration Test (Recommended)

1. Start the mock robot service:
   ```bash
   cd /home/hafnium/aloha-lite/frontend/tests
   python3 mock_robot_service.py &
   ```

2. Start the integration test server:
   ```bash
   python3 integration_test_server.py
   ```

3. Open http://localhost:3000 in your browser

4. Test beaker analysis by clicking any color button

### Option 2: Simple Test

```bash
cd /home/hafnium/aloha-lite/frontend/tests
python3 simple_test.py
```

Open http://localhost:3000 to test basic functionality.

### Option 3: Direct Frontend Serving

```bash
cd /home/hafnium/aloha-lite/frontend/tests
python3 serve_frontend.py
```

This serves the frontend on http://localhost:3000 with CORS support.

## 🧪 Test Types

### 1. Mock Service Testing (`mock_robot_service.py`)

- **Purpose**: Simulate robot service API without dependencies
- **Port**: 8001 (default)
- **Features**: 
  - Health check endpoint
  - Execute endpoint with beaker analysis simulation
  - Status polling with beaker analysis results
  - Dedicated beaker analysis endpoint

### 2. Integration Testing (`integration_test_server.py`)

- **Purpose**: Test full frontend-to-backend integration
- **Port**: 3000 (default)
- **Features**:
  - Serves frontend files
  - Proxies robot service requests to mock service
  - Handles CORS for browser testing
  - Error fallback when mock service unavailable

### 3. Simple Testing (`simple_test.py`)

- **Purpose**: Basic frontend functionality testing
- **Port**: 3000 (default)
- **Features**:
  - Self-contained test environment
  - Built-in mock responses
  - No external dependencies

### 4. Simulation (`test_integration_simulation.py`)

- **Purpose**: Demonstrate API call flow without actual servers
- **Features**:
  - Shows expected request/response format
  - Demonstrates frontend processing logic
  - Educational tool for understanding integration

## 🔧 Configuration

### Mock Robot Service Configuration

The mock service runs on port 8001 by default. To change:

```python
# In mock_robot_service.py
def run_mock_server(port=8001):  # Change this
```

### Frontend Server Ports

Most servers default to port 3000. To change:

```bash
python3 serve_frontend.py 3001  # Custom port
```

### Integration Test Server

The integration server expects the mock service on port 8001. Update `ROBOT_SERVICE_URL` if needed:

```python
# In integration_test_server.py
ROBOT_SERVICE_URL = "http://localhost:8001"  # Change if needed
```

## 📊 Testing Beaker Analysis Integration

The tests specifically validate:

1. **API Endpoints**:
   - `POST /robot/execute` - Execute laboratory procedure
   - `GET /robot/{cmd_id}/status` - Status with beaker analysis results
   - `GET /robot/{cmd_id}/beaker-analysis` - Dedicated analysis endpoint

2. **Frontend Integration**:
   - Status polling detects `beaker_analysis_results`
   - `displayAnalysisResults()` function shows comprehensive visualization
   - Error handling when analysis unavailable

3. **Data Flow**:
   - Laboratory procedure triggers beaker analysis
   - Results include colors, percentages, confidence, position, volume, temperature, pH
   - Frontend displays all analysis data with proper formatting

## 🎯 Expected Test Results

When testing beaker analysis:

1. **Execute Request**: Send laboratory procedure to robot service
2. **Status Response**: Receive task status with beaker analysis results
3. **Frontend Display**: See comprehensive analysis visualization including:
   - Dominant color and confidence score
   - Color breakdown percentages
   - Beaker position coordinates
   - Volume and temperature estimates
   - pH and mixing quality assessment

## 🐛 Troubleshooting

### Mock Service Won't Start
- Check if port 8001 is already in use: `lsof -i :8001`
- Try a different port in `mock_robot_service.py`

### Frontend Can't Connect
- Ensure mock service is running on expected port
- Check CORS headers in browser developer tools
- Verify integration server proxy configuration

### No Beaker Analysis Results
- Check that test uses "laboratory" in sequence name
- Verify mock service includes `beaker_analysis_results` in response
- Check browser console for JavaScript errors

## 📝 Adding New Tests

To add new test scenarios:

1. **Mock Service**: Add new response patterns in `mock_robot_service.py`
2. **Frontend Tests**: Create new test functions in test files
3. **Validation**: Add new checks to `validate_integration.py`
4. **Documentation**: Update this README with new test descriptions

## 🔗 Related Files

- `../index.html` - Main frontend file being tested
- `../../robot_service/main.py` - Actual robot service implementation
- `../../robot_service/tests/` - Backend test files
- `../../temp_rules/sequential_sequences.json` - Laboratory procedure configuration
