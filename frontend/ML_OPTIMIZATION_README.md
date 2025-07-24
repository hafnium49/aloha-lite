# ML-Enhanced Color Optimization Frontend

An intelligent color mixing system that uses machine learning (Bayesian optimization) to automatically recommend optimal color ratios for achieving target colors.

## 🎯 System Overview

This enhanced frontend implements a complete machine learning workflow for color optimization:

### Step-by-Step Process

1. **Target Color Generation** - System generates a random target color and displays it
2. **User Input** - User specifies initial color ratios and executes mixing
3. **Robot Execution** - Robot mixes colors, measures the result, and sends data back
4. **ML Analysis** - System analyzes the measurement vs target and updates ML model
5. **Smart Recommendations** - ML algorithm recommends improved ratios for next attempt
6. **Iterative Optimization** - Process repeats with increasingly better recommendations

## 🧠 ML Algorithm Details

### Bayesian Optimization
- Uses Gaussian Process Regression to model the color mixing function
- Expected Improvement acquisition function for exploration/exploitation balance
- Handles noisy measurements and uncertainty quantification
- Adapts to user's specific mixing environment and equipment

### Fallback Systems
- **Heuristic Mode**: When ML libraries unavailable, uses intelligent rule-based recommendations
- **Initial Guesses**: Smart starting points based on target color analysis
- **Robust Handling**: Graceful degradation when measurements are missing

## 🚀 Quick Start

### Installation
```bash
cd frontend
./start_ml_frontend.sh
```

### Manual Setup
```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Dependencies
- **Core**: FastAPI, uvicorn, httpx
- **ML**: scipy, scikit-learn, numpy
- **Optional**: All ML libraries are optional - system works without them

## 🎨 Frontend Features

### Target Color System
- Random target color generation with achievable RGB values
- Visual target display with RGB and hex values
- Manual target color setting capability

### ML Recommendations
- Real-time ratio recommendations based on previous attempts
- Confidence indicators and prediction uncertainty
- Apply recommendations with one click

### Optimization Statistics
- Success rate tracking and improvement trends
- Distance-to-target measurements over time
- Visual charts showing optimization progress
- Historical attempt analysis

### Integration
- Seamless integration with existing robot control system
- Automatic measurement data collection from beaker analysis
- Maintains all existing color mixing and analysis functionality

## 📊 API Endpoints

### ML Optimization Endpoints
- `GET /api/target-color` - Generate new random target color
- `POST /api/target-color` - Set specific target color
- `POST /api/recommend-ratios` - Get ML-based recommendations
- `GET /api/optimization-history` - View complete optimization history
- `POST /api/reset-optimization` - Reset ML model and history

### Existing Proxy Endpoints
- `/robot/*` - Proxy to robot service (port 8000)
- `/vision/*` - Proxy to vision bridge (port 5000)
- `/health` - System health check with ML status

## 🔧 Configuration

### Environment Variables
```bash
ROBOT_SERVICE_URL=http://localhost:8000  # Robot service endpoint
VISION_SERVICE_URL=http://localhost:5000  # Vision bridge endpoint
```

### ML Parameters
The system automatically tunes most parameters, but key settings include:
- **Exploration Factor**: 0.3 (30% exploration vs exploitation)
- **Initial Guess Strategy**: Color-space mapping with mixing rules
- **Optimization Bounds**: 0.1 to 5.0 for each color ratio
- **Kernel**: RBF + Constant for Gaussian Process

## 🎯 Usage Workflow

### First Session
1. Open http://localhost:3000
2. System displays random target color
3. Enter initial color ratios or click "推奨比率を取得" for ML suggestion
4. Click "混合を調剤してスナップ撮影" to execute
5. System measures result and automatically updates ML model
6. View updated recommendations for next attempt

### Ongoing Optimization
1. Apply recommended ratios or modify them
2. Execute mixing and measurement
3. System learns from each attempt
4. Recommendations become increasingly accurate
5. Monitor improvement trends in statistics panel

### Advanced Features
- **History Analysis**: View all previous attempts and their outcomes
- **Model Reset**: Start fresh optimization for new target colors
- **Manual Targets**: Set specific RGB targets for custom experiments
- **Performance Metrics**: Track optimization efficiency over time

## 🧪 Technical Details

### Color Distance Calculation
Uses Euclidean distance in RGB space: `sqrt((r1-r2)² + (g1-g2)² + (b1-b2)²)`

### Ratio Normalization
Ratios are normalized to sum to 3.0 for practical mixing volumes while maintaining proportions.

### Gaussian Process Model
- **Kernel**: `ConstantKernel(1.0) * RBF(length_scale=1.0)`
- **Alpha**: 1e-6 for numerical stability
- **Normalization**: Y-values normalized for better model performance

### Acquisition Function
Expected Improvement with exploration parameter ξ=0.01:
```
EI(x) = (f_best - μ(x) - ξ) * Φ(Z) + σ(x) * φ(Z)
```
where Z = (f_best - μ(x) - ξ) / σ(x)

## 🛠️ Troubleshooting

### ML Libraries Not Available
System falls back to heuristic optimization. Install with:
```bash
pip install scipy scikit-learn numpy
```

### Robot Service Connection Issues
Check that robot service is running on port 8000:
```bash
curl http://localhost:8000/health
```

### Vision Service Problems
Verify vision bridge is accessible on port 5000:
```bash
curl http://localhost:5000/health
```

### No Beaker Analysis Results
ML optimization requires color measurements. Ensure:
- Camera is working and configured
- Vision bridge is processing images correctly
- Beaker analysis is enabled in robot sequences

## 📈 Performance Tips

### Faster Convergence
- Start with reasonable initial guesses
- Use consistent lighting conditions
- Ensure accurate color measurements
- Allow system to learn from 3-5 attempts before expecting optimal results

### Best Practices
- Generate new targets periodically to test generalization
- Monitor improvement trends to validate ML performance
- Reset optimization when switching to very different target colors
- Use manual targets to test specific color mixing challenges

## 🔮 Future Enhancements

Potential improvements for the ML system:
- Multi-objective optimization (color + transparency + viscosity)
- Advanced color spaces (LAB, HSV) for perceptually-uniform distances
- Active learning strategies for more efficient data collection
- Transfer learning between different target colors
- Ensemble methods for robust predictions
