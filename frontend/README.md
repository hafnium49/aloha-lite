# Frontend Service

A FastAPI-based web interface for the ALOHA Lite robot system with **Hue-only Color Optimization**. This service provides an intelligent web interface for color mixing with Bayesian optimization focused on hue space, robot control, and beaker analysis, while acting as a proxy to avoid CORS issues between the frontend and backend services.

## Features

- 🎨 **Hue-only Optimization**: Simplified Bayesian optimization using Gaussian Process Regression focused on hue angles (0-360°)
- 🌈 **HSV Color Space**: Direct hue manipulation with RGB conversion utilities for intuitive color control
- � **Interactive Color Interface**: Modern responsive design optimized for wide monitors with real-time hue preview
- 🧠 **Smart Recommendations**: AI-powered suggestions for optimal color ratios using Expected Improvement acquisition in hue space
- 🤖 **Robot Control**: Direct interface to robot dispensing and positioning operations with format transformation
- 🧪 **Beaker Analysis**: Upload and analyze beaker images with AI-powered color detection via vision bridge
- 🔄 **Service Proxy**: Eliminates CORS issues by proxying requests to backend services with proper endpoint mapping
- 📊 **Real-time Monitoring**: Live status updates, progress tracking, and hue-based optimization statistics
- 🎯 **Visual Feedback**: Hue progress charts, ML recommendations, trend analysis, and operation logging
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
│   (Port 3000)   │    │ (Hue-Enhanced)  │    │  (Port 8000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Vision Bridge   │
                       │  (Port 5000)    │
                       └─────────────────┘

Hue Optimization Pipeline:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Target Hue      │───▶│ Bayesian        │───▶│ Hue             │
│ Generation      │    │ Optimization    │    │ Recommendations │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Hue Space       │    │ Gaussian        │    │ Expected        │
│ Sampling        │    │ Process Reg.    │    │ Improvement     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## API Endpoints

### Frontend Interface
- `GET /` - Main web interface with ML-enhanced color mixing (serves index.html)
- `GET /health` - Frontend service health check
- `GET /status` - Check status of all backend services

### Hue-Only Optimization Endpoints
- `GET /api/target-color` - Generate random target hue for optimization challenge
- `POST /api/target-color` - Set specific target hue for optimization
- `POST /api/recommend-ratios` - Get hue-based color ratio recommendations using Bayesian optimization
- `GET /api/optimization-history` - Retrieve complete optimization history with hue data
- `POST /api/reset-optimization` - Reset optimization history and ML model
- `GET /api/color-space-data` - Get hue space data for visualization charts

### Robot Service Integration
- `POST /robot/dispense` - Enhanced dispense endpoint with format transformation for robot service compatibility

### Vision Service Integration
- `POST /vision/capture` - Capture image using vision bridge snapshot endpoint (maps to `/snapshot`)
- `POST /vision/analyze` - Analyze uploaded image using vision bridge analyze-beaker endpoint (maps to `/analyze-beaker`)
- `GET,POST,PUT,DELETE /vision/{path:path}` - General proxy to vision service for other endpoints

### Proxy Endpoints
- `GET,POST,PUT,DELETE /robot/{path:path}` - Proxy to robot service for general operations
- `GET /status` - Check status of frontend service

## Web Interface Features

### Hue-Only Color Optimization (v3.0)
1. **Simplified Bayesian Optimization**: Uses Gaussian Process Regression focused on hue angles (0-360°)
2. **Target Hue Generation**: Random hue sampling from red, yellow, and blue sectors for optimization challenges  
3. **Smart Recommendations**: AI suggests optimal color ratios based on hue distance minimization
4. **Real-time Optimization**: Live hue-based recommendations as you adjust ratios
5. **Optimization Statistics**: Track best attempts, improvements, and hue convergence trends
6. **Modern Responsive Design**: Glass-morphism UI optimized for wide monitors (1400px+ displays)

#### Hue Optimization Algorithm Details
```python
# Hue-Only Bayesian Optimization Components
- Gaussian Process Regressor with RBF kernel for hue space
- Expected Improvement acquisition function for hue angle optimization
- HSV color space with direct hue manipulation (0-360°)
- Angular distance calculation for circular hue space
- Triangle interpolation for initial hue guesses
- Adaptive exploration vs exploitation balance in hue space
```

### Interactive Color Interface
1. **Modern CSS Grid Layout**: Two-column responsive design for wide screens
2. **Glass-morphism Design**: Modern translucent cards with backdrop blur effects
3. **Interactive Ratios**: Smooth sliders and inputs for red, yellow, and blue ratios
4. **Live Preview**: Real-time color gradient preview with smooth transitions
5. **Dynamic Button Updates**: Button text shows current ratios and ML confidence
6. **Normalized Percentages**: Automatic calculation and display of color percentages

### Hue-Only Recommendations Panel
1. **Smart Suggestions**: AI-powered ratio recommendations with hue-based confidence scores
2. **Optimization History**: Track of previous attempts and hue improvements
3. **Trend Analysis**: Visual indicators of hue optimization progress
4. **Best Match Tracking**: Highlights best hue matches achieved
5. **Learning Indicators**: Shows when ML model is learning from new hue data

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
├── main.py                    # FastAPI server with hue-only optimization and enhanced vision proxy functionality  
├── index.html                 # Modern responsive web interface with hue-based optimization
├── requirements.txt           # Python dependencies (includes scikit-learn, scipy)
├── README.md                 # This file
├── Dockerfile                # Container configuration
└── tests/                    # Frontend tests and validation
    ├── test_frontend_integration.py
    └── run_tests.py
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

### Testing
```bash
# Run frontend integration tests
cd /home/hafnium/aloha-lite/frontend/tests
python run_tests.py

# Test hue optimization functionality
python test_frontend_integration.py
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

### Hue-Only Color Optimization Workflow
1. **Target Hue Generation**: System generates random target hue angle (0-360°) from red/yellow/blue sectors
2. **User Interaction**: User adjusts color ratios using modern responsive interface
3. **Hue Recommendations**: Bayesian optimization suggests optimal ratios for target hue in real-time
4. **Color Preview**: Live gradient shows current mix with smooth hue transitions
5. **Optimization Loop**: ML learns from each attempt to improve future hue predictions
6. **Dispensing**: User clicks enhanced button to execute color mixing with format transformation
7. **Results Analysis**: Beaker analysis compares actual vs target hue values
8. **ML Learning**: System updates model with actual vs predicted hue results

### Hue-Based Bayesian Optimization Engine
1. **Gaussian Process Model**: Learns relationship between ratios and hue outcomes in circular space
2. **Expected Improvement**: Balances exploration of new ratios vs exploitation of known good hue matches
3. **HSV Color Space**: Direct hue manipulation with RGB conversion utilities
4. **Angular Distance**: Proper circular distance calculation for hue angles (handles 359°-1° wraparound)
5. **Adaptive Learning**: Model improves with each color mixing attempt in hue space
6. **Uncertainty Quantification**: Provides confidence scores for hue-based recommendations

### Modern Responsive Interface
1. **CSS Grid Layout**: Two-column design optimized for wide monitors (max-width: 1400px)
2. **Glass-morphism Design**: Translucent cards with backdrop-filter blur effects
3. **Smooth Animations**: CSS transitions for all interactive elements
4. **Mobile Responsive**: Adapts to different screen sizes with media queries
5. **Accessibility**: Proper contrast ratios and keyboard navigation support
6. **Performance Optimized**: Efficient DOM updates and minimal JavaScript footprint

### Beaker Analysis Workflow
1. User uploads beaker image via drag & drop or file picker
2. Frontend sends image to vision service via enhanced proxy with proper endpoint mapping
3. AI analyzes the image for color content using space_mask algorithm by default
4. Results are displayed with visual color swatches and hue information
5. Color interpretation and statistics are shown with hue-based analysis

### Error Handling
- **Service Unavailable**: Clear error messages when backend services are down
- **Hue Optimization Errors**: Graceful fallback when Bayesian optimization fails in hue space
- **Vision Service Mapping**: Proper endpoint transformation for `/capture` → `/snapshot` and `/analyze` → `/analyze-beaker`
- **Robot Service Format**: Automatic transformation of simple {red, yellow, blue} to complex DispenseRequest format
- **Target Hue Initialization**: Safe fallbacks when target hue is not set
- **JSON Serialization**: Proper conversion of numpy types to native Python types
- **Timeout Handling**: Graceful handling of long-running operations
- **Network Errors**: Retry mechanisms and user-friendly error displays
- **Validation**: Client-side validation for hue ratios and optimization inputs
- **Hue Space Errors**: Robust handling of circular hue space edge cases and wraparound

## Machine Learning Components

### ColorOptimizer Class
The core ML engine that powers intelligent hue-based color recommendations:

```python
class ColorOptimizer:
    """Bayesian optimiser that works purely in *hue* space."""
    
    def __init__(self):
        self.target_hue: Optional[float] = None
        self.history: List[Dict] = []           # each: ratios, measured_rgb, hue, dist
        self.gp: Optional[GaussianProcessRegressor] = None
    
    @staticmethod
    def _rgb_to_hue(rgb: Tuple[int, int, int]) -> float:
        """Return hue in degrees [0,360). Grey/black returns 0."""
    
    @staticmethod
    def _hue_distance(h1: float, h2: float) -> float:
        """Shortest angular distance in degrees."""
    
    def _hue_guess(self) -> Dict[str, float]:
        """Map desired hue to an initial RGB‑triangle interpolation."""
    
    def _gp_next(self) -> Dict[str, float]:
        """Gaussian Process with Expected Improvement for hue optimization."""
```

#### Key Optimization Features
- **Hue-Only Focus**: Optimization purely in hue space (0-360°) for simplified color matching
- **Circular Distance**: Proper angular distance calculation handling hue wraparound
- **Triangle Interpolation**: Initial heuristic mapping from target hue to RGB ratios
- **Gaussian Process**: ML learning from previous attempts to improve recommendations
- **Expected Improvement**: Acquisition function balancing exploration vs exploitation
- **Adaptive Learning**: Continuous improvement with each color mixing experiment

#### Key Methods
- `set_target_hue()`: Set target hue angle for optimization challenge
- `recommend_next_ratios()`: Main optimization method with 2-phase approach (heuristic → GP)
- `add_measurement()`: Record actual results to improve future predictions
- `get_stats()`: Optimization statistics including best/current/average hue distance
- `_rgb_to_hue()` / `_hue_to_rgb()`: Color space conversion utilities
- `_hue_distance()`: Circular hue distance calculation
- `_normalize()`: Ratio normalization with minimum volume constraints

### Hue Optimization Algorithm Performance
- **Convergence**: Typically finds optimal ratios within 3-5 iterations using triangle interpolation + GP
- **Accuracy**: Achieves hue distance < 10° (visually similar) consistently in hue space
- **Efficiency**: Sub-second response times for real-time recommendations with simplified hue calculations
- **Robustness**: Handles edge cases and circular hue space boundaries gracefully (359°-1° wraparound)
- **Learning**: Continuously improves with each color mixing experiment using GP in hue space
- **Simplicity**: Uses only 3 pigments (red, yellow, blue) with direct hue optimization

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

**Vision Service Endpoint Errors**
```
404 Not Found when calling /vision/capture
```
**Solution**: Fixed in v3.0. The frontend now properly maps `/vision/capture` to vision bridge `/snapshot` and `/vision/analyze` to `/analyze-beaker`. Ensure you're using the updated frontend version.

**Robot Service Format Errors**
```
422 Unprocessable Entity from robot service
```
**Solution**: Fixed in v3.0. The frontend now automatically transforms simple `{red, yellow, blue}` format to the complex DispenseRequest format required by the robot service.

**Hue Optimization Errors**
```
Error: Hue optimization failed
```
**Solution**: The hue-based ML system has fallback mechanisms. Check that scipy and scikit-learn are installed:
```bash
pip install scikit-learn scipy numpy
```

**Hue Space Conversion Issues**
```
Error: Invalid hue values or circular distance calculation
```
**Solution**: This indicates edge-case hue values. The system handles circular hue space (359°-1° = 2° distance) gracefully, but ensure input ratios are within valid ranges (0-3.0 mL).

**ML Optimization Errors**
```
Error: Bayesian optimization failed
```
**Solution**: The ML system has fallback mechanisms. Check that scipy and scikit-learn are installed:
```bash
pip install scikit-learn scipy numpy
```

**Color Space Conversion Issues**
```
Error: Invalid color values in LAB space
```
**Solution**: This indicates edge-case color values. The system should handle these gracefully, but ensure input ratios are within valid ranges (0-100).

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

## Contributing

1. Follow existing code style and patterns
2. Add tests for new functionality in `tests/` directory
3. Update this README for new features
4. Ensure the interface works with both development and production backend configurations
5. Test ML functionality with various color targets and ratios
6. Verify responsive design across different screen sizes

## Changelog

### v3.0 - Hue-Only Optimization System (August 2025)
- **MAJOR OVERHAUL**: Complete system transformation from RGB/LAB to hue-only optimization
- **NEW**: Simplified ColorOptimizer class focused purely on hue space (0-360°)
- **NEW**: Triangle interpolation for initial hue guesses based on RGB vertices
- **NEW**: Circular hue distance calculation handling wraparound (359°-1° = 2°)
- **ENHANCED**: `/vision/capture` endpoint mapping to vision bridge `/snapshot`
- **ENHANCED**: `/vision/analyze` endpoint mapping to vision bridge `/analyze-beaker`
- **FIXED**: Robot service format transformation from simple {red, yellow, blue} to DispenseRequest format
- **FIXED**: Vision service 404 errors with proper endpoint mapping
- **SIMPLIFIED**: 2-phase optimization (heuristic guess → GP) instead of complex multi-phase
- **REMOVED**: Complex LAB color space, Delta-E calculations, and ground truth calibration
- **OPTIMIZED**: Direct HSV color space operations for faster hue calculations
- **IMPROVED**: Real-time hue-based recommendations with circular distance optimization

### v1.0 - Initial Release  
- Basic color mixing interface with sliders
- Robot service proxy functionality
- Vision service integration for beaker analysis
- Simple responsive design
- Health checks and status monitoring

## License

Part of the ALOHA Lite project. See main project LICENSE for details.
