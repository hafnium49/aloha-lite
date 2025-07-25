# Vision Bridge Service

The Vision Bridge is a FastAPI-based service that provides computer vision capabilities for the ALOHA Lite robot system. It handles image processing, beaker analysis, camera snapshots, and integrates with S3 storage for image management. The service now includes advanced SAM 2 integration for enhanced segmentation capabilities.

## Features

- 🔍 **Beaker Analysis**: AI-powered color detection and clustering analysis of beaker solutions
- 🎯 **Center-Weighted Detection**: Enhanced beaker detection optimized for center-positioned beakers
- 🤖 **SAM 2 Integration**: Advanced semantic segmentation with Meta's SAM 2.1 models (optional)
- 📸 **Camera Snapshots**: Capture and store images from connected cameras
- 🎨 **Color Processing**: Advanced color space analysis with K-means clustering
- ☁️ **S3 Integration**: Optional cloud storage for images (can be disabled for local development)
- 📊 **Prometheus Metrics**: Built-in monitoring and metrics collection
- 🔄 **Circle Detection**: Automated beaker detection using computer vision with adaptive parameters
- 🧪 **Graceful Fallback**: Robust operation with or without SAM 2 models

## Quick Start

### Development Mode (No S3 Required)

```bash
cd /home/hafnium/aloha-lite/vision_bridge
REQUIRE_S3=false python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

### Production Mode (S3 Required)

```bash
cd /home/hafnium/aloha-lite/vision_bridge
export S3_ENDPOINT="your-s3-endpoint"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export BUCKET="snapshots"
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REQUIRE_S3` | No | `true` | Set to `false` to disable S3 requirements for local development |
| `TESTING` | No | `false` | Set to `true` to disable Prometheus server startup during testing |
| `SAM_CHECKPOINT` | No | - | Path to SAM 2 model checkpoint file (enables SAM segmentation) |
| `SAM_CONFIG` | No | - | Path to SAM 2 model configuration file |
| `S3_ENDPOINT` | Yes* | - | S3-compatible storage endpoint URL |
| `AWS_ACCESS_KEY_ID` | Yes* | - | AWS access key for S3 authentication |
| `AWS_SECRET_ACCESS_KEY` | Yes* | - | AWS secret key for S3 authentication |
| `BUCKET` | No | `snapshots` | S3 bucket name for storing images |
| `PHOS_URL` | No | `http://phosphobot` | Phosphobot camera service URL |

*Required only when `REQUIRE_S3=true` (production mode)

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Camera Operations
- `POST /snap` - Capture a snapshot from the camera
  - Returns image URL (S3 presigned URL or local fallback)

### Beaker Analysis
- `POST /analyze-beaker` - Analyze uploaded beaker image
  - **Input**: Multipart form data with image file
  - **Output**: Comprehensive color analysis results

#### Beaker Analysis Response Format
```json
{
  "dominant_color": {
    "hex": "#ff0000",
    "rgb": [255, 0, 0]
  },
  "beaker_circle": {
    "x": 320,
    "y": 240,
    "radius": 150
  },
  "clusters": [
    {
      "rgb": [255, 0, 0],
      "hex": "#ff0000",
      "pixel_count": 1500,
      "saturation": 0.85
    }
  ],
  "analysis_stats": {
    "num_clusters": 3,
    "total_pixels_analyzed": 5000
  },
  "visualization_image": "base64-encoded-image"
}
```

## Computer Vision Pipeline

### SAM 2 Enhanced Analysis (v3.0)
When SAM 2 is available, the vision bridge leverages Meta's Segment Anything Model 2.1 for advanced segmentation:

1. **Hough Circle Detection**: Initial beaker location using traditional computer vision
2. **SAM 2 Segmentation**: High-precision mask generation using the detected circle as a prompt
3. **Hybrid Analysis**: Combines circle detection (70%) with SAM segmentation (30%) for optimal accuracy
4. **Graceful Fallback**: Automatically falls back to circle-only detection if SAM 2 is unavailable

