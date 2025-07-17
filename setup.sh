#!/bin/bash
# ALOHA-Lite Setup Script
# =======================
# This script installs all dependencies for the ALOHA-Lite robot control system

set -e  # Exit on any error

echo "🚀 ALOHA-Lite Setup Script"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "execute_rules.py" ]; then
    echo "❌ Error: Please run this script from the aloha-lite root directory"
    exit 1
fi

echo "📦 Installing Python dependencies from PyPI..."

# Install all requirements from PyPI (includes modern_robotics)
pip install -r requirements.txt

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 You can now use the trajectory planner:"
echo "   python3 trajectory_example.py"
echo "   python3 trajectory_executor.py --help"
echo ""
echo "🤖 To control robots:"
echo "   python3 execute_rules.py --config your_config_name"
echo "   python3 trajectory_executor.py --config your_config_name"
