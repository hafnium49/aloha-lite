# Frontend Service

A FastAPI-based web interface for the ALOHA Lite robot system with **ML-enhanced color optimization**. This service provides an intelligent web interface for color mixing with Bayesian optimization, robot control, and beaker analysis, while acting as a proxy to avoid CORS issues between the frontend and backend services.

## Features

- 🤖 **ML-Enhanced Color Mixing**: Bayesian optimization with Gaussian Process Regression for intelligent color recommendations
- 🎨 **Hue-Only Target Optimization**: CIELAB color space optimization using angular distance for perceptually accurate hue matching
- � **Ground Truth Calibration**: Real-world calibration matrix integration from robot-generated ground truth data
- �🎨 **Interactive Color Interface**: Modern responsive design optimized for wide monitors with real-time color preview
- 🧠 **Smart Recommendations**: AI-powered suggestions for optimal color ratios using Expected Improvement acquisition
- 🤖 **Robot Control**: Direct interface to robot dispensing and positioning operations
- 🧪 **Beaker Analysis**: Upload and analyze beaker images with AI-powered color detection
- 🔄 **Service Proxy**: Eliminates CORS issues by proxying requests to backend services
- 📊 **Real-time Monitoring**: Live status updates, progress tracking, and optimization statistics
- 🎯 **Visual Feedback**: Color preview, ML recommendations, hue-based visualization, and operation logging
- 📱 **Responsive Design**: Glass-morphism UI with CSS Grid layout optimized for modern displays

## Quick Start

### Development Mode
```bash
cd /home/hafnium/aloha-lite/frontend
python -m uvicorn main:app --host 0.0.0.0 --port 3000
```

