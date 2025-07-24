#!/bin/bash
"""
ML-Enhanced Frontend Startup Script
Installs dependencies and starts the color optimization frontend server
"""

set -e

echo "🎨 Starting ML-Enhanced Color Optimization Frontend"
echo "=============================================="

# Change to frontend directory
cd "$(dirname "$0")"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check ML availability
echo "🧠 Checking ML libraries..."
python3 -c "
try:
    import scipy, sklearn, numpy
    print('✅ All ML libraries available - Bayesian optimization enabled')
except ImportError as e:
    print(f'⚠️ ML libraries missing: {e}')
    print('💡 Run: pip install scipy scikit-learn numpy')
"

# Start the server
echo "🚀 Starting ML-enhanced frontend server on port 3000..."
echo "🎯 Features enabled:"
echo "   - Target color generation"
echo "   - Bayesian optimization recommendations"
echo "   - Color mixing history tracking"
echo "   - Real-time optimization statistics"
echo ""
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🔗 API endpoints:"
echo "   - GET  /api/target-color (generate target)"
echo "   - POST /api/recommend-ratios (get ML recommendations)"
echo "   - GET  /api/optimization-history (view history)"
echo ""

python3 main.py