#### SAM 2 Integration Features
- **Multiple Model Support**: Compatible with SAM 2.1 tiny, small, base_plus, and large variants
- **Automatic Setup**: Use `setup_sam2.py` script for easy model and configuration download
- **Performance Optimization**: Efficient GPU/CPU utilization with model caching
- **Quality Enhancement**: Superior edge detection and segmentation accuracy

### Enhanced Beaker Detection (v2.0)
The vision bridge features an improved center-weighted detection algorithm optimized for beakers positioned near the image center:

1. **Hough Circle Transform**: Detects all circular objects in the image
2. **Center-Weighted Scoring**: Combines circle size (30%) and center proximity (70%) to rank candidates
3. **Adaptive Parameters**: Automatically scales detection parameters based on image dimensions
4. **Fallback Logic**: Maintains compatibility with edge-case scenarios

#### Detection Algorithm
```python
# Center-weighted scoring formula
score = 0.7 * center_score + 0.3 * size_score

# Where:
# center_score = 1 - (distance_from_center / max_distance)
# size_score = radius / max_radius_found
```

#### Key Improvements
- **Higher Accuracy**: Prioritizes center-located beakers (typical use case)
- **Robust Performance**: Handles multiple circular objects in frame
- **Adaptive Scaling**: Works across different image resolutions
- **Enhanced Logging**: Detailed debugging information for circle selection

### Beaker Detection (Legacy)
1. **Circle Detection**: Uses Hough Circle Transform to locate beaker in image
2. **Region Extraction**: Extracts circular region of interest
3. **Color Analysis**: Performs K-means clustering on extracted pixels

### Color Analysis
1. **Preprocessing**: Image enhancement and noise reduction
2. **Color Space Conversion**: RGB → HSV for better color separation
3. **Clustering**: K-means algorithm groups similar colors
4. **Dominant Color**: Identifies most prominent color by pixel count and saturation

## Monitoring

The service exposes Prometheus metrics on port 9003:

- `cam_snapshot_ok_total` - Successful camera snapshots
- `cam_snapshot_err_total` - Failed camera snapshots  
- `circle_detect_ok_total` - Successful circle detections
- `circle_detect_err_total` - Failed circle detections

## Dependencies

Key Python packages:
- `fastapi` - Web framework
- `opencv-python` - Computer vision operations
- `scikit-learn` - Machine learning (K-means clustering)
- `numpy` - Numerical computations
- `boto3` - AWS S3 integration
- `prometheus-client` - Metrics collection
- `sam2>=1.1.0` - Meta's Segment Anything Model 2 (optional)
- `torch` - PyTorch deep learning framework (for SAM 2)

## SAM 2 Setup

### Automatic Setup (Recommended)
```bash
cd /home/hafnium/aloha-lite/vision_bridge
python setup_sam2.py
```

This script will:
- Download and set up the SAM 2 repository
- Download your chosen model checkpoint
- Create environment configuration files
- Test the installation

### Manual Setup
1. **Install SAM 2 package**:
   ```bash
   pip install sam2>=1.1.0
   ```

2. **Download model checkpoints**:
   ```bash
   # Available models: sam2.1_hiera_tiny.pt, sam2.1_hiera_small.pt, 
   #                   sam2.1_hiera_base_plus.pt, sam2.1_hiera_large.pt
   wget -P /models/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
   ```

3. **Set environment variables**:
   ```bash
   export SAM_CHECKPOINT="/models/sam2.1_hiera_large.pt"
   export SAM_CONFIG="configs/sam2.1/sam2.1_hiera_l.yaml"
   ```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│  Vision Bridge  │───▶│   Camera/S3     │
│   (Web UI)      │    │   (Port 5000)   │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Prometheus    │
                       │   (Port 9003)   │
                       └─────────────────┘
```

## Development

### Running Tests
The comprehensive test suite is located in `/tests` directory with organized structure:

```bash
cd /home/hafnium/aloha-lite/vision_bridge/tests

# Run all tests via test runner
python run_tests.py --type all

# Run specific test categories
python run_tests.py --type unit      # Unit tests
python run_tests.py --type api       # API integration tests
python run_tests.py --type sam2      # SAM 2 integration tests
python run_tests.py --type container # Container-based tests

