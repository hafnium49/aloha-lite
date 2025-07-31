#!/usr/bin/env python3
"""
Frontend FastAPI Server with ML-based Colour Optimisation

A FastAPI server that serves the frontend HTML interface, proxies robot &
vision requests, and provides colour-mix ratios via a hybrid Bayesian /
calibration optimiser.

This version keeps TWO separate calibration states:

  1. colour_optimizer  – learns its own 3×3 pigment matrix from data.
  2. bottle_model      – holds a fixed, hidden 3×3 matrix that represents
                         the real bottle strengths; it is ONLY used to
                         generate *reachable* target colours.
"""

import os, json, random, logging, httpx
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# ── ML / SciPy ───────────────────────────────────────────────────────────────
try:
    from scipy.optimize import minimize, lsq_linear
    from scipy.spatial.distance import euclidean
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    from scipy.stats import norm
    ML_AVAILABLE = True
except ImportError:
    print("⚠️  ML libraries not available.  pip install scipy scikit-learn")
    ML_AVAILABLE = False

# ── Colour-science (optional) ────────────────────────────────────────────────
try:
    import colour
    COLOR_SCIENCE_AVAILABLE = True
except ImportError:
    COLOR_SCIENCE_AVAILABLE = False

# ── logging & config ────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROBOT_SERVICE_URL  = os.getenv("ROBOT_SERVICE_URL",  "http://localhost:8000")
VISION_SERVICE_URL = os.getenv("VISION_SERVICE_URL", "http://localhost:5000")

