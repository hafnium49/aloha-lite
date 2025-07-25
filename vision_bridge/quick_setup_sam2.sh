#!/bin/bash
# Quick setup script for SAM 2 with vision_bridge
# This sets up the SAM 2.1 tiny model for efficient performance

echo "🤖 SAM 2 Quick Setup for Vision Bridge"
echo "======================================="
echo "Setting up SAM 2.1 Tiny model (optimized for speed and efficiency)"
echo ""

# Check if we're in the right directory
if [[ ! -f "beaker_analysis.py" ]]; then
    echo "❌ Please run this script from the vision_bridge directory"
    echo "Usage: cd /home/hafnium/aloha-lite/vision_bridge && ./quick_setup_sam2.sh"
    exit 1
fi

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install SAM 2 from PyPI
echo "📥 Installing SAM 2 from PyPI..."
pip install sam2

# Create checkpoints directory
echo "📁 Creating checkpoints directory..."
mkdir -p checkpoints

# Download SAM 2.1 tiny model checkpoint
echo "📥 Downloading SAM 2.1 tiny model checkpoint..."
cd checkpoints
wget -O sam2.1_hiera_tiny.pt https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt
cd ..

# Create configs directory and download configuration
echo "📥 Downloading model configuration..."
mkdir -p configs/sam2.1
cd configs/sam2.1
wget -O sam2.1_hiera_t.yaml https://raw.githubusercontent.com/facebookresearch/sam2/main/sam2/configs/sam2.1/sam2.1_hiera_t.yaml
cd ../..

echo "📦 Installing additional dependencies..."
pip install huggingface_hub

# Check if installation was successful
if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 SAM 2 setup completed successfully!"
    echo ""
    echo "� Installation Summary:"
    echo "- SAM 2 installed via pip"
    echo "- Model: sam2.1_hiera_tiny.pt (38.9M parameters, 91.2 FPS)"
    echo "- Config: sam2.1_hiera_t.yaml"
    echo "- Location: ./checkpoints/sam2.1_hiera_tiny.pt"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Test the installation:"
    echo "   python -c \"import sam2; print('SAM 2 imported successfully')\""
    echo ""
    echo "2. Test with vision_bridge:"
    echo "   python beaker_analysis.py"
    echo ""
    echo "3. Alternative: Use Hugging Face model (no local files needed):"
    echo "   from sam2.sam2_image_predictor import SAM2ImagePredictor"
    echo "   predictor = SAM2ImagePredictor.from_pretrained('facebook/sam2-hiera-tiny')"
    echo ""
    echo "The vision_bridge will now automatically use SAM 2 for enhanced beaker detection!"
    echo ""
    echo "📊 Model Performance:"
    echo "- Size: 38.9M parameters"
    echo "- Speed: 91.2 FPS on A100"
    echo "- SA-V test (J&F): 76.5"
    echo "- Optimized for real-time applications"
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    echo "You can try:"
    echo "- Check internet connection"
    echo "- Verify conda environment: conda activate aloha-lite"
    echo "- Manual installation: pip install sam2"
    echo "- Check available disk space"
    echo ""
    echo "Alternative approach using Hugging Face:"
    echo "pip install huggingface_hub"
    echo "# Then use: SAM2ImagePredictor.from_pretrained('facebook/sam2-hiera-tiny')"
fi
