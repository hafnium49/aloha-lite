# Frontend Color Optimization System Tests

This directory contains comprehensive tests for the 4-pigment hue-based color optimization system in `frontend/main.py`.

## 🧪 Test Overview

The tests validate the complete color optimization system including:
- **4-Pigment System**: Red, yellow, blue pigments with white solvent background (auto-calculated to 3.0 total volume)
- **Hue-Based Optimization**: CIELAB color space with angular distance calculations instead of RGB Euclidean distance
- **Phase-Based Optimization**: Hybrid approach with N≤8 hybrid phase and N≥9 calibration-only for white-locked system
- **API Integration**: FastAPI endpoints for 4-pigment ratio recommendations and hue distance tracking
- **Ground Truth Calibration**: 4x3 matrix support for pigment-to-RGB mapping with white solvent normalization
- **Frontend Integration**: White solvent auto-calculation and 4-pigment ratio display (R:Y:B:W format)

## 📁 Files Overview

### Core Test Files

- **`test_hue_optimization.py`** - Comprehensive tests for CIELAB hue-based optimization with angular distance (NEW)
- **`test_4_pigment_system.py`** - Tests for 4-pigment system with white solvent auto-calculation (UPDATED)
- **`test_4_pigment_api.py`** - API endpoint tests for 4-pigment ratios with hue distance tracking (NEW)
- **`test_optimization.py`** - Tests the phase-based color optimization algorithm for white-locked system (UPDATED)
- **`test_color_space.py`** - Color space conversion and 4x3 matrix operations (UPDATED)
- **`run_updated_tests.py`** - Comprehensive test runner for all hue-based optimization tests (NEW)
- **`mock_robot_service.py`** - Mock robot service that simulates API endpoints for testing
- **`integration_test_server.py`** - Full integration test server that serves frontend and proxies to mock service
- **`simple_test.py`** - Simple test runner for basic frontend validation
- **`test_integration_simulation.py`** - Simulation script that shows API call flow

### Utilities

- **`serve_frontend.py`** - Basic HTTP server for serving frontend files with CORS support
- **`validate_integration.py`** - Validation script to check if integration code is properly implemented
- **`run_tests.py`** - Test runner that executes all tests in the directory (NEW)

### Documentation

- **`INTEGRATION_TEST_RESULTS.md`** - Comprehensive integration test results and status
- **`README.md`** - This file

## 🚀 Quick Start

### Option 1: Run All Tests (Recommended)

```bash
cd /home/hafnium/aloha-lite/frontend/tests
python run_updated_tests.py
```

This will run:
- Hue-based optimization tests (CIELAB color space with angular distance)
- 4-pigment system tests (red, yellow, blue, white with auto-calculation)
- API endpoint validation tests (hue distance tracking)
- Phase-based optimization tests (N≤8 hybrid, N≥9 calibration-only)
- Color space conversion tests (RGB to CIELAB)
- Matrix dimension validation tests (4x3 ground truth matrices)
- Frontend integration tests (white solvent auto-calculation)

### Option 2: Run Specific Test Modules

#### Hue-Based Optimization Tests
```bash
cd /home/hafnium/aloha-lite/frontend/tests
python test_hue_optimization.py
```

Tests the CIELAB hue-based optimization system:
- RGB to CIELAB conversion (`_rgb_to_lab`) with proper color space transformation
- Hue angle calculation (`_hue_deg`) with arctan2-based implementation
- Angular distance measurement (`_ang_diff`) for hue-only optimization
- Hue-only optimization integration replacing RGB Euclidean distance
- Color tolerance validation (±70° for non-red colors, stricter for red)

#### 4-Pigment System Tests
```bash
cd /home/hafnium/aloha-lite/frontend/tests
python test_4_pigment_system.py
```

Tests the 4-pigment system functionality:
- ColorOptimizer initialization with 4 pigments (red, yellow, blue, white)
- White solvent normalization and auto-calculation (remaining volume up to 3.0)
- 4x3 ground truth matrix validation (4 pigments × 3 RGB channels)
- Phase-based optimization with white-locked system
- Frontend white ratio display and auto-calculation validation

#### API Endpoint Tests
```bash
cd /home/hafnium/aloha-lite/frontend/tests
python test_4_pigment_api.py
```

Tests FastAPI endpoints for 4-pigment functionality:
- Target color generation and validation with CIELAB conversion
- 4-pigment ratio recommendations with hue distance tracking
- Measurement feedback loops with angular distance calculations
- Optimization statistics collection (hue distances vs RGB distances)
- API response validation for white solvent inclusion