# ╔══════════════════════════════════════╗
# ║          C O L O R  O P T I M I S E R          ║  (UNCHANGED LOGIC)
# ╚══════════════════════════════════════╝
class ColorOptimizer:
    """
    Hybrid optimiser with 4 phases.
    Phase schedule  (N = len(history) *before* proposing a mix)
      0   : pure dominant pigment
      1   : GP only
      2   : rough α-calibration  +  GP  (0.6 / 0.4)
      3-7 : full 9-parameter NNLS  +  GP   (calib weight ↑, GP ↓)
      ≥8  : NNLS only
    """
    # ---------- init ----------
    def __init__(self):
        self.history: List[Dict] = []
        self.target_color: Optional[Tuple[int,int,int]] = None
        self.P_est: Optional[np.ndarray] = None      # (3,3) absorbance/volume
        self.std_error: Optional[float] = None
        self.gp_model: Optional[GaussianProcessRegressor] = None
        self.epsilon_rgb = 10.0                      # only used for info

    # ---------- low-level helpers ----------
    @staticmethod
    def _lin_rgb(rgb):
        arr = np.asarray(rgb)/255.0
        return np.power(arr, 2.2).clip(1e-4, 1)

    @classmethod
    def _rgb_to_absorb(cls, rgb):
        return -np.log10(cls._lin_rgb(rgb))

    def _ratios_to_array(self, d):       # dict→[r,y,b]
        return np.array([d.get('red',0), d.get('yellow',0), d.get('blue',0)])

    def _array_to_ratios(self, a):
        return {'red':float(a[0]), 'yellow':float(a[1]), 'blue':float(a[2])}

    def _normalize(self, d):
        s = sum(d.values()) or 1.0
        f = 3.0/s
        return {k:max(0.1,v*f) for k,v in d.items()}

    # ---------- public methods ----------
    def set_target_color(self, rgb):
        self.target_color = rgb
        logger.info("🎯 New target colour RGB%s", rgb)

    def add_measurement(self, ratios, measured_rgb):
        d = euclidean(measured_rgb, self.target_color) if self.target_color else 0
        self.history.append({"timestamp":datetime.now().isoformat(),
                             "ratios":ratios.copy(),
                             "measured_rgb":measured_rgb,
                             "distance_to_target":d})
        logger.info("📊 Logged trial #%d  dist≈%.2f", len(self.history), d)

    # ---------- calibration ----------
    def _rough_scale_calibration(self):
        if len(self.history) < 2: return
        P_hue = np.array([[0.8,0.1,0.1],
                          [0.2,0.9,0.1],
                          [0.1,0.1,0.9]])
        W = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        A = np.stack([self._rgb_to_absorb(h['measured_rgb']) for h in self.history])
        L = np.einsum('nk,kj->nkj', W, P_hue).reshape(-1,3)
        alpha, *_ = np.linalg.lstsq(L, A.reshape(-1), rcond=None)
        self.P_est = np.diag(alpha.clip(1e-6)) @ P_hue

    def _fit_full_calibration(self):
        if len(self.history) < 3 or not ML_AVAILABLE: return
        W = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        A = np.stack([self._rgb_to_absorb(h['measured_rgb']) for h in self.history])
        P = np.zeros((3,3))
        for ch in range(3):
            res = lsq_linear(W, A[:,ch], bounds=(0,np.inf))
            P[:,ch] = res.x
        self.P_est = P
        resid = A - W @ P
        self.std_error = float(np.sqrt(np.mean(resid**2)))

    def _inverse_weights(self):
        if self.P_est is None or not ML_AVAILABLE:
            return None
        res = lsq_linear(self.P_est.T,
                         self._rgb_to_absorb(self.target_color),
                         bounds=(0,8))
        return self._normalize(self._array_to_ratios(res.x))

    # ---------- GP helper ----------
    def _gp_next(self, seed=None):
        if not ML_AVAILABLE: return self._get_random()
        X = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        y = np.array([h['distance_to_target'] for h in self.history])
        X += np.random.normal(0,1e-6,X.shape)
        gp = GaussianProcessRegressor(ConstantKernel(1.0,(1e-3,1e3))*RBF(1.0,(1e-2,1e2)),
                                      alpha=1e-4, normalize_y=True, n_restarts_optimizer=3)
        gp.fit(X,y); self.gp_model = gp; f_best = y.min()
        def acq(x):
            m,s = gp.predict(x.reshape(1,-1), return_std=True)
            xi  = 0.1; z = (f_best-m-xi)/(s+1e-9)
            return -(f_best-m-xi)*norm.cdf(z) - s*norm.pdf(z)
        starts = [np.random.uniform(0.1,5,(3,)) for _ in range(6)]
        if seed is not None: starts.append(self._ratios_to_array(seed))
        best_x,best_v = None,np.inf
        for s0 in starts:
            res = minimize(acq, s0, method='L-BFGS-B', bounds=[(0.05,8)]*3)
            if res.success and res.fun < best_v:
                best_v,best_x = res.fun,res.x
        return self._normalize(self._array_to_ratios(best_x if best_x is not None else starts[0]))

    # ---------- misc helpers ----------
    def _get_random(self):
        return self._normalize({c:random.uniform(0.1,3.0) for c in ('red','yellow','blue')})

    # ---------- main decision ----------
    def recommend_next_ratios(self):
        N = len(self.history)
        
        # Handle case where no target color is set
        if self.target_color is None:
            logger.warning("⚠️  No target color set, using random ratios")
            return self._get_random()
            
        if N == 0:
            # Instead of pure dominant color, use a smarter initial guess
            # Convert target RGB to absorbance and estimate ratios
            target_absorb = self._rgb_to_absorb(self.target_color)
            
            # Use a rough heuristic based on color characteristics
            r, g, b = self.target_color
            
            # Estimate ratios based on color appearance
            red_ratio = max(0.1, (r - g - b + 255) / 255.0 * 2.0)
            yellow_ratio = max(0.1, (r + g - 2*b + 255) / 255.0 * 1.5) 
            blue_ratio = max(0.1, (b - r - g + 255) / 255.0 * 2.0)
            
            # Create initial guess and normalize
            initial_guess = {'red': red_ratio, 'yellow': yellow_ratio, 'blue': blue_ratio}
            return self._normalize(initial_guess)

        if N == 1:
            return self._gp_next()

        if N == 2:
            self._rough_scale_calibration()
            w_cal = self._inverse_weights()
            w_gp  = self._gp_next()
            return w_gp if w_cal is None else self._normalize(
                {c:0.6*w_cal[c]+0.4*w_gp[c] for c in w_cal})

        if 3 <= N <= 7:
            self._fit_full_calibration()
            w_cal = self._inverse_weights()
            w_gp  = self._gp_next(seed=w_cal)
            if w_cal is None: return w_gp
            w_cal_w = (N-1)/8.0; w_gp_w = 1.0 - w_cal_w
            return self._normalize({c:w_cal_w*w_cal[c]+w_gp_w*w_gp[c] for c in w_cal})

        self._fit_full_calibration()
        res = self._inverse_weights()
        return res if res else self._get_random()

    # ---------- lightweight stats ----------
    def get_statistics(self):
        d = [h['distance_to_target'] for h in self.history]
        return {"total_attempts":len(self.history),
                "best_distance":min(d) if d else None,
                "current_distance":d[-1] if d else None,
                "std_error_absorb":self.std_error}