# Run individual tests
python test_beaker_analysis.py
python test_sam2_integration.py
```

### Test Categories

The test suite includes:

#### Core Vision Tests
- **Beaker analysis validation**: Color detection and clustering accuracy
- **Center-weighted detection**: Algorithm performance with various beaker positions
- **API endpoint testing**: Full integration tests with running server
- **Circle detection**: Hough transform parameter validation

#### SAM 2 Integration Tests
- **Import and functionality testing**: SAM 2 package integration
- **Model loading and inference**: Checkpoint compatibility verification
- **Visualization generation**: Output quality and format validation
- **Graceful fallback testing**: Behavior when SAM 2 is unavailable
- **Environment configuration**: Variable and path validation

#### Test Results
- Test visualizations are saved to `tests/test_results/` directory
- JSON analysis data includes beaker coordinates, colors, and cluster information
- SAM 2 test outputs include segmentation masks and hybrid analysis results

### Local Development Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (see above)
3. Run in development mode: `REQUIRE_S3=false uvicorn main:app --reload --port 5000`

## Troubleshooting

### Common Issues

**S3_ENDPOINT Error**
```
ERROR:main:S3_ENDPOINT environment variable is required
```
**Solution**: Set `REQUIRE_S3=false` for local development or configure S3 variables for production.

**Camera Connection Failed**
```
Camera error: 502
```
**Solution**: Verify `PHOS_URL` points to accessible camera service.

**SAM 2 Not Available**
```
WARNING:main:SAM checkpoint not found (/models/sam2.1_hiera_large.pt); SAM disabled
```
**Solution**: Install SAM 2 using `python setup_sam2.py` or set `SAM_CHECKPOINT` environment variable. Service continues with circle detection fallback.

**Model Loading Error**
```
ERROR: Failed to load SAM model
```
**Solution**: Verify SAM checkpoint file exists and is compatible. Check `SAM_CONFIG` path points to correct configuration file.

**Circle Detection Failed**
```
No beaker detected in image
```
**Solution**: Ensure image contains a clear circular beaker with good contrast. The enhanced algorithm works best with beakers positioned near the center of the image.

**Beaker Detection Accuracy Issues**
```
INFO:main:Beaker detection: found X circles, selected (x, y, r=radius) with score 0.XXX
```
**Solution**: Check the logged center distance. For optimal results, position beakers within the center region of the camera frame. The algorithm prioritizes circles closer to the image center.

### Debug Mode
Add logging configuration for detailed debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Robot Service

The Vision Bridge works in conjunction with the Robot Service:
- Robot Service calls Vision Bridge for beaker analysis during color mixing operations
- Images are analyzed and results returned to enhance automation accuracy
- Both services can run independently for development and testing

## Contributing

1. Follow existing code style and patterns
2. Add tests for new functionality
3. Update this README for new features
4. Ensure both development and production modes work correctly

## Changelog

### v3.0 - SAM 2 Integration (July 2025)
- **NEW**: Meta SAM 2.1 integration for advanced semantic segmentation
- **ADDED**: Support for all SAM 2.1 model variants (tiny, small, base_plus, large)
- **ENHANCED**: Hybrid analysis combining circle detection with SAM segmentation
- **IMPROVED**: Automatic setup script for easy SAM 2 configuration
- **ADDED**: Comprehensive SAM 2 test suite with unittest integration
- **UPDATED**: Graceful fallback when SAM 2 models are unavailable
- **ORGANIZED**: Restructured test files in dedicated tests/ directory
- **ENHANCED**: Test result organization in test_results/ subdirectory

### v2.0 - Center-Weighted Detection (July 2025)
- **NEW**: Implemented center-weighted beaker detection algorithm
- **IMPROVED**: 70% center proximity + 30% size scoring for better accuracy
- **ENHANCED**: Adaptive parameter scaling based on image dimensions
- **ADDED**: Comprehensive test suite with synthetic beaker generation
- **FIXED**: Robust handling of multiple circular objects in frame
- **UPDATED**: Enhanced logging for detection debugging and monitoring

### v1.0 - Initial Release
- Basic Hough Circle Transform detection
- K-means color clustering analysis
- S3 integration for image storage
- FastAPI web service framework
- Prometheus metrics collection

## License

Part of the ALOHA Lite project. See main project LICENSE for details.