#### Color Optimization Tests
```bash
cd /home/hafnium/aloha-lite/frontend/tests
python test_optimization.py
```

Tests the phase-based optimization algorithm:
- Phase transitions (N≤8 hybrid phase, N≥9 calibration-only phase)
- Hybrid optimization with white-locked system and hue-based distance
- Calibration-only mode validation for advanced optimization stages
- White solvent handling in both optimization phases

## 🎨 Frontend Integration Features

The updated frontend (`index.html`) now includes:

### White Solvent Auto-Calculation
- **Auto-calculation**: White solvent amount automatically calculated as remaining volume up to 3.0 total
- **Display**: Readonly white ratio input field shows calculated amount
- **Visualization**: Color preview maintains 3-pigment gradient while white is handled separately
- **Button Text**: Mixing button shows all 4 ratios in R:Y:B:W format

### Enhanced Color Preview
- **Gradient Display**: Visual representation of red, yellow, blue proportions
- **White Background**: White solvent provides the base/background for color mixing
- **Dynamic Updates**: Real-time updates as ratios change
- **Validation**: Prevents mixing when all ratios are zero

### 4-Pigment API Integration
- **Endpoint Support**: Compatible with `/api/recommend-ratios` for 4-pigment recommendations
- **Hue Distance Tracking**: Displays hue-based distances instead of RGB Euclidean
- **Statistics Display**: Shows optimization progress with CIELAB-based metrics
- **White Handling**: Properly manages white solvent in API requests and responses

## 🧪 Test Types

### Option 3: Full Integration Test

1. **Activate conda environment**:
   ```bash
   conda activate aloha-lite
   ```

2. **Start the mock robot service**:
   ```bash
   cd /home/hafnium/aloha-lite/frontend/tests
   python3 mock_robot_service.py &
   ```

3. **Start the integration test server**:
   ```bash
   python3 integration_test_server.py
   ```

4. **Open http://localhost:3000 in your browser**

5. **Test 4-pigment functionality**:
   - Adjust red, yellow, blue ratios
   - Observe white solvent auto-calculation
   - Test mixing button with 4-pigment ratios
   - Validate hue-based optimization recommendations

### Option 4: Conda Environment Testing

```bash
# Ensure conda environment is active
conda activate aloha-lite

# Run all tests with proper environment
cd /home/hafnium/aloha-lite/frontend/tests
python run_updated_tests.py
```

### Option 5: Simple Test

```bash
cd /home/hafnium/aloha-lite/frontend/tests
python3 simple_test.py
```

Open http://localhost:3000 to test basic functionality including:
- 4-pigment ratio input and auto-calculation
- White solvent display and validation
- Hue-based color optimization
- CIELAB color space integration

### Option 6: Direct Frontend Serving

```bash
cd /home/hafnium/aloha-lite/frontend/tests
python3 serve_frontend.py
```

This serves the frontend on http://localhost:3000 with CORS support for testing:
- 4-pigment white solvent auto-calculation
- Hue-based optimization interface
- CIELAB color space visualization
- Updated mixing button with R:Y:B:W format

## 🔬 Key Testing Validations

### 1. Hue-Based Optimization Validation
- **CIELAB Conversion**: RGB to CIELAB color space transformation accuracy
- **Hue Angle Calculation**: Proper arctan2-based hue angle computation (0-360°)
- **Angular Distance**: Hue-only distance calculation replacing RGB Euclidean distance
- **Tolerance Testing**: ±70° tolerance for non-red colors, stricter validation for red hues
- **Integration Testing**: End-to-end hue-based optimization workflow

### 2. 4-Pigment System Validation
- **Matrix Dimensions**: 4x3 ground truth matrix (4 pigments × 3 RGB channels)
- **White Solvent**: Auto-calculation to maintain 3.0 total volume
- **Normalization**: Proper handling of white solvent in ratio calculations
- **Phase Transitions**: N≤8 hybrid phase, N≥9 calibration-only for white-locked system
- **API Compatibility**: 4-pigment ratio handling in all endpoints

### 3. Frontend Integration Validation
- **Auto-Calculation**: White solvent automatically calculated as (3.0 - red - yellow - blue)
- **Input Validation**: Prevents negative values and maintains total volume constraints
- **Display Format**: Mixing button shows R:Y:B:W format with proper decimal handling
- **Preview Updates**: Real-time color preview with white solvent consideration
- **API Integration**: Proper 4-pigment data transmission to backend services

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
   - `POST /robot/execute` - Execute laboratory procedure with 4-pigment ratios
   - `GET /robot/{cmd_id}/status` - Status with beaker analysis results and hue distances
   - `GET /robot/{cmd_id}/beaker-analysis` - Dedicated analysis endpoint with CIELAB data

