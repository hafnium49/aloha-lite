#!/usr/bin/env python3
"""
Frontend FastAPI Server with ML-based Color Optimization

A FastAPI server that serves the frontend HTML interface, acts as a proxy 
to the robot service and vision bridge, and provides ML-powered color 
optimization using Bayesian optimization for color mixing recommendations.
"""

import os
import json
import random
import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

# Machine Learning imports
try:
    from scipy.optimize import minimize
    from scipy.spatial.distance import euclidean
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    from scipy.stats import norm
    ML_AVAILABLE = True
except ImportError:
    print("⚠️  ML libraries not available. Install with: pip install scipy scikit-learn")
    ML_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ROBOT_SERVICE_URL = os.getenv("ROBOT_SERVICE_URL", "http://localhost:8000")
VISION_SERVICE_URL = os.getenv("VISION_SERVICE_URL", "http://localhost:5000")

class ColorOptimizer:
    """Bayesian optimization-based color mixing optimizer"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.target_color: Optional[Tuple[int, int, int]] = None
        self.gp_model = None
        self.kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) if ML_AVAILABLE else None
        
    def set_target_color(self, rgb: Tuple[int, int, int]):
        """Set the target color for optimization"""
        self.target_color = rgb
        logger.info(f"🎯 Target color set to RGB{rgb}")
        
    def add_measurement(self, ratios: Dict[str, float], measured_rgb: Tuple[int, int, int]):
        """Add a measurement to the history"""
        distance = self._calculate_color_distance(measured_rgb, self.target_color) if self.target_color else 0
        
        measurement = {
            'timestamp': datetime.now().isoformat(),
            'ratios': ratios.copy(),
            'measured_rgb': measured_rgb,
            'distance_to_target': distance
        }
        self.history.append(measurement)
        
        # Enhanced logging with optimization insights
        improvement_msg = ""
        if len(self.history) > 1:
            prev_distance = self.history[-2]['distance_to_target']
            improvement = prev_distance - distance
            improvement_pct = (improvement / prev_distance) * 100 if prev_distance > 0 else 0
            improvement_msg = f", improvement: {improvement:+.2f} ({improvement_pct:+.1f}%)"
            
            # Track if we found a new best
            best_so_far = min(h['distance_to_target'] for h in self.history[:-1])
            if distance < best_so_far:
                improvement_msg += " 🎯 NEW BEST!"
        
        logger.info(f"📊 Added measurement: ratios={ratios}, RGB={measured_rgb}, distance={distance:.2f}{improvement_msg}")
        
        # Log optimization status every few measurements
        if len(self.history) % 3 == 0:
            stats = self.get_statistics()
            logger.info(f"🔍 Optimization status: {stats['convergence_status']}, diversity: {stats['ratio_diversity']:.3f}, efficiency: {stats['optimization_efficiency']:.1%}")
        
    def _calculate_color_distance(self, rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
        """Calculate Euclidean distance between two RGB colors"""
        return euclidean(rgb1, rgb2)
        
    def _ratios_to_array(self, ratios: Dict[str, float]) -> np.ndarray:
        """Convert ratio dict to numpy array [red, yellow, blue]"""
        return np.array([ratios.get('red', 0), ratios.get('yellow', 0), ratios.get('blue', 0)])
        
    def _array_to_ratios(self, arr: np.ndarray) -> Dict[str, float]:
        """Convert numpy array to ratio dict"""
        return {'red': float(arr[0]), 'yellow': float(arr[1]), 'blue': float(arr[2])}
        
    def _normalize_ratios(self, ratios: Dict[str, float]) -> Dict[str, float]:
        """Normalize ratios to sum to a reasonable total (3.0 for balanced mixing)"""
        total = sum(ratios.values())
        if total == 0:
            return {'red': 1.0, 'yellow': 1.0, 'blue': 1.0}
        
        # Scale to sum to 3.0 for reasonable mixing ratios
        scale_factor = 3.0 / total
        return {
            'red': ratios['red'] * scale_factor,
            'yellow': ratios['yellow'] * scale_factor,
            'blue': ratios['blue'] * scale_factor
        }
        
    def recommend_next_ratios(self) -> Dict[str, float]:
        """Use Bayesian optimization to recommend next color ratios"""
        if not self.target_color:
            logger.warning("⚠️  No target color set, using random ratios")
            return self._get_random_ratios()
            
        if len(self.history) == 0:
            logger.info("📝 No history available, using smart initial guess")
            return self._get_initial_guess()
            
        # Check if optimization appears stuck (recommending very similar ratios)
        if len(self.history) >= 3 and self._is_optimization_stuck():
            logger.info("🔄 Optimization appears stuck, injecting exploration")
            return self._inject_exploration()
            
        if not ML_AVAILABLE:
            logger.warning("⚠️  ML not available, using heuristic approach")
            return self._enhanced_heuristic_recommendation()
            
        try:
            return self._bayesian_optimization()
        except Exception as e:
            logger.error(f"❌ Bayesian optimization failed: {e}")
            return self._enhanced_heuristic_recommendation()
            
    def _is_optimization_stuck(self) -> bool:
        """Check if recent recommendations are too similar (indicating convergence/stagnation)"""
        if len(self.history) < 3:
            return False
            
        # Check last 3 recommendations for similarity
        recent_ratios = [h['ratios'] for h in self.history[-3:]]
        
        # Calculate variance in ratios
        for color in ['red', 'yellow', 'blue']:
            values = [r[color] for r in recent_ratios]
            variance = np.var(values) if ML_AVAILABLE else sum((x - sum(values)/len(values))**2 for x in values) / len(values)
            if variance > 0.01:  # If any color has significant variance, not stuck
                return False
                
        # Also check if distances aren't improving
        recent_distances = [h['distance_to_target'] for h in self.history[-3:]]
        improvement = max(recent_distances) - min(recent_distances)
        relative_improvement = improvement / (max(recent_distances) + 1e-6)
        
        is_stuck = relative_improvement < 0.05  # Less than 5% improvement range
        if is_stuck:
            logger.info(f"🚫 Optimization stuck: ratio_variance_low=True, improvement={relative_improvement:.3f}")
        
        return is_stuck
        
    def _inject_exploration(self) -> Dict[str, float]:
        """Inject exploration when optimization is stuck"""
        # Get the best point so far
        best_measurement = min(self.history, key=lambda x: x['distance_to_target'])
        best_ratios = best_measurement['ratios'].copy()
        
        # Apply large perturbation to break out of local optimum
        exploration_strength = 0.8  # Large perturbation
        
        # Choose random exploration strategy
        strategy = random.choice(['random_walk', 'opposite_direction', 'dimension_focus'])
        
        if strategy == 'random_walk':
            # Random walk from best point
            for color in ['red', 'yellow', 'blue']:
                perturbation = random.uniform(-exploration_strength, exploration_strength)
                best_ratios[color] = max(0.1, best_ratios[color] * (1 + perturbation))
                
        elif strategy == 'opposite_direction':
            # Try opposite direction from recent trend
            if len(self.history) >= 2:
                prev_ratios = self.history[-2]['ratios']
                for color in ['red', 'yellow', 'blue']:
                    trend = best_ratios[color] - prev_ratios[color]
                    # Go opposite direction with amplification
                    best_ratios[color] = max(0.1, best_ratios[color] - 2 * trend)
                    
        else:  # dimension_focus
            # Focus exploration on one dimension
            focus_color = random.choice(['red', 'yellow', 'blue'])
            for color in ['red', 'yellow', 'blue']:
                if color == focus_color:
                    # Large change in focus dimension
                    best_ratios[color] *= random.uniform(0.3, 3.0)
                else:
                    # Small changes in other dimensions
                    best_ratios[color] *= random.uniform(0.8, 1.2)
                best_ratios[color] = max(0.1, best_ratios[color])
        
        logger.info(f"🚀 Injecting exploration (strategy={strategy}): {best_ratios}")
        return self._normalize_ratios(best_ratios)
            
    def _get_random_ratios(self) -> Dict[str, float]:
        """Generate random ratios for initial exploration"""
        ratios = {
            'red': random.uniform(0.1, 3.0),
            'yellow': random.uniform(0.1, 3.0),
            'blue': random.uniform(0.1, 3.0)
        }
        return self._normalize_ratios(ratios)
        
    def _get_initial_guess(self) -> Dict[str, float]:
        """Generate intelligent initial guess based on target color"""
        if not self.target_color:
            return self._get_random_ratios()
            
        r, g, b = self.target_color
        
        # Simple color-to-ratio mapping heuristic
        # This is a rough approximation of how RGB maps to pigment mixing
        red_ratio = max(0.1, (r / 255.0) * 2.0)
        yellow_ratio = max(0.1, (g / 255.0) * 2.0)
        blue_ratio = max(0.1, (b / 255.0) * 2.0)
        
        # Adjust for common color mixing rules
        if r > g and r > b:  # Red dominant
            red_ratio *= 1.5
        elif g > r and g > b:  # Green/Yellow dominant
            yellow_ratio *= 1.5
            red_ratio *= 0.8  # Red + Yellow = Orange/Green
        elif b > r and b > g:  # Blue dominant
            blue_ratio *= 1.5
            
        ratios = {'red': red_ratio, 'yellow': yellow_ratio, 'blue': blue_ratio}
        return self._normalize_ratios(ratios)
        
    def _heuristic_recommendation(self) -> Dict[str, float]:
        """Heuristic-based recommendation when ML is not available"""
        if len(self.history) == 0:
            return self._get_initial_guess()
            
        # Find the best previous result
        best_measurement = min(self.history, key=lambda x: x['distance_to_target'])
        best_ratios = best_measurement['ratios'].copy()
        
        # Add some exploration around the best result
        exploration_factor = 0.3
        for color in ['red', 'yellow', 'blue']:
            perturbation = random.uniform(-exploration_factor, exploration_factor)
            best_ratios[color] = max(0.1, best_ratios[color] * (1 + perturbation))
            
        return self._normalize_ratios(best_ratios)
        
    def _bayesian_optimization(self) -> Dict[str, float]:
        """Bayesian optimization using Gaussian Process"""
        if len(self.history) < 2:
            return self._get_initial_guess()
            
        # Prepare training data
        X = np.array([self._ratios_to_array(h['ratios']) for h in self.history])
        y = np.array([h['distance_to_target'] for h in self.history])
        
        # Add noise to avoid numerical issues with identical points
        X_noise = X + np.random.normal(0, 1e-6, X.shape)
        
        # Train Gaussian Process with better hyperparameters
        kernel = ConstantKernel(1.0, constant_value_bounds=(1e-3, 1e3)) * RBF(
            length_scale=1.0, length_scale_bounds=(1e-2, 1e2)
        )
        self.gp_model = GaussianProcessRegressor(
            kernel=kernel, 
            alpha=1e-4,  # Increased noise parameter
            normalize_y=True,
            n_restarts_optimizer=5  # Better hyperparameter optimization
        )
        self.gp_model.fit(X_noise, y)
        
        # Current best (minimum distance)
        f_best = np.min(y)
        
        # Enhanced acquisition function with adaptive exploration
        def acquisition_function(x):
            x = x.reshape(1, -1)
            mu, sigma = self.gp_model.predict(x, return_std=True)
            
            # Adaptive exploration parameter based on optimization progress
            # Start with high exploration, reduce as we get better results
            base_xi = 0.1  # Increased from 0.01
            progress_factor = max(0.01, f_best / (np.max(y) + 1e-6))  # How much improvement we've made
            xi = base_xi * (1 + progress_factor)  # More exploration when progress is slow
            
            # Expected Improvement with enhanced exploration
            improvement = f_best - mu - xi
            Z = improvement / (sigma + 1e-9)
            
            ei = improvement * norm.cdf(Z) + sigma * norm.pdf(Z)
            
            # Add pure exploration term to encourage diversity
            exploration_bonus = 0.1 * sigma  # Bonus for high uncertainty areas
            
            return -(ei[0] + exploration_bonus)  # Minimize negative EI + exploration
            
        # Enhanced optimization with more comprehensive search
        best_x = None
        best_ei = float('inf')
        
        # Multiple optimization strategies
        
        # Strategy 1: Random starts with wider bounds
        for _ in range(20):  # Increased from 10
            x0 = np.random.uniform(0.05, 8.0, 3)  # Wider search space
            
            result = minimize(
                acquisition_function,
                x0,
                method='L-BFGS-B',
                bounds=[(0.05, 8.0), (0.05, 8.0), (0.05, 8.0)]  # Wider bounds
            )
            
            if result.success and result.fun < best_ei:
                best_ei = result.fun
                best_x = result.x
                
        # Strategy 2: Grid-based initialization for better coverage
        grid_points = np.linspace(0.1, 5.0, 5)
        for r in grid_points[::2]:  # Sparse grid to avoid too many evaluations
            for y in grid_points[::2]:
                for b in grid_points[::2]:
                    x0 = np.array([r, y, b])
                    
                    result = minimize(
                        acquisition_function,
                        x0,
                        method='L-BFGS-B',
                        bounds=[(0.05, 8.0), (0.05, 8.0), (0.05, 8.0)]
                    )
                    
                    if result.success and result.fun < best_ei:
                        best_ei = result.fun
                        best_x = result.x
        
        # Strategy 3: Explore around previous best points
        if len(self.history) >= 3:
            # Get top 3 best points
            sorted_history = sorted(self.history, key=lambda x: x['distance_to_target'])[:3]
            for measurement in sorted_history:
                base_ratios = self._ratios_to_array(measurement['ratios'])
                
                # Try variations around best points
                for _ in range(3):
                    perturbation = np.random.normal(0, 0.5, 3)  # Larger perturbation
                    x0 = np.clip(base_ratios + perturbation, 0.05, 8.0)
                    
                    result = minimize(
                        acquisition_function,
                        x0,
                        method='L-BFGS-B',
                        bounds=[(0.05, 8.0), (0.05, 8.0), (0.05, 8.0)]
                    )
                    
                    if result.success and result.fun < best_ei:
                        best_ei = result.fun
                        best_x = result.x
                
        if best_x is not None:
            recommended_ratios = self._array_to_ratios(best_x)
            normalized_ratios = self._normalize_ratios(recommended_ratios)
            
            logger.info(f"🔍 Bayesian optimization: raw={recommended_ratios}, normalized={normalized_ratios}")
            logger.info(f"🔍 Acquisition value: {best_ei:.6f}, Current best distance: {f_best:.2f}")
            
            return normalized_ratios
        else:
            logger.warning("⚠️  All optimization attempts failed, using enhanced heuristic fallback")
            return self._enhanced_heuristic_recommendation()
            
    def _enhanced_heuristic_recommendation(self) -> Dict[str, float]:
        """Enhanced heuristic recommendation with better exploration"""
        if len(self.history) == 0:
            return self._get_initial_guess()
            
        # Find the best few results, not just the single best
        sorted_history = sorted(self.history, key=lambda x: x['distance_to_target'])
        
        if len(sorted_history) >= 3:
            # Weighted combination of top 3 results
            weights = [0.5, 0.3, 0.2]  # Higher weight for better results
            combined_ratios = {'red': 0, 'yellow': 0, 'blue': 0}
            
            for i, measurement in enumerate(sorted_history[:3]):
                for color in ['red', 'yellow', 'blue']:
                    combined_ratios[color] += weights[i] * measurement['ratios'][color]
        else:
            # Use best result as base
            combined_ratios = sorted_history[0]['ratios'].copy()
        
        # Add adaptive exploration based on convergence
        recent_distances = [h['distance_to_target'] for h in self.history[-5:]]
        if len(recent_distances) >= 3:
            improvement_rate = (max(recent_distances) - min(recent_distances)) / max(1, max(recent_distances))
            exploration_factor = max(0.1, 0.8 * (1 - improvement_rate))  # More exploration if not improving
        else:
            exploration_factor = 0.4
        
        # Apply exploration with bias toward promising directions
        for color in ['red', 'yellow', 'blue']:
            # Random perturbation with exploration factor
            perturbation = random.uniform(-exploration_factor, exploration_factor)
            combined_ratios[color] = max(0.1, combined_ratios[color] * (1 + perturbation))
            
        logger.info(f"🎲 Enhanced heuristic: exploration_factor={exploration_factor:.2f}")
        return self._normalize_ratios(combined_ratios)
            
    def get_statistics(self) -> Dict:
        """Get optimization statistics"""
        if len(self.history) == 0:
            return {
                'total_attempts': 0,
                'best_distance': None,
                'average_distance': None,
                'improvement_trend': [],
                'convergence_status': 'no_data'
            }
            
        distances = [h['distance_to_target'] for h in self.history]
        
        # Calculate convergence metrics
        convergence_status = 'exploring'
        if len(distances) >= 5:
            recent_improvement = (max(distances[-5:]) - min(distances[-5:])) / (max(distances[-5:]) + 1e-6)
            if recent_improvement < 0.05:
                convergence_status = 'converged' if self._is_optimization_stuck() else 'converging'
            elif len(distances) >= 10:
                overall_improvement = (max(distances[:5]) - min(distances[-5:])) / (max(distances[:5]) + 1e-6)
                if overall_improvement > 0.3:
                    convergence_status = 'improving'
        
        # Calculate ratio diversity (how much we're exploring)
        ratio_diversity = 0.0
        if len(self.history) >= 2:
            recent_ratios = [h['ratios'] for h in self.history[-5:]] if len(self.history) >= 5 else [h['ratios'] for h in self.history]
            color_variances = []
            for color in ['red', 'yellow', 'blue']:
                values = [r[color] for r in recent_ratios]
                if ML_AVAILABLE:
                    variance = np.var(values)
                else:
                    mean_val = sum(values) / len(values)
                    variance = sum((x - mean_val)**2 for x in values) / len(values)
                color_variances.append(variance)
            ratio_diversity = sum(color_variances) / len(color_variances)
        
        return {
            'total_attempts': len(self.history),
            'best_distance': min(distances),
            'average_distance': np.mean(distances) if ML_AVAILABLE else sum(distances) / len(distances),
            'current_distance': distances[-1],
            'improvement_trend': distances,
            'target_rgb': self.target_color,
            'convergence_status': convergence_status,
            'ratio_diversity': ratio_diversity,
            'recent_improvement': (distances[0] - distances[-1]) / (distances[0] + 1e-6) if len(distances) > 1 else 0,
            'optimization_efficiency': len([d for d in distances if d < distances[0] * 0.8]) / len(distances) if len(distances) > 1 else 0
        }

def generate_random_target_color() -> Tuple[int, int, int]:
    """Generate a random target color that's achievable with RGB pigments"""
    # Generate colors that are more likely to be achievable with pigment mixing
    color_profiles = [
        # Red-based colors
        (random.randint(150, 255), random.randint(0, 100), random.randint(0, 100)),
        # Yellow-based colors  
        (random.randint(200, 255), random.randint(200, 255), random.randint(0, 50)),
        # Blue-based colors
        (random.randint(0, 100), random.randint(0, 100), random.randint(150, 255)),
        # Purple colors (red + blue)
        (random.randint(100, 200), random.randint(0, 100), random.randint(100, 200)),
        # Orange colors (red + yellow)
        (random.randint(200, 255), random.randint(100, 200), random.randint(0, 50)),
        # Green colors (yellow + blue)
        (random.randint(0, 100), random.randint(150, 255), random.randint(50, 150)),
    ]
    
    return random.choice(color_profiles)

