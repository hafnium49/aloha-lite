#!/bin/bash
# Quick setup script for SAM 2 with vision_bridge
# This sets up the recommended large model for best accuracy

echo "🤖 SAM 2 Quick Setup for Vision Bridge"
echo "======================================="
echo "Setting up SAM 2.1 Large model (recommended for best accuracy)"
echo ""

# Check if we're in the right directory
if [[ ! -f "beaker_analysis.py" ]]; then
    echo "❌ Please run this script from the vision_bridge directory"
    echo "Usage: cd /home/hafnium/aloha-lite/vision_bridge && ./quick_setup_sam2.sh"
    exit 1
fi

# Run the setup script with large model
echo "📥 Starting SAM 2 setup..."
python setup_sam2.py large

# Check if setup was successful
if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Activate SAM 2 environment:"
    echo "   source ./sam2_setup/setup_sam2_environment.sh"
    echo ""
    echo "2. Test the installation:"
    echo "   python ./sam2_setup/test_vision_bridge_sam2.py"
    echo ""
    echo "3. Test with vision_bridge:"
    echo "   python beaker_analysis.py"
    echo ""
    echo "The vision_bridge will now automatically use SAM 2 for enhanced beaker detection!"
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    echo "You can try:"
    echo "- Check internet connection"
    echo "- Try a smaller model: python setup_sam2.py small"
    echo "- Check available disk space (large model needs ~900MB)"
fi
