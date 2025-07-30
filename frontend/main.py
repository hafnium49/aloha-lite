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
    from scipy.optimize import minimize, lsq_linear
    from scipy.spatial.distance import euclidean
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    from scipy.stats import norm
    ML_AVAILABLE = True
except ImportError:
    print("⚠️  ML libraries not available. Install with: pip install scipy scikit-learn")
    ML_AVAILABLE = False

# Color Science imports for perceptually uniform plotting
try:
    import colour
    COLOR_SCIENCE_AVAILABLE = True
    print("✅ Color science library available for CAM02-UCS plotting")
except ImportError:
    COLOR_SCIENCE_AVAILABLE = False
    print("⚠️  Color science library not available. Install with: pip install colour-science")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ROBOT_SERVICE_URL = os.getenv("ROBOT_SERVICE_URL", "http://localhost:8000")
VISION_SERVICE_URL = os.getenv("VISION_SERVICE_URL", "http://localhost:5000")

class ColorOptimizer:
    """
    Phase schedule  (N = len(history) BEFORE recommending the next mix)

      N = 0 : pure dominant-channel squirt               (baseline)
      N = 1 : Bayesian GP only                           (black-box)
      N = 2 : rough 3-scalar calibration  ⊕  GP          (60 % cal / 40 % GP)
      3 ≤ N ≤ 7 :   full 9-parameter NNLS calibration  ⊕  GP
                   – weight on calibration rises linearly
                   – GP weight falls to zero by N = 8
      N ≥ 8 : deterministic NNLS calibration ONLY
               – σ_resid (standard error) calculated on every call
    """

    # ───────────── initialisation ─────────────
    def __init__(self):
        self.history: List[Dict] = []
        self.target_color: Optional[Tuple[int, int, int]] = None
        self.P_est: Optional[np.ndarray] = None   # (3,3) absorbance matrix
        self.std_error: Optional[float] = None
        self.gp_model: Optional[GaussianProcessRegressor] = None
        self.epsilon_rgb = 10.0                   # not used until N ≥ 8

    # ───────────── low-level helpers ──────────
    @staticmethod
    def _lin_rgb(rgb):  # sRGB→linear
        x = np.asarray(rgb)/255.0
        return np.power(x, 2.2).clip(1e-4, 1)

    @classmethod
    def _rgb_to_absorb(cls, rgb):
        return -np.log10(cls._lin_rgb(rgb))

    def _ratios_to_array(self, r):  # dict→np[3]
        return np.array([r.get('red',0), r.get('yellow',0), r.get('blue',0)])

    def _array_to_ratios(self, a):
        return {'red':float(a[0]), 'yellow':float(a[1]), 'blue':float(a[2])}

    def _normalize(self, d):
        s = sum(d.values()) or 1.0
        f = 3.0/s
        return {k:max(0.1, v*f) for k,v in d.items()}

    # ───────────── public API ────────────────
    def set_target_color(self, rgb):
        self.target_color = rgb
        logger.info(f"🎯 target RGB{rgb}")

    def add_measurement(self, ratios, measured_rgb):
        d = euclidean(measured_rgb, self.target_color) if self.target_color else 0
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "ratios": ratios.copy(),
            "measured_rgb": measured_rgb,
            "distance_to_target": d
        })
        logger.info("📊 logged #%d  Δ≈%.2f", len(self.history), d)

    # ───────────── calibration blocks ────────
    def _rough_scale_calibration(self):
        """Fit 3 scale factors α_r,y,b with fixed hue basis."""
        if len(self.history) < 2:
            return
        P_hue = np.array([[0.8,0.1,0.1],
                          [0.2,0.9,0.1],
                          [0.1,0.1,0.9]])
        W = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        A = np.stack([self._rgb_to_absorb(h['measured_rgb']) for h in self.history])
        L = np.einsum('nk,kj->nkj', W, P_hue).reshape(-1,3)
        alpha, *_ = np.linalg.lstsq(L, A.reshape(-1), rcond=None)
        self.P_est = np.diag(alpha.clip(1e-6)) @ P_hue
        logger.info("🔧 rough α = %s", alpha.round(3))

    def _fit_full_calibration(self):
        """Least-squares fit of full 3×3 pigment matrix; works for any N≥3."""
        if len(self.history) < 3 or not ML_AVAILABLE:
            return
        W = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        A = np.stack([self._rgb_to_absorb(h['measured_rgb']) for h in self.history])
        P = np.zeros((3,3))
        for ch in range(3):
            res = lsq_linear(W, A[:,ch], bounds=(0, np.inf))
            P[:,ch] = res.x
        self.P_est = P
        resid = A - W @ P
        self.std_error = float(np.sqrt(np.mean(resid**2)))
        logger.info("🧮 NNLS fit  σ_resid=%.4f", self.std_error)

    def _inverse_weights(self):
        if self.P_est is None or not ML_AVAILABLE:
            return None
        res = lsq_linear(self.P_est.T,
                         self._rgb_to_absorb(self.target_color),
                         bounds=(0,8))
        return self._normalize(self._array_to_ratios(res.x))

    # ───────────── Gaussian-process helper ───
    def _gp_next(self, seed=None):
        if not ML_AVAILABLE:
            return self._get_random()
        X = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        y = np.array([h['distance_to_target'] for h in self.history])
        X += np.random.normal(0,1e-6,X.shape)
        ker = ConstantKernel(1.0,(1e-3,1e3))*RBF(1.0,(1e-2,1e2))
        gp  = GaussianProcessRegressor(kernel=ker, alpha=1e-4,
                                       normalize_y=True, n_restarts_optimizer=3)
        gp.fit(X,y); self.gp_model = gp
        f_best = y.min()
        def acq(xx):
            m,s = gp.predict(xx.reshape(1,-1), return_std=True)
            xi  = 0.1; z = (f_best-m-xi)/(s+1e-9)
            return -(f_best-m-xi)*norm.cdf(z) - s*norm.pdf(z)
        starts = [np.random.uniform(0.1,5,(3,)) for _ in range(6)]
        if seed is not None:
            starts.append(self._ratios_to_array(seed))
        best_x,best_v = None,np.inf
        for s0 in starts:
            res = minimize(acq, s0, method='L-BFGS-B', bounds=[(0.05,8)]*3)
            if res.success and res.fun < best_v:
                best_v,best_x = res.fun,res.x
        return self._normalize(self._array_to_ratios(best_x if best_x is not None else starts[0]))

    # ───────────── boilerplate generators ────
    def _get_random(self):
        return self._normalize({c:random.uniform(0.1,3.0) for c in ('red','yellow','blue')})

    def _get_initial(self):
        r,g,b = self.target_color
        return self._normalize({'red':(r/255)*2+0.1,
                                'yellow':(g/255)*2+0.1,
                                'blue':(b/255)*2+0.1})

    # ───────────── main phase logic ──────────
    def recommend_next_ratios(self):
        N = len(self.history)

        # Phase 0
        if N == 0:
            r,g,b = self.target_color; dom = np.argmax([r,g,b])
            pure = np.zeros(3); pure[dom] = 3.0
            return self._array_to_ratios(pure)

        # Phase 1
        if N == 1:
            return self._gp_next()

        # Phase 2
        if N == 2:
            self._rough_scale_calibration()
            w_cal = self._inverse_weights()
            w_gp  = self._gp_next()
            if w_cal is None:
                return w_gp
            return self._normalize({c:0.6*w_cal[c]+0.4*w_gp[c] for c in w_cal})

        # Phase 3-7 : blended NNLS + GP
        if 3 <= N <= 7:
            self._fit_full_calibration()
            w_cal = self._inverse_weights()
            w_gp  = self._gp_next(seed=w_cal)
            if w_cal is None:
                return w_gp
            w_cal_weight = (N-1)/8.0          # 0.25 → 0.75 as N=3→7
            w_gp_weight  = 1.0 - w_cal_weight
            return self._normalize({c:w_cal_weight*w_cal[c]+w_gp_weight*w_gp[c]
                                    for c in w_cal})

        # Phase ≥8 : calibration only
        self._fit_full_calibration()
        res = self._inverse_weights()
        return res if res else self._get_random()

    # ───────────── quick stats for UI ────────
    def get_statistics(self):
        d = [h['distance_to_target'] for h in self.history]
        return {"total_attempts": len(self.history),
                "best_distance":  min(d) if d else None,
                "std_error_absorb": self.std_error,
                "current_distance": d[-1] if d else None,
                "average_distance": sum(d) / len(d) if d else None,
                "improvement_trend": d,
                "target_rgb": self.target_color,
                "convergence_status": "exploring",
                "ratio_diversity": 0.0,
                "recent_improvement": (d[0] - d[-1]) / (d[0] + 1e-6) if len(d) > 1 else 0,
                "optimization_efficiency": len([dist for dist in d if dist < d[0] * 0.8]) / len(d) if len(d) > 1 else 0}

    # ───────────── color space conversion helpers ────────
    @staticmethod
    def _rgb_to_cam02ucs(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert sRGB (0-255) to CAM02-UCS J' a' b' coordinates"""
        if not COLOR_SCIENCE_AVAILABLE:
            # Fallback to approximate CIELAB conversion
            return ColorOptimizer._rgb_to_lab(rgb)
        
        try:
            # Convert sRGB to XYZ
            rgb_norm = np.array(rgb) / 255.0
            xyz = colour.sRGB_to_XYZ(rgb_norm)
            
            # Convert XYZ to CAM02-UCS
            # Using standard viewing conditions (D65, 20% background, average surround)
            cam02ucs = colour.XYZ_to_CAM02UCS(xyz)
            
            return tuple(cam02ucs)
        except Exception as e:
            logger.warning(f"CAM02-UCS conversion failed: {e}, falling back to CIELAB")
            return ColorOptimizer._rgb_to_lab(rgb)
    
    @staticmethod
    def _rgb_to_lab(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert sRGB (0-255) to CIELAB L* a* b* coordinates"""
        if COLOR_SCIENCE_AVAILABLE:
            try:
                rgb_norm = np.array(rgb) / 255.0
                xyz = colour.sRGB_to_XYZ(rgb_norm)
                lab = colour.XYZ_to_Lab(xyz)
                return tuple(lab)
            except Exception as e:
                logger.warning(f"CIELAB conversion failed: {e}, using approximation")
        
        # Fallback approximation for CIELAB without colour-science
        r, g, b = np.array(rgb) / 255.0
        
        # Rough sRGB to XYZ approximation
        xyz = np.array([
            0.4124 * r + 0.3576 * g + 0.1805 * b,
            0.2126 * r + 0.7152 * g + 0.0722 * b,
            0.0193 * r + 0.1192 * g + 0.9505 * b
        ])
        
        # Rough XYZ to LAB approximation
        xyz = xyz / np.array([0.95047, 1.0, 1.08883])  # D65 reference white
        
        def f(t):
            return np.where(t > 0.008856, np.power(t, 1/3), (7.787 * t + 16/116))
        
        fx, fy, fz = f(xyz)
        
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        
        return (L, a, b)

    def get_color_space_data(self) -> Dict:
        """Get color space data for perceptual plotting"""
        if not self.target_color or len(self.history) == 0:
            return {
                'available': False,
                'color_space': 'CAM02-UCS' if COLOR_SCIENCE_AVAILABLE else 'CIELAB',
                'target': None,
                'trail': []
            }
        
        # Convert target color
        target_lab = self._rgb_to_cam02ucs(self.target_color)
        
        # Convert history
        trail_data = []
        for measurement in self.history:
            rgb = measurement['measured_rgb']
            lab = self._rgb_to_cam02ucs(rgb)
            trail_data.append({
                'lab': lab,
                'rgb': rgb,
                'ratios': measurement['ratios'],
                'distance': measurement['distance_to_target'],
                'timestamp': measurement['timestamp']
            })
        
        return {
            'available': True,
            'color_space': 'CAM02-UCS' if COLOR_SCIENCE_AVAILABLE else 'CIELAB',
            'target': {
                'lab': target_lab,
                'rgb': self.target_color
            },
            'trail': trail_data,
            'axis_labels': {
                'x': "a'" if COLOR_SCIENCE_AVAILABLE else 'a*',
                'y': "b'" if COLOR_SCIENCE_AVAILABLE else 'b*',
                'title': 'Color Optimization Progress in CAM02-UCS a′b′ plane' if COLOR_SCIENCE_AVAILABLE else 'Color Optimization Progress in CIELAB a*b* plane'
            }
        }

    def get_color_space_data(self) -> Dict:
        """Get color space data for perceptual plotting"""
        if not self.target_color or len(self.history) == 0:
            return {
                'available': False,
                'color_space': 'CAM02-UCS' if COLOR_SCIENCE_AVAILABLE else 'CIELAB',
                'target': None,
                'trail': []
            }
        
        # Convert target color
        target_lab = self._rgb_to_cam02ucs(self.target_color)
        
        # Convert history
        trail_data = []
        for measurement in self.history:
            rgb = measurement['measured_rgb']
            lab = self._rgb_to_cam02ucs(rgb)
            trail_data.append({
                'lab': lab,
                'rgb': rgb,
                'ratios': measurement['ratios'],
                'distance': measurement['distance_to_target'],
                'timestamp': measurement['timestamp']
            })
        
        return {
            'available': True,
            'color_space': 'CAM02-UCS' if COLOR_SCIENCE_AVAILABLE else 'CIELAB',
            'target': {
                'lab': target_lab,
                'rgb': self.target_color
            },
            'trail': trail_data,
            'axis_labels': {
                'x': "a'" if COLOR_SCIENCE_AVAILABLE else 'a*',
                'y': "b'" if COLOR_SCIENCE_AVAILABLE else 'b*',
                'title': 'Color Optimization Progress in CAM02-UCS a′b′ plane' if COLOR_SCIENCE_AVAILABLE else 'Color Optimization Progress in CIELAB a*b* plane'
            }
        }
            
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
        return is_stuck

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

@app.get("/api/color-space-data")
async def get_color_space_data():
    """Get color space data for perceptual plotting"""
    try:
        data = color_optimizer.get_color_space_data()
        return {
            'status': 'success',
            'data': data
        }
    except Exception as e:
        logger.error(f"Color space data error: {e}")
        raise HTTPException(status_code=500, detail=f"Color space data error: {str(e)}")

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