# ╔══════════════════════════════════════╗
# ║    H I D D E N   B O T T L E   M O D E L     ║
# ╚══════════════════════════════════════╝
class BottleModel(ColorOptimizer):
    """Fixed pigment matrix known only to the backend (for target sampling)."""
    def __init__(self, P_true: np.ndarray):
        super().__init__()
        self.P_est = P_true.copy()   # never changes

def load_ground_truth_calibration():
    """
    Load ground truth calibration data from JSON files and construct the calibration matrix.
    Returns a 3x3 numpy array representing the true pigment absorbance matrix.
    """
    ground_truth_dir = Path(__file__).parent / "ground_truth_calibration"

    try:
        # Try to load calibration summary first.  It may contain either a direct
        # calibration matrix or RGB measurements for each solution.
        summary_file = ground_truth_dir / "calibration_summary.json"
        summary_rgb = {}
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary_data = json.load(f)

            if "calibration_matrix" in summary_data.get("calibration_summary", {}):
                matrix_data = summary_data["calibration_summary"]["calibration_matrix"]["matrix"]
                P_true = np.array(matrix_data)
                logger.info("🎯 Loaded ground truth matrix from calibration summary")
                logger.info("📊 Matrix shape: %s, mean absorbance: %.3f", P_true.shape, P_true.mean())
                return P_true

            solutions_block = summary_data.get("calibration_summary", {}).get("solutions", {})
            for colour in ("red", "yellow", "blue"):
                if colour in solutions_block and "rgb" in solutions_block[colour]:
                    summary_rgb[colour] = solutions_block[colour]["rgb"]

        # Next try individual solution files which may contain coefficients or RGB values
        solutions = ["red", "yellow", "blue"]
        absorbance_coefficients = []
        rgb_colors = []
        
        for solution in solutions:
            solution_file = ground_truth_dir / f"{solution}_solution_ground_truth.json"
            if solution_file.exists():
                with open(solution_file, 'r') as f:
                    solution_data = json.load(f)

                abs_coeff = solution_data.get("calibration_parameters", {}).get("absorbance_coefficient")
                rgb = solution_data.get("color_measurement", {}).get("rgb")

                absorbance_coefficients.append(abs_coeff)
                rgb_colors.append(rgb)

                logger.info("📊 Loaded %s solution: RGB%s, abs_coeff=%s",
                           solution, rgb, abs_coeff)
            else:
                logger.warning("⚠️  Missing ground truth file: %s", solution_file)
                absorbance_coefficients.append(None)
                rgb_colors.append(None)
        
        # Priority 1: use absorbance coefficients if all are available
        if all(c is not None for c in absorbance_coefficients):
            P_true = np.array([
                [absorbance_coefficients[0], 0.1, 0.08],
                [0.15, absorbance_coefficients[1], 0.1],
                [0.12, 0.15, absorbance_coefficients[2]]
            ])
            logger.info("🔧 Constructed ground truth matrix from individual files")
            logger.info("📊 Matrix:\n%s", P_true)
            return P_true

        # Priority 2: compute matrix from RGB measurements
        rgb_source = summary_rgb if len(summary_rgb) == 3 else {
            c: rgb_colors[i] for i, c in enumerate(solutions) if rgb_colors[i] is not None
        }
        if len(rgb_source) == 3:
            # Ground truth calibration uses single solutions at total volume 3.0
            # For w = [3.0, 0.0, 0.0], we want A = w @ P_est = rgb_to_absorb(red_rgb)
            # This means P_est[0,0] = rgb_to_absorb(red_rgb)[0] / 3.0, P_est[0,1] = rgb_to_absorb(red_rgb)[1] / 3.0, etc.
            # But we also need the matrix to represent the correct mixing behavior.
            # The correct approach: P_est[i,j] represents the j-th RGB component absorbance per unit of i-th color
            P_true = np.array([
                ColorOptimizer._rgb_to_absorb(rgb_source["red"]) / 3.0,    # Row 0: red color's absorbance per unit volume
                ColorOptimizer._rgb_to_absorb(rgb_source["yellow"]) / 3.0, # Row 1: yellow color's absorbance per unit volume  
                ColorOptimizer._rgb_to_absorb(rgb_source["blue"]) / 3.0    # Row 2: blue color's absorbance per unit volume
            ])  # Shape: (3,3) where rows are colors, columns are RGB channels
            
            logger.info("🔧 Constructed ground truth matrix from RGB measurements (normalized for volume 3.0)")
            logger.info("📊 Matrix:\n%s", P_true)
            return P_true
            
    except Exception as e:
        logger.warning("⚠️  Error loading ground truth calibration: %s", e)
        logger.info("🔄 Falling back to random matrix generation")
    
    # Final fallback: generate random matrix (original behavior)
    np.random.seed(42)
    P_fallback = np.abs(np.random.normal(loc=0.3, scale=0.15, size=(3,3)))
    logger.info("🎲 Using random fallback matrix")
    return P_fallback