# Global optimizer instance
color_optimizer = ColorOptimizer()

app = FastAPI(
    title="Aloha Lite Frontend",
    description="Web interface for robot control and beaker analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend HTML file."""
    try:
        with open("/home/hafnium/aloha-lite/frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend HTML file not found")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "frontend",
        "robot_service": ROBOT_SERVICE_URL,
        "vision_service": VISION_SERVICE_URL,
        "ml_available": ML_AVAILABLE
    }

@app.get("/api/target-color")
async def get_target_color():
    """Generate new random target color"""
    rgb = generate_random_target_color()
    color_optimizer.set_target_color(rgb)
    
    return {
        'status': 'success',
        'target_rgb': rgb,
        'target_hex': f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    }

@app.post("/api/target-color")
async def set_target_color(request: Request):
    """Set specific target color"""
    data = await request.json()
    rgb = tuple(data.get('rgb', [255, 0, 0]))
    color_optimizer.set_target_color(rgb)
    
    return {
        'status': 'success',
        'target_rgb': rgb,
        'target_hex': f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    }

@app.post("/api/recommend-ratios")
async def recommend_ratios(request: Request):
    """Get ML-based color ratio recommendations"""
    try:
        data = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        
        # If measurement data is provided, add it to history
        if 'measured_rgb' in data and 'ratios' in data:
            measured_rgb = tuple(data['measured_rgb'])
            ratios = data['ratios']
            color_optimizer.add_measurement(ratios, measured_rgb)
        
        # Get recommendation
        recommended_ratios = color_optimizer.recommend_next_ratios()
        stats = color_optimizer.get_statistics()
        
        return {
            'status': 'success',
            'recommended_ratios': recommended_ratios,
            'statistics': stats,
            'ml_available': ML_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.get("/api/optimization-history")
async def optimization_history():
    """Get the full optimization history"""
    return {
        'status': 'success',
        'history': color_optimizer.history,
        'statistics': color_optimizer.get_statistics()
    }

@app.post("/api/reset-optimization")
async def reset_optimization():
    """Reset the optimization history"""
    color_optimizer.history.clear()
    color_optimizer.gp_model = None
    
    return {
        'status': 'success',
        'message': 'Optimization history reset'
    }

@app.api_route("/robot/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_robot_service(request: Request, path: str):
    """Proxy requests to the robot service."""
    url = f"{ROBOT_SERVICE_URL}/robot/{path}"
    logger.info(f"Proxying {request.method} request to: {url}")
    
    # Forward query parameters
    if request.query_params:
        url += "?" + str(request.query_params)
    
    # Use longer timeout for robot operations (6+ minutes for laboratory procedures)
    async with httpx.AsyncClient(timeout=1000.0) as client:
        try:
            # Get request body if present
            body = await request.body() if request.method in ["POST", "PUT"] else None
            if body:
                logger.info(f"Request body: {body.decode()}")
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=body
            )
            
            logger.info(f"Robot service response status: {response.status_code}")
            logger.info(f"Robot service response headers: {dict(response.headers)}")
            
            # Return the response properly
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    response_json = response.json()
                    logger.info(f"Robot service response JSON: {response_json}")
                    return response_json
                else:
                    response_text = response.text
                    logger.info(f"Robot service response text: {response_text}")
                    return response_text
            except Exception as parse_error:
                logger.error(f"Error parsing response: {parse_error}")
                # Try to get raw response content
                try:
                    raw_content = response.content.decode()
                    logger.error(f"Raw response content: {raw_content}")
                    return {"error": "Response parsing failed", "raw_status": response.status_code, "raw_content": raw_content}
                except:
                    return {"error": "Response parsing failed", "raw_status": response.status_code}
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Robot service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Robot service unavailable")
        except Exception as e:
            logger.error(f"Robot service proxy error: {e}")
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# Proxy endpoints for vision service
@app.api_route("/vision/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_vision_service(request: Request, path: str):
    """Proxy requests to the vision service."""
    url = f"{VISION_SERVICE_URL}/{path}"
    
    # Forward query parameters
    if request.query_params:
        url += "?" + str(request.query_params)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Handle multipart form data (for image uploads)
            if request.headers.get("content-type", "").startswith("multipart/form-data"):
                form = await request.form()
                files = {}
                data = {}
                
                for key, value in form.items():
                    if hasattr(value, 'read'):  # File upload
                        files[key] = (value.filename, await value.read(), value.content_type)
                    else:  # Regular form field
                        data[key] = value
                
                response = await client.request(
                    method=request.method,
                    url=url,
                    files=files,
                    data=data
                )
            else:
                # Get request body if present
                body = await request.body() if request.method in ["POST", "PUT"] else None
                
                # Forward the request
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=dict(request.headers),
                    content=body
                )
            
            # Return the response properly
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Vision service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Vision service unavailable")
        except Exception as e:
            logger.error(f"Vision service proxy error: {e}")
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

@app.get("/status")
async def system_status():
    """Check the status of all backend services."""
    status = {
        "frontend": "healthy",
        "services": {}
    }
    
    # Check robot service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ROBOT_SERVICE_URL}/health")
            status["services"]["robot"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        status["services"]["robot"] = "unavailable"
    
    # Check vision service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{VISION_SERVICE_URL}/health")
            status["services"]["vision"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        status["services"]["vision"] = "unavailable"
    
    return status

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🎨 Starting Color Optimization Frontend Server")
    logger.info(f"🤖 Robot Service: {ROBOT_SERVICE_URL}")
    logger.info(f"👁️  Vision Service: {VISION_SERVICE_URL}")
    logger.info(f"🧠 ML Available: {ML_AVAILABLE}")
    
    if not ML_AVAILABLE:
        logger.warning("💡 To enable ML features, install: pip install scipy scikit-learn")
    
    # Generate initial target color
    initial_target = generate_random_target_color()
    color_optimizer.set_target_color(initial_target)
    logger.info(f"🎯 Initial target color: RGB{initial_target}")
    
    uvicorn.run(app, host="0.0.0.0", port=3000)
