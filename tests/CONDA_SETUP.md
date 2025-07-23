# ALOHA-Lite Conda Environment Setup Guide

## Recommended Python Version
**Python 3.11** is the recommended version for aloha-lite, as used in the Docker containers and tested configurations.

## Quick Setup

### 1. Create the conda environment
```bash
conda create -n aloha-lite python=3.11 -y
conda activate aloha-lite
```

### 2. Install core dependencies
```bash
# Core robot control dependencies
pip install -r ../requirements.txt

# Development dependencies (optional but recommended)
pip install -r ../requirements-dev.txt
```

### 3. Install service-specific dependencies (if needed)
```bash
# For vision bridge development
pip install -r ../vision_bridge/requirements.txt

# For robot service development  
pip install -r ../robot_service/requirements.txt
```

## Detailed Setup Steps

### Step 1: Create and activate environment
```bash
# Create new environment with Python 3.11
conda create -n aloha-lite python=3.11 numpy matplotlib opencv -y

# Activate the environment
conda activate aloha-lite
```

### Step 2: Install core requirements
```bash
# Install main project dependencies
pip install -r ../requirements.txt
```

### Step 3: Install development tools (recommended)
```bash
# Install development and testing tools
pip install -r ../requirements-dev.txt
```

### Step 4: Install service dependencies (if developing specific services)

For **vision bridge** development:
```bash
pip install -r ../vision_bridge/requirements.txt
# Additional vision dependencies
conda install opencv -y
```

For **robot service** development:
```bash
pip install -r ../robot_service/requirements.txt
```

### Step 5: Verify installation
```bash
# Test core imports
python -c "import numpy, requests, modern_robotics; print('Core dependencies OK')"

# Test development tools
python -c "import pytest, matplotlib, pandas; print('Dev dependencies OK')"

# Test vision dependencies (if installed)
python -c "import cv2, fastapi; print('Vision dependencies OK')"
```

## Environment.yml Alternative

You can also create an `environment.yml` file for easier setup:

```yaml
name: aloha-lite
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - numpy>=1.20.0
  - matplotlib>=3.3.0
  - pandas>=1.2.0
  - scipy>=1.6.0
  - opencv
  - jupyter
  - pytest>=6.0.0
  - black>=21.0.0
  - pip
  - pip:
    - requests>=2.25.0
    - modern_robotics>=1.0.0
    - typeguard
    - fastapi
    - uvicorn[standard]
    - httpx
    - boto3
    - python-multipart
    - prometheus-client
    - pyzmq
    - pydantic
    - pytest-cov>=2.10.0
    - flake8>=3.8.0
    - mypy>=0.800
    - sphinx>=3.5.0
    - sphinx-rtd-theme>=0.5.0
```

Then create the environment with:
```bash
conda env create -f environment.yml
conda activate aloha-lite
```

## Managing the Environment

### Activate environment
```bash
conda activate aloha-lite
```

### Deactivate environment
```bash
conda deactivate
```

### Update environment
```bash
conda activate aloha-lite
pip install --upgrade -r ../requirements.txt -r ../requirements-dev.txt
```

### Remove environment
```bash
conda env remove -n aloha-lite
```

### Export current environment
```bash
conda activate aloha-lite
conda env export > environment.yml
```

## Development Workflow

1. **Activate environment**: `conda activate aloha-lite`
2. **Run tests**: `python -m pytest tests/`
3. **Format code**: `black .`
4. **Check linting**: `flake8`
5. **Type checking**: `mypy .`

## Troubleshooting

### Common Issues

1. **OpenCV installation issues**:
   ```bash
   conda install opencv -c conda-forge
   ```

2. **ModernRobotics import errors**:
   ```bash
   pip install --upgrade modern_robotics
   ```

3. **FastAPI/Vision dependencies conflicts**:
   ```bash
   pip install --upgrade fastapi uvicorn httpx
   ```

### Platform-specific Notes

**Windows**: 
- Use Anaconda Prompt or PowerShell
- Some packages may require Visual Studio Build Tools

**macOS**: 
- Ensure Xcode Command Line Tools are installed
- May need to install additional OpenCV dependencies

**Linux**: 
- Install system dependencies for OpenCV:
  ```bash
  sudo apt-get install libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgl1-mesa-glx
  ```

## Testing the Setup

After setup, verify everything works:

```bash
# Activate environment
conda activate aloha-lite

# Test core functionality
python -c "
import numpy as np
import requests
import modern_robotics as mr
print('✅ Core dependencies working')
"

# Test development tools
python -c "
import pytest
import matplotlib.pyplot as plt
import pandas as pd
print('✅ Development tools working')
"

# Run project tests
cd ../vision_bridge/tests
python run_tests.py --type unit
```

## Environment Information

- **Python Version**: 3.11 (recommended, matches Docker containers)
- **Package Manager**: conda + pip hybrid approach
- **Key Dependencies**: numpy, requests, modern_robotics, fastapi, opencv
- **Development Tools**: pytest, black, flake8, mypy, jupyter
- **Architecture**: Supports multi-service development (robot_service, vision_bridge, frontend)
