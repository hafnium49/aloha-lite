# Vision Bridge Service

The Vision Bridge is a FastAPI-based service that provides computer vision capabilities for the ALOHA Lite robot system. It handles image processing, beaker analysis, camera snapshots, and integrates with S3 storage for image management.

## Features

- 🔍 **Beaker Analysis**: AI-powered color detection and clustering analysis of beaker solutions
- 📸 **Camera Snapshots**: Capture and store images from connected cameras
- 🎨 **Color Processing**: Advanced color space analysis with K-means clustering
- ☁️ **S3 Integration**: Optional cloud storage for images (can be disabled for local development)
- 📊 **Prometheus Metrics**: Built-in monitoring and metrics collection
- 🔄 **Circle Detection**: Automated beaker detection using computer vision

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

### Beaker Detection
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
```bash
cd /home/hafnium/aloha-lite/vision_bridge
python -m pytest tests/ -v
```

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

**Circle Detection Failed**
```
No beaker detected in image
```
**Solution**: Ensure image contains a clear circular beaker with good contrast.

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

## License

Part of the ALOHA Lite project. See main project LICENSE for details.