2. **Frontend Integration**:
   - Status polling detects `beaker_analysis_results` with hue information
   - `displayAnalysisResults()` function shows comprehensive visualization including hue data
   - Error handling when analysis unavailable
   - 4-pigment ratio display in analysis results

3. **Data Flow**:
   - Laboratory procedure triggers beaker analysis with 4-pigment input
   - Results include colors, hue angles, CIELAB coordinates, confidence, position
   - Frontend displays all analysis data with hue-based distance calculations
   - White solvent handling in analysis pipeline

## 🎯 Expected Test Results

When testing the 4-pigment hue-based optimization system:

1. **Execute Request**: Send 4-pigment ratios (red, yellow, blue, white) to robot service
2. **Status Response**: Receive task status with beaker analysis results including hue data
3. **Frontend Display**: See comprehensive analysis visualization including:
   - Dominant color with CIELAB coordinates and hue angle
   - 4-pigment ratio breakdown and white solvent calculation
   - Hue-based distance measurements instead of RGB Euclidean
   - Color space visualization with angular distance indicators
   - Optimization statistics with CIELAB-based progress tracking

### Specific Test Outcomes

#### Hue Optimization Tests
- **test_hue_optimization.py**: All 6 tests should pass
  - RGB to CIELAB conversion accuracy
  - Hue angle calculations (proper 0-360° range)
  - Angular distance measurements for optimization
  - Integration with ColorOptimizer class

#### 4-Pigment System Tests  
- **test_4_pigment_system.py**: All 5 tests should pass
  - 4-pigment initialization and matrix validation
  - White solvent normalization and auto-calculation
  - Phase-based optimization with white-locked system
  - Ground truth matrix dimensions (4x3)

#### API Endpoint Tests
- **test_4_pigment_api.py**: All API tests should pass
  - 4-pigment ratio recommendations
  - Hue distance tracking in responses
  - White solvent inclusion in API calls
  - Optimization statistics with CIELAB metrics

## 🐛 Troubleshooting

### Mock Service Won't Start
- Check if port 8001 is already in use: `lsof -i :8001`
- Try a different port in `mock_robot_service.py`
- Ensure conda aloha-lite environment is active

### Frontend Can't Connect
- Ensure mock service is running on expected port
- Check CORS headers in browser developer tools
- Verify integration server proxy configuration
- Confirm conda environment activation

### No Beaker Analysis Results
- Check that test uses "laboratory" in sequence name
- Verify mock service includes `beaker_analysis_results` in response
- Check browser console for JavaScript errors
- Validate 4-pigment ratio data transmission

### Test Failures
- **Hue Calculation Errors**: Check tolerance settings (±70° for non-red colors)
- **Matrix Dimension Errors**: Ensure 4x3 matrix expectations (4 pigments × 3 RGB)
- **White Solvent Errors**: Verify auto-calculation logic (remaining volume up to 3.0)
- **API Errors**: Check 4-pigment ratio format in requests/responses

### Conda Environment Issues
```bash
# Verify environment is active
conda info --envs
conda activate aloha-lite

# Check Python path and packages
which python
pip list | grep -E "(fastapi|numpy|scipy)"
```

## 📝 Adding New Tests

To add new test scenarios:

1. **Mock Service**: Add new response patterns in `mock_robot_service.py` with 4-pigment support
2. **Frontend Tests**: Create new test functions in test files for hue-based scenarios
3. **Validation**: Add new checks to `validate_integration.py` for CIELAB validation
4. **Documentation**: Update this README with new hue-based test descriptions
5. **Test Data**: Include 4-pigment test cases with white solvent scenarios

### New Test Development Guidelines
- **Hue Testing**: Use CIELAB color space for distance calculations
- **4-Pigment Support**: Always include white solvent in test scenarios
- **Tolerance Settings**: Use appropriate tolerances for hue angle calculations
- **Matrix Validation**: Ensure 4x3 dimensions for ground truth matrices
- **Frontend Integration**: Test white solvent auto-calculation and display

## 🔗 Related Files

- `../index.html` - Main frontend file being tested
- `../../robot_service/main.py` - Actual robot service implementation
- `../../robot_service/tests/` - Backend test files
- `../../temp_rules/sequential_sequences.json` - Laboratory procedure configuration
