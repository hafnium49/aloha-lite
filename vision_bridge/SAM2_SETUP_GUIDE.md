# SAM 2 Setup Guide for Vision Bridge

This guide helps you set up SAM 2 (Segment Anything Model 2) for enhanced beaker detection in the vision_bridge.

## Quick Start

### 1. Choose a Model

Available SAM 2.1 models:

| Model | Size | Speed | Description |
|-------|------|-------|-------------|
| `tiny` | 155MB | Fastest | Good for real-time applications |
| `small` | 185MB | Fast | Balanced speed and accuracy |
| `base_plus` | 323MB | Medium | Good accuracy with reasonable speed |
| `large` | 898MB | Slower | Best accuracy (recommended) |

### 2. Run Setup Script

```bash
# Navigate to vision_bridge directory
cd /home/hafnium/aloha-lite/vision_bridge

# Run setup script (recommended: large model for best accuracy)
python setup_sam2.py large

# Or choose a different model
python setup_sam2.py small
```

### 3. Activate SAM 2 Environment

```bash
# Source the generated environment script
source ./sam2_setup/setup_sam2_environment.sh

# Test the installation
python ./sam2_setup/test_vision_bridge_sam2.py
```

### 4. Test with Vision Bridge

```bash
# Test with the updated vision_bridge
python beaker_analysis.py
```

## Manual Setup (Alternative)

If you prefer manual setup:

### 1. Clone SAM 2 Repository

```bash
git clone https://github.com/facebookresearch/sam2.git
cd sam2
```

### 2. Download Model Checkpoint

```bash
# Create checkpoints directory
mkdir -p checkpoints

# Download SAM 2.1 Large model (recommended)
wget -O checkpoints/sam2.1_hiera_large.pt \
  https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
```

### 3. Set Environment Variables

```bash
export SAM_CHECKPOINT="/path/to/sam2/checkpoints/sam2.1_hiera_large.pt"
export SAM_CONFIG="/path/to/sam2/configs/sam2.1/sam2.1_hiera_l.yaml"
export PYTHONPATH="/path/to/sam2:$PYTHONPATH"
```

## Integration with Vision Bridge

Once SAM 2 is set up, the vision_bridge will automatically:

1. **Detect SAM 2 availability** - Check for checkpoint and config files
2. **Initialize SAM 2 predictor** - Load model if available
3. **Enhanced segmentation** - Use SAM 2 for more accurate beaker detection
4. **Graceful fallback** - Use circle detection if SAM 2 unavailable

## Performance Notes

- **GPU Recommended**: SAM 2 performs much better on GPU
- **Memory Requirements**: Large model needs ~4GB GPU memory
- **Speed vs Accuracy**: 
  - Tiny/Small: Real-time capable (~80+ FPS)
  - Base+/Large: Higher accuracy (~40-60 FPS)

## Troubleshooting

### Common Issues

1. **"sam2 not installed" warning**
   - This is expected - we use the repository directly
   - The vision_bridge handles this automatically

2. **CUDA out of memory**
   - Try a smaller model (tiny or small)
   - Reduce batch size if processing multiple images

3. **Config file not found**
   - Ensure the SAM 2 repository is properly cloned
   - Check that config path matches model name

4. **Checkpoint download fails**
   - Check internet connection
   - Try downloading manually from Meta's servers

### Environment Variables

Make sure these are set correctly:

```bash
echo $SAM_CHECKPOINT  # Should point to .pt file
echo $SAM_CONFIG      # Should point to .yaml file
echo $PYTHONPATH      # Should include sam2 repository path
```

## Model Comparison

### SAM 2.1 vs Circle Detection

| Method | Accuracy | Speed | Robustness |
|--------|----------|-------|------------|
| Circle Only | Good | Very Fast | Moderate |
| SAM 2.1 Tiny | Better | Fast | Good |
| SAM 2.1 Large | Best | Moderate | Excellent |

### When to Use Each Model

- **Tiny**: Real-time applications, resource-constrained environments
- **Small**: Balanced performance for most use cases
- **Base+**: Higher accuracy needed, moderate speed acceptable
- **Large**: Best possible accuracy, speed less critical

## Support

The vision_bridge automatically handles:
- Model loading and initialization
- Error handling and fallback
- Device selection (CUDA/CPU)
- Memory management

For issues, check the vision_bridge logs for SAM-related warnings or errors.
