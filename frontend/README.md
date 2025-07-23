# Frontend Service

A FastAPI-based web interface for the ALOHA Lite robot system. This service provides a user-friendly web interface for color mixing, robot control, and beaker analysis, while acting as a proxy to avoid CORS issues between the frontend and backend services.

## Features

- 🎨 **Color Mixing Interface**: Interactive web UI for specifying color ratios (red, yellow, blue)
- 🤖 **Robot Control**: Direct interface to robot dispensing and positioning operations
- 🧪 **Beaker Analysis**: Upload and analyze beaker images with AI-powered color detection
- 🔄 **Service Proxy**: Eliminates CORS issues by proxying requests to backend services
- 📊 **Real-time Monitoring**: Live status updates and progress tracking
- 🎯 **Visual Feedback**: Color preview, analysis results, and operation logging

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
│   (Port 3000)   │    │  (FastAPI)      │    │  (Port 8000)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Vision Bridge   │
                       │  (Port 5000)    │
                       └─────────────────┘
```

## API Endpoints

### Frontend Interface
- `GET /` - Main web interface (serves index.html)
- `GET /health` - Frontend service health check
- `GET /status` - Check status of all backend services

### Proxy Endpoints
- `POST /robot/dispense` - Proxy to robot service for color mixing operations
- `GET /robot/{cmd_id}/status` - Proxy to robot service for operation status
- `GET /robot/{cmd_id}/pose-snapshot` - Proxy to robot service for snapshots
- `POST /vision/analyze-beaker` - Proxy to vision service for beaker analysis

## Web Interface Features

### Color Mixing
1. **Interactive Ratios**: Adjust red, yellow, and blue color ratios with sliders/inputs
2. **Live Preview**: Real-time color gradient preview of the mix
3. **Dynamic Button**: Button text updates to show current ratios
4. **Normalized Percentages**: Automatic calculation of color percentages

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
├── main.py              # FastAPI server with proxy functionality
├── index.html           # Main web interface
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── Dockerfile          # Container configuration
└── tests/              # Frontend tests
```

## Dependencies

Key Python packages:
- `fastapi` - Web framework and API server
- `uvicorn` - ASGI server for FastAPI
- `httpx` - HTTP client for proxy functionality
- `python-multipart` - Support for form data and file uploads

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

### Color Mixing Workflow
1. User adjusts color ratios in the web interface
2. Frontend calculates normalized percentages
3. User clicks "Dispense Mix & Snap" button
4. Frontend sends request to robot service via proxy
5. Real-time status updates are displayed
6. Final snapshot and beaker analysis results are shown

### Beaker Analysis Workflow
1. User uploads beaker image via drag & drop or file picker
2. Frontend sends image to vision service via proxy
3. AI analyzes the image for color content
4. Results are displayed with visual color swatches
5. Color interpretation and statistics are shown

### Error Handling
- **Service Unavailable**: Clear error messages when backend services are down
- **Timeout Handling**: Graceful handling of long-running operations
- **Network Errors**: Retry mechanisms and user-friendly error displays
- **Validation**: Client-side validation for color ratios and inputs

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

**File Upload Failures**
```
Vision service proxy error
```
**Solution**: Verify vision service is running and accessible:
```bash
REQUIRE_S3=false python -m uvicorn vision_bridge.main:app --host 0.0.0.0 --port 5000
```

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

## License

Part of the ALOHA Lite project. See main project LICENSE for details.