# --- Load ground truth calibration and create bottle model ---
from pathlib import Path
_P_TRUE = load_ground_truth_calibration()
bottle_model = BottleModel(_P_TRUE)

# ╔══════════════════════════════════════╗
# ║     Target-colour helper functions     ║
# ╚══════════════════════════════════════╝
def _sample_reachable_rgb(P_est: np.ndarray,
                          max_total: float = 3.0) -> Tuple[Tuple[int,int,int], np.ndarray]:
    """Return (rgb8, weights) inside the reachable gamut of P_est.
    
    Generates normalized color ratios that sum to max_total (default 3.0)
    to match the ColorOptimizer's normalization scheme and ground truth calibration.
    """
    # Generate random ratios using exponential distribution to avoid uniform bias
    raw_ratios = np.random.exponential(1.0, 3)
    
    # Create ratio dictionary and normalize using the same method as ColorOptimizer
    ratio_dict = {'red': raw_ratios[0], 'yellow': raw_ratios[1], 'blue': raw_ratios[2]}
    
    # Apply ColorOptimizer._normalize() logic exactly
    s = sum(ratio_dict.values()) or 1.0
    f = max_total / s
    normalized_dict = {k: max(0.1, v * f) for k, v in ratio_dict.items()}
    
    # Convert back to array for matrix operations
    w = np.array([normalized_dict['red'], normalized_dict['yellow'], normalized_dict['blue']])
    
    # Calculate absorbance and convert to RGB
    A = w @ P_est
    rgb_lin = 10 ** (-A)
    rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
    return rgb8, w

def generate_random_target_color() -> Tuple[int,int,int]:
    """
    Draw a target colour guaranteed reachable by the current bottle model.
    Uses normalized ratios that sum to 3.0 to match ground truth calibration conditions.
    While no model exists (very first run only), fall back to a safe palette.
    """
    if bottle_model.P_est is not None:
        rgb, _ = _sample_reachable_rgb(bottle_model.P_est, max_total=3.0)
        return rgb

    # fallback (should never be used after first start)
    safe_palette = [(255,0,0),(255,255,0),(0,0,255)]
    return random.choice(safe_palette)

# ╔══════════════════════════════════════╗
# ║     FastAPI   +  endpoints (UNCHANGED)    ║
# ╚══════════════════════════════════════╝
color_optimizer = ColorOptimizer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    rgb0 = generate_random_target_color()
    color_optimizer.set_target_color(rgb0)
    logger.info("🎯 Initial target RGB%s", rgb0)
    yield
    # Shutdown (nothing needed)