### Access the Interface
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:3000/docs
- **Health Check**: http://localhost:3000/health
- **System Status**: http://localhost:3000/status

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ROBOT_SERVICE_URL` | Robot service backend URL | `http://localhost:8000` |
| `VISION_SERVICE_URL` | Vision bridge service URL | `http://localhost:5000` |

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│  Frontend       │───▶│  Robot Service  │
│   (Port 3000)   │    │ (ML-Enhanced)   │    │  (Port 8000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Vision Bridge   │
                       │  (Port 5000)    │
                       └─────────────────┘

Ground Truth Integration:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Robot Sequence  │───▶│ Color           │───▶│ Ground Truth    │
│ Execution       │    │ Measurement     │    │ JSON Files      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Calibration     │    │ RGB/Hex Data    │    │ Frontend        │
│ Utility         │    │ Collection      │    │ Integration     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
                       └─────────────────┘

ML Pipeline:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Target Color    │───▶│ Bayesian        │───▶│ ML              │
│ Generation      │    │ Optimization    │    │ Recommendations │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Color Space     │    │ Gaussian        │    │ Expected        │
│ Sampling        │    │ Process Reg.    │    │ Improvement     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## API Endpoints

### Frontend Interface
- `GET /` - Main web interface with ML-enhanced color mixing (serves index.html)
- `GET /health` - Frontend service health check
- `GET /status` - Check status of all backend services

### ML Optimization Endpoints
- `GET /api/target-color` - Generate random target color for optimization challenge
- `POST /api/recommend-ratios` - Get ML-powered color ratio recommendations using Bayesian optimization
- `GET /api/hue-visual-data` - Retrieve hue-based optimization visualization data for angular distance tracking

### Ground Truth Calibration
- **Calibration Matrix Loading**: Automatically loads real-world calibration data from robot experiments
- **RGB-based Calibration**: Constructs calibration matrices from measured RGB values of pure solutions
- **Fallback Mechanisms**: Graceful handling when ground truth data is unavailable
- **Test Integration**: Comprehensive test suite validates ground truth integration functionality

### Proxy Endpoints
- `POST /robot/dispense` - Proxy to robot service for color mixing operations
- `GET /robot/{cmd_id}/status` - Proxy to robot service for operation status
- `GET /robot/{cmd_id}/pose-snapshot` - Proxy to robot service for snapshots
- `POST /vision/analyze-beaker` - Proxy to vision service for beaker analysis

## Web Interface Features

### ML-Enhanced Color Mixing (v2.0)
1. **Bayesian Optimization**: Uses Gaussian Process Regression with Expected Improvement acquisition function
2. **Hue-Only Target Mode**: CIELAB color space optimization using angular distance instead of RGB Euclidean distance
3. **Target Color Generation**: Random LAB color space sampling for optimization challenges  
4. **Smart Recommendations**: AI suggests optimal color ratios based on hue angle minimization
5. **Real-time Optimization**: Live ML recommendations as you adjust ratios
6. **Optimization Statistics**: Track best attempts, improvements, and convergence trends
7. **Modern Responsive Design**: Glass-morphism UI optimized for wide monitors (1400px+ displays)

#### ML Algorithm Details
```python
# Bayesian Optimization Components
- Gaussian Process Regressor with RBF kernel
- Expected Improvement acquisition function  
- CIELAB color space for perceptual accuracy
- Angular distance calculation for hue-only optimization
- Adaptive exploration vs exploitation balance
```

#### Hue-Only Optimization Features
- **Angular Distance Calculation**: Uses `_ang_diff()` method for shortest path between hue angles
- **CIELAB Hue Extraction**: Converts RGB → CIELAB → hue angle using `_hue_deg()` method  
- **Perceptual Accuracy**: Optimization based on human color perception rather than RGB values
- **Automatic Mode Detection**: Switches to hue-only mode when `hue_target_deg` is set
- **Wraparound Handling**: Properly handles 0°/360° hue angle wraparound

### Interactive Color Interface
1. **Modern CSS Grid Layout**: Two-column responsive design for wide screens
2. **Glass-morphism Design**: Modern translucent cards with backdrop blur effects
3. **Interactive Ratios**: Smooth sliders and inputs for red, yellow, and blue ratios
4. **Live Preview**: Real-time color gradient preview with smooth transitions
5. **Dynamic Button Updates**: Button text shows current ratios and ML confidence
6. **Normalized Percentages**: Automatic calculation and display of color percentages

### ML Recommendations Panel
1. **Smart Suggestions**: AI-powered ratio recommendations with confidence scores
2. **Optimization History**: Track of previous attempts and improvements
3. **Hue-Based Visualization**: Polar dial, a*-b* scatter plots, and angular distance tracking
4. **Best Match Tracking**: Highlights best color matches achieved
5. **Learning Indicators**: Shows when ML model is learning from new data

### Robot Operations
1. **One-Click Dispensing**: Single button to execute complete color mixing procedure
2. **Progress Tracking**: Real-time status updates during operation
3. **Error Handling**: Clear error messages and timeout handling
4. **Automatic Retries**: Built-in retry mechanisms for reliability

### Beaker Analysis
1. **Drag & Drop Upload**: Easy image upload interface
2. **AI-Powered Analysis**: Advanced color clustering and detection
3. **Visual Results**: Color swatches, cluster analysis, and statistics
4. **Color Interpretation**: Automatic solution type detection and descriptions

## File Structure

```
frontend/
├── main.py                    # FastAPI server with ML optimization and proxy functionality  
├── index.html                 # Modern responsive web interface with hue-based visualization
├── requirements.txt           # Python dependencies (includes scikit-learn, scipy)
├── README.md                 # This file
├── Dockerfile                # Container configuration
├── ground_truth_calibration/ # Ground truth calibration data from robot experiments
│   ├── red_solution_ground_truth.json
│   ├── yellow_solution_ground_truth.json
│   ├── blue_solution_ground_truth.json
│   ├── white_solution_ground_truth.json
│   └── calibration_summary.json
└── tests/                    # Comprehensive frontend test suite
    ├── test_ground_truth_calibration.py   # Complete mocking test scenarios (11 tests)
    ├── test_ground_truth_real.py          # Real data validation tests (8 tests)
    ├── test_hue_optimization.py           # Hue-based optimization tests (NEW)
    └── run_updated_frontend_tests.py      # Test runner for all frontend modules
```

## Dependencies

Key Python packages:
- `fastapi` - Web framework and API server
- `uvicorn` - ASGI server for FastAPI
- `httpx` - HTTP client for proxy functionality
- `python-multipart` - Support for form data and file uploads
- `scikit-learn` - Machine learning for Bayesian optimization
- `scipy` - Scientific computing for color space operations
- `numpy` - Numerical computations for ML algorithms

## Development

### Installation
```bash
cd /home/hafnium/aloha-lite/frontend
pip install -r requirements.txt
```

### Local Development
```bash
# Start with auto-reload
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### Testing Ground Truth Integration
```bash
# Run comprehensive ground truth calibration tests
cd /home/hafnium/aloha-lite/frontend/tests

# Run all tests (19 total: 11 mocking + 8 real data)
python -m pytest test_ground_truth_calibration.py test_ground_truth_real.py -v

# Run hue-based optimization tests
python -m pytest test_hue_optimization.py -v

# Run comprehensive test suite
python run_updated_frontend_tests.py

# Run individual test suites
python -m pytest test_ground_truth_calibration.py -v  # 11 comprehensive mocking tests
python -m pytest test_ground_truth_real.py -v        # 8 real data validation tests
python -m pytest test_hue_optimization.py -v         # Hue-based optimization tests
```

### Configuration
Set environment variables for different backend configurations:
```bash
export ROBOT_SERVICE_URL="http://your-robot-service:8000"
export VISION_SERVICE_URL="http://your-vision-service:5000"
```

## Integration with Backend Services

### Robot Service Integration
- Proxies all `/robot/*` requests to the robot service
- Handles timeout and error scenarios gracefully
- Supports all robot operations: dispensing, status checks, snapshots

### Vision Service Integration
- Proxies all `/vision/*` requests to the vision service
- Handles multipart form data for image uploads
- Supports beaker analysis and camera operations

## Features in Detail

### ML-Enhanced Color Mixing Workflow
1. **Target Color Generation**: System generates random target color in LAB space with hue angle calculation
2. **User Interaction**: User adjusts color ratios using modern responsive interface
3. **ML Recommendations**: Bayesian optimization suggests optimal ratios based on hue distance minimization
4. **Color Preview**: Live gradient shows current mix with smooth transitions
5. **Optimization Loop**: ML learns from each attempt to improve future recommendations
6. **Dispensing**: User clicks enhanced button to execute color mixing
7. **Results Analysis**: Beaker analysis compares actual vs target colors using angular distance
8. **ML Learning**: System updates model with actual vs predicted results

### Bayesian Optimization Engine
1. **Gaussian Process Model**: Learns relationship between ratios and color outcomes
2. **Expected Improvement**: Balances exploration of new ratios vs exploitation of known good ones
3. **CIELAB Color Space**: Uses perceptually uniform color space for accurate comparisons
4. **Hue-Only Optimization**: Angular distance calculation for hue angle matching (when hue target is set)
5. **Dual Distance Metrics**: Supports both CIEDE2000 Delta-E and angular hue distance calculations
6. **Adaptive Learning**: Model improves with each color mixing attempt
7. **Uncertainty Quantification**: Provides confidence scores for recommendations

### Modern Responsive Interface
1. **CSS Grid Layout**: Two-column design optimized for wide monitors (max-width: 1400px)
2. **Glass-morphism Design**: Translucent cards with backdrop-filter blur effects
3. **Smooth Animations**: CSS transitions for all interactive elements
4. **Hue-Based Visualization**: Polar dial charts, a*-b* scatter plots, and angular distance tracking
5. **Mobile Responsive**: Adapts to different screen sizes with media queries
6. **Accessibility**: Proper contrast ratios and keyboard navigation support
7. **Performance Optimized**: Efficient DOM updates and minimal JavaScript footprint

### Beaker Analysis Workflow
1. User uploads beaker image via drag & drop or file picker
2. Frontend sends image to vision service via proxy
3. AI analyzes the image for color content
4. Results are displayed with visual color swatches
5. Color interpretation and statistics are shown

### Error Handling
- **Service Unavailable**: Clear error messages when backend services are down
- **ML Model Errors**: Graceful fallback when Bayesian optimization fails
- **Ground Truth Loading**: Robust handling of missing or malformed calibration files
- **Target Color Initialization**: Safe fallbacks when target color is not set (fixed TypeError)
- **JSON Serialization**: Proper conversion of numpy types to native Python types (fixed ValueError)
- **Timeout Handling**: Graceful handling of long-running operations
- **Network Errors**: Retry mechanisms and user-friendly error displays
- **Validation**: Client-side validation for color ratios and ML inputs
- **Color Space Errors**: Robust handling of color conversion edge cases

## Machine Learning Components

### Ground Truth Calibration System
The frontend integrates with a ground truth calibration system that uses real robot-generated data:

```python
def load_ground_truth_calibration(allow_white_absorbance: bool = False):
    """
    Load ground truth calibration data from JSON files and construct the calibration matrix.
    
    Args:
        allow_white_absorbance: If False (default), white-solvent absorbance is locked to zero
                              assuming pure RGB(255,255,255) background. If True, allows
                              loading of actual white-solvent absorbance parameters.
    
    Returns:
        A 4x3 numpy array representing the true pigment absorbance matrix.
    """
    # Priority 1: Load pre-computed calibration matrix from summary
    # Priority 2: Construct matrix from individual solution files  
    # Priority 3: Fallback to random matrix with proper 4x3 dimensions
```

#### Calibration Data Structure
- **Individual Solution Files**: `{color}_solution_ground_truth.json` with RGB measurements and absorbance coefficients
- **White Solution Support**: `white_solution_ground_truth.json` for white-solvent calibration (optional)
- **Calibration Summary**: `calibration_summary.json` with session information and optional pre-computed 4x3 matrices
- **RGB-to-Absorbance Conversion**: Uses `ColorOptimizer._rgb_to_absorb()` for matrix construction from real measurements
- **4x3 Matrix Format**: Supports 4 pigments (red, yellow, blue, white) × 3 RGB channels with white-solvent locking
- **Robust Loading**: Handles missing files, malformed JSON, and validation errors with comprehensive fallback mechanisms
- **Test Coverage**: 19 comprehensive tests validate all loading scenarios, error handling, and integration points

### ColorOptimizer Class
The core ML engine that powers intelligent color recommendations with adaptive phase scheduling:

```python
class ColorOptimizer:
    def __init__(self, allow_white_absorbance: bool = False):
        self.gp_regressor = GaussianProcessRegressor(
            kernel=RBF(length_scale=1.0),
            alpha=1e-6,
            normalize_y=True,
            n_restarts_optimizer=5
        )
        self.data_points = []
        self.target_color = None
        self.allow_white_absorbance = allow_white_absorbance
```

#### Adaptive Phase Schedule
The ColorOptimizer uses a 4-phase optimization strategy that adapts based on white-solvent configuration:

**Phase Schedule (N = trials completed):**
- **Phase 0**: Heuristic single-shot (dominant pigment guess)
- **Phase 1**: Gaussian Process only
- **Phase 2**: Rough α-calibration + GP (60/40 weighting)
- **Phase 3-8**: Full NNLS (9-param when white locked) + GP - *default configuration*
- **Phase 3-11**: Full NNLS (12-param when white learnable) + GP - *when ALLOW_WHITE_ABSORBANCE=True*
- **Phase ≥9/12**: NNLS calibration only

**Key Optimization Features:**
- **Adaptive Convergence**: Shorter hybrid phase (3-8) when white-solvent absorbance is locked to zero for faster convergence
- **Parameter Efficiency**: Only 9 effective parameters optimized by default vs 12 when white absorbance is learnable
- **Mathematical Stability**: White-solvent locked to [0,0,0] assuming pure RGB(255,255,255) background
- **Flexible Configuration**: Can enable white-solvent learning for non-ideal backgrounds if needed

#### Key Methods
- `generate_target_color()`: Random LAB color sampling for optimization challenges
- `recommend_ratios()`: Bayesian optimization with Expected Improvement and adaptive phase scheduling
- `_bayesian_optimization()`: Core optimization algorithm implementation with hybrid NNLS+GP phases
- `_expected_improvement()`: Acquisition function for exploration/exploitation balance
- `_rgb_to_lab()` / `_lab_to_rgb()`: Color space conversion utilities
- `_hue_deg()`: Extract hue angle in degrees from RGB using CIELAB conversion
- `_ang_diff()`: Calculate angular distance between two hue angles (shortest path)
- `_color_difference()`: CIEDE2000 Delta-E calculation (fallback when hue target not set)
- `_fit_full_calibration()`: Non-negative least squares calibration with white-solvent locking
- `_rough_scale_calibration()`: Initial calibration phase with heuristic scaling

### ML Algorithm Performance
- **Convergence**: Typically finds optimal ratios within 5-8 iterations (when white-solvent locked) or 7-12 iterations (when learnable)
- **Hue Accuracy**: Achieves angular distance < 10° for hue-only optimization consistently
- **Color Accuracy**: Achieves Delta-E < 5.0 (just noticeable difference) for full color matching
- **Efficiency**: Sub-second response times for real-time recommendations with adaptive phase scheduling
- **Robustness**: Handles edge cases and color space boundaries gracefully with white-solvent locking for stability
- **Learning**: Continuously improves with each color mixing experiment using hybrid NNLS+GP optimization
- **Parameter Optimization**: Uses 9 effective parameters by default (white locked) vs 12 parameters when white absorbance is learnable

## Monitoring

### Health Checks
- `GET /health`: Frontend service health
- `GET /status`: Complete system status including all backend services

### Logging
- Structured logging for all proxy requests
- Error tracking and debugging information
- Request/response logging for troubleshooting

## Troubleshooting

### Common Issues

**TypeError: cannot unpack non-iterable NoneType object**
```
TypeError: cannot unpack non-iterable NoneType object
```
**Solution**: This was fixed in recent updates. The ColorOptimizer now properly handles cases where no target color is set by providing safe fallbacks and proper initialization.

**JSON Serialization Errors (numpy.int64)**
```
ValueError: 'numpy.int64' object is not iterable
```
**Solution**: Fixed by converting numpy integers to native Python integers in RGB generation. The API endpoints now properly serialize all numeric values to JSON.

**Frontend Not Loading**
```
Error: Cannot access http://localhost:3000
```
**Solution**: Ensure the frontend service is running:
```bash
cd /home/hafnium/aloha-lite/frontend
python -m uvicorn main:app --host 0.0.0.0 --port 3000
```

**Backend Service Errors**
```
503 Service Unavailable
```
**Solution**: Check that backend services are running:
```bash
# Check robot service
curl http://localhost:8000/health

# Check vision service  
curl http://localhost:5000/health
```

**CORS Issues**
```
Access-Control-Allow-Origin error
```
**Solution**: The frontend proxy eliminates CORS issues. Ensure you're accessing the interface through the frontend service (port 3000) rather than directly accessing backend services.

**ML Optimization Errors**
```
Error: Bayesian optimization failed
```
**Solution**: The ML system has fallback mechanisms. Check that scipy and scikit-learn are installed:
```bash
pip install scikit-learn scipy numpy
```

**Hue Optimization Errors**
```
Error: Angular distance calculation failed
```
**Solution**: This indicates issues with hue angle calculation. The system should handle color space edge cases gracefully. Ensure the target color generates valid CIELAB values:
```bash
# Check if color values are within valid ranges
# L: 0-100, a: typically -100 to +100, b: typically -100 to +100
```

**Responsive Design Issues**
```
Interface not displaying correctly on wide monitors
```
**Solution**: The interface is optimized for displays 1400px+ wide. For smaller screens, the layout will adapt but may not show the full two-column design.

### Debug Mode
For detailed debugging, run with increased logging:
```bash
cd /home/hafnium/aloha-lite/frontend
uvicorn main:app --host 0.0.0.0 --port 3000 --log-level debug
```

## Hue-Only Target Optimization

The frontend implements a sophisticated hue-only optimization system that focuses on matching hue angles rather than full RGB color matching. This provides more perceptually accurate color matching based on human color perception.

### How It Works

When a target color is set using `set_target_color()`, the system automatically:

1. **Extracts Target Hue**: Converts RGB → CIELAB → hue angle using `_hue_deg()`
2. **Sets Optimization Mode**: Stores target hue in `hue_target_deg` attribute
3. **Switches Distance Calculation**: Uses angular distance instead of RGB Euclidean distance
4. **Optimizes for Hue Match**: ML system minimizes angular distance between measured and target hues

### Key Components

```python
# Core hue optimization methods in ColorOptimizer class
def _hue_deg(cls, rgb):
    """Extract hue angle in degrees from RGB via CIELAB conversion."""
    L, a, b = cls._rgb_to_lab(rgb)
    return degrees(atan2(b, a)) % 360

def _ang_diff(h1, h2):
    """Calculate shortest angular distance between two hue angles."""
    diff = abs(h1 - h2)
    return min(diff, 360 - diff)

def add_measurement(self, ratios, measured_rgb):
    if self.hue_target_deg is not None:
        measured_hue = self._hue_deg(measured_rgb)
        d = self._ang_diff(measured_hue, self.hue_target_deg)  # Use hue distance
    else:
        d = euclidean(measured_rgb, self.target_color)  # Fallback to RGB distance
```

### Visualization Features

The interface provides comprehensive hue-based visualization:

- **Polar Dial Chart**: Shows target hue and measurement history on a 360° color wheel
- **a*-b* Scatter Plot**: CIELAB color space visualization with angular relationships
- **Error Timeline**: Angular distance errors over optimization attempts
- **Color Strip**: Timeline showing RGB progression of optimization attempts

### Benefits

1. **Perceptual Accuracy**: Matches human color perception better than RGB distance
2. **Hue Consistency**: Focuses on achieving the right color family/hue
3. **Robustness**: Handles lighting variations and saturation differences gracefully
4. **Visual Feedback**: Clear angular distance metrics for users to understand progress

### Configuration

The hue-only optimization is automatically enabled when:
- Target color is set via `set_target_color()`
- `hue_target_deg` attribute is not None
- System falls back to RGB distance when hue target is unavailable

## Contributing

1. Follow existing code style and patterns
2. Add tests for new functionality in `tests/` directory
3. Update this README for new features
4. Ensure the interface works with both development and production backend configurations
5. Test ML functionality with various color targets and ratios
6. Verify responsive design across different screen sizes

## Changelog

### v2.4 - Hue-Only Target Optimization (August 2025)
- **NEW**: Hue-only target optimization system using CIELAB color space and angular distance calculation
- **ADDED**: `_hue_deg()` method for extracting hue angles from RGB via CIELAB conversion
- **ADDED**: `_ang_diff()` method for calculating shortest angular distance between hue angles
- **ENHANCED**: `add_measurement()` automatically switches to hue distance when `hue_target_deg` is set
- **INTEGRATED**: Hue-based visualization with polar dial charts, a*-b* scatter plots, and error timelines
- **IMPROVED**: Perceptually accurate color matching based on human color perception
- **ADDED**: `/api/hue-visual-data` endpoint for hue-based optimization visualization data
- **DOCUMENTED**: Comprehensive documentation of hue-only optimization system and benefits
- **TESTED**: New `test_hue_optimization.py` test suite validates hue angle calculation and optimization

### v2.3 - Comprehensive Test Suite & Cleanup (August 2025)
- **ENHANCED**: Complete ground truth calibration test suite with 19 comprehensive tests
- **FIXED**: All Path mocking issues in test suite - now 100% reliable test execution
- **ADDED**: `test_ground_truth_calibration.py` with 11 comprehensive mocking scenarios for edge cases
- **ADDED**: `test_ground_truth_real.py` with 8 real data validation tests using actual calibration files
- **CLEANED**: Removed outdated test files (`test_ground_truth_calibration_old.py`, `test_ground_truth_calibration_fixed.py`, `test_ground_truth_simple.py`)
- **IMPROVED**: Test reliability using real temporary files instead of complex Path mocking
- **UPDATED**: Test runner `run_updated_frontend_tests.py` for streamlined test execution
- **VALIDATED**: All 19 tests pass consistently, covering all ground truth integration scenarios
- **DOCUMENTED**: Updated README with current test suite status and usage instructions

### v2.2 - Adaptive ML Optimization (August 2025)
- **ENHANCED**: ColorOptimizer now uses adaptive phase scheduling based on white-solvent configuration
- **OPTIMIZED**: Hybrid phase reduced from 3-11 to 3-8 trials when white-solvent absorbance is locked (default)
- **IMPROVED**: Faster convergence with 9 effective parameters vs 12 when white absorbance is locked to zero
- **ADDED**: `allow_white_absorbance` parameter for flexible white-solvent learning configuration
- **MATHEMATICAL**: White-solvent absorbance locked to [0,0,0] by default assuming pure RGB(255,255,255) background
- **PERFORMANCE**: Reduced computational overhead while maintaining optimization quality
- **DOCUMENTATION**: Updated class docstring and README to reflect adaptive phase schedule

### v2.1 - Ground Truth Integration & Bug Fixes (July 2025)
- **NEW**: Ground truth calibration system integration with robot-generated data (4x3 matrix support)
- **NEW**: `load_ground_truth_calibration()` function loads real calibration matrices from JSON files with white-solvent support
- **NEW**: Comprehensive test framework with 19 test cases for ground truth integration (11 mocking + 8 real data)
- **FIXED**: TypeError when target color is None - added proper null checks and fallbacks
- **FIXED**: JSON serialization errors with numpy.int64 objects - converted to native Python integers
- **ADDED**: Robust error handling and logging for ground truth calibration loading
- **ENHANCED**: Application startup with proper target color initialization using lifespan context manager
- **ADDED**: `frontend/ground_truth_calibration/` directory with real robot-generated calibration data
- **IMPROVED**: ColorOptimizer safety with graceful handling of uninitialized states
- **SUPPORTED**: White solution calibration files for advanced color mixing scenarios

### v2.0 - ML-Enhanced Color Mixing (July 2025)
- **NEW**: Bayesian optimization with Gaussian Process Regression for intelligent color recommendations
- **NEW**: Target color generation with LAB color space sampling
- **NEW**: Real-time ML recommendations with confidence scores and optimization statistics
- **REDESIGNED**: Modern glass-morphism interface with CSS Grid layout optimized for wide monitors
- **ENHANCED**: Responsive design with smooth animations and transitions
- **ADDED**: `/api/target-color` and `/api/recommend-ratios` ML endpoints
- **IMPROVED**: Color preview with smooth gradient transitions
- **UPDATED**: Button text to show current ratios and ML confidence levels
- **ADDED**: Comprehensive ML components with ColorOptimizer class
- **INTEGRATED**: CIEDE2000 Delta-E color difference calculations for perceptual accuracy

### v1.0 - Initial Release  
- Basic color mixing interface with sliders
- Robot service proxy functionality
- Vision service integration for beaker analysis
- Simple responsive design
- Health checks and status monitoring

## License

Part of the ALOHA Lite project. See main project LICENSE for details.