app = FastAPI(title="Aloha-Lite Frontend",
              description="Web interface for robot control and colour mixing",
              version="1.0.0",
              lifespan=lifespan)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], allow_headers=["*"],
                   allow_methods=["*"], allow_credentials=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("/home/hafnium/aloha-lite/frontend/index.html") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend HTML not found")

@app.get("/api/target-color")
async def api_target():
    rgb = generate_random_target_color()
    color_optimizer.set_target_color(rgb)
    # Ensure RGB values are native Python integers for JSON serialization
    rgb_clean = tuple(int(x) for x in rgb)
    return {"status":"success",
            "target_rgb":rgb_clean,
            "target_hex":f"#{rgb_clean[0]:02x}{rgb_clean[1]:02x}{rgb_clean[2]:02x}"}

@app.post("/api/target-color")
async def api_set_target(req:Request):
    data = await req.json()
    rgb = tuple(data.get("rgb",[255,0,0]))
    color_optimizer.set_target_color(rgb)
    # Ensure RGB values are native Python integers for JSON serialization
    rgb_clean = tuple(int(x) for x in rgb)
    return {"status":"success","target_rgb":rgb_clean,
            "target_hex":f"#{rgb_clean[0]:02x}{rgb_clean[1]:02x}{rgb_clean[2]:02x}"}

@app.post("/api/recommend-ratios")
async def api_recommend(req:Request):
    data = await req.json() if req.headers.get("content-type","").startswith("application/json") else {}
    if "measured_rgb" in data and "ratios" in data:
        color_optimizer.add_measurement(data["ratios"], tuple(data["measured_rgb"]))
    return {"status":"success",
            "recommended_ratios":color_optimizer.recommend_next_ratios(),
            "statistics":color_optimizer.get_statistics(),
            "ml_available":ML_AVAILABLE}

@app.get("/api/optimization-history")
async def api_history():
    return {"status":"success",
            "history":color_optimizer.history,
            "statistics":color_optimizer.get_statistics()}

@app.post("/api/reset-optimization")
async def api_reset():
    color_optimizer.history.clear(); color_optimizer.gp_model=None
    return {"status":"success","message":"history reset"}

# ╔══════════════════════════════════════╗
# ║        Robot & Vision Proxy Endpoints        ║
# ╚══════════════════════════════════════╝

@app.post("/robot/dispense")
async def robot_dispense(req: Request):
    """Proxy endpoint for robot dispensing commands."""
    try:
        data = await req.json()
        logger.info("🤖 Forwarding dispense request to robot service: %s", data)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ROBOT_SERVICE_URL}/dispense",
                json=data,
                timeout=30.0
            )
            
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Robot dispense successful: %s", result)
            return result
        else:
            logger.error("❌ Robot dispense failed: %d %s", response.status_code, response.text)
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
    except httpx.RequestError as e:
        logger.error("🔌 Robot service connection error: %s", e)
        raise HTTPException(status_code=503, detail=f"Robot service unavailable: {e}")
    except Exception as e:
        logger.error("⚠️ Robot dispense error: %s", e)
        raise HTTPException(status_code=500, detail=f"Dispense failed: {e}")

@app.get("/robot/health")
async def robot_health():
    """Check robot service health."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ROBOT_SERVICE_URL}/health", timeout=5.0)
        return {"robot_service": "connected", "status_code": response.status_code}
    except Exception as e:
        return {"robot_service": "disconnected", "error": str(e)}

@app.post("/vision/analyze")
async def vision_analyze(req: Request):
    """Proxy endpoint for vision analysis."""
    try:
        data = await req.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{VISION_SERVICE_URL}/analyze", json=data, timeout=30.0)
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception as e:
        logger.error("🔌 Vision service error: %s", e)
        raise HTTPException(status_code=503, detail=f"Vision service unavailable: {e}")

@app.get("/vision/health")
async def vision_health():
    """Check vision service health."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{VISION_SERVICE_URL}/health", timeout=5.0)
        return {"vision_service": "connected", "status_code": response.status_code}
    except Exception as e:
        return {"vision_service": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    rgb0 = generate_random_target_color()
    color_optimizer.set_target_color(rgb0)
    logger.info("🎯 Initial target RGB%s", rgb0)
    uvicorn.run(app, host="0.0.0.0", port=3000)
