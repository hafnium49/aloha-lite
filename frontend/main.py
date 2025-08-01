#!/usr/bin/env python3
"""
Hue‑only Colour‑mix Optimiser – FastAPI Frontend
────────────────────────────────────────────────
◆ Three fixed stock solutions: red, yellow, blue
◆ Objective           : minimise |Δ hue|  (degrees)
◆ Control parameters  : dispense volumes (mL) of R, Y, B
"""

from __future__ import annotations
import random, logging, httpx, os, uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ── optional ML libs ─────────────────────────────────────────────────────────
try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    from scipy.optimize import minimize
    ML_AVAILABLE = True
except ImportError:
    print("⚠️  ML libraries not available – optimiser will fall back to random search")
    ML_AVAILABLE = False

# ── basic config & logging ───────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

ROBOT_SERVICE_URL  = os.getenv("ROBOT_SERVICE_URL" , "http://localhost:8000")
VISION_SERVICE_URL = os.getenv("VISION_SERVICE_URL", "http://localhost:5000")

# ── pigments (no white solvent) ──────────────────────────────────────────────
PIGMENTS = ("red", "yellow", "blue")
N_PIG    = 3              # fixed number of controllable channels

# ╔═════════════════════════════════════╗
# ║        H U E   O P T I M I S E R    ║
# ╚═════════════════════════════════════╝
class ColorOptimizer:
    """Bayesian optimiser that works purely in *hue* space."""

    # ── helper: RGB↔HSV -------------------------------------------------------
    @staticmethod
    def _rgb_to_hue(rgb: Tuple[int, int, int]) -> float:
        """Return hue in degrees [0,360).  Grey/black returns 0."""
        r, g, b = [x / 255.0 for x in rgb]
        mx, mn = max(r, g, b), min(r, g, b)
        if mx == mn:
            return 0.0
        if mx == r:
            h = (60 * ((g - b) / (mx - mn))) % 360
        elif mx == g:
            h = (60 * ((b - r) / (mx - mn)) + 120) % 360
        else:
            h = (60 * ((r - g) / (mx - mn)) + 240) % 360
        return h

    @staticmethod
    def _hue_to_rgb(h: float) -> Tuple[int, int, int]:
        """Full‑saturation HSV→RGB8 for display."""
        h = h % 360
        s, v = 1.0, 1.0
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if   0 <= h < 60:   rp, gp, bp = c, x, 0
        elif 60 <= h < 120: rp, gp, bp = x, c, 0
        elif 120 <= h < 180: rp, gp, bp = 0, c, x
        elif 180 <= h < 240: rp, gp, bp = 0, x, c
        elif 240 <= h < 300: rp, gp, bp = x, 0, c
        else:                rp, gp, bp = c, 0, x
        return tuple(int(round((v_ + m) * 255)) for v_ in (rp, gp, bp))

    @staticmethod
    def _hue_distance(h1: float, h2: float) -> float:
        """Shortest angular distance in degrees."""
        d = abs((h1 - h2) % 360)
        return 360 - d if d > 180 else d

    # ── constructor ----------------------------------------------------------
    def __init__(self):
        self.target_hue: Optional[float] = None
        self.history: List[Dict] = []           # each: ratios, measured_rgb, hue, dist
        self.gp: Optional[GaussianProcessRegressor] = None

    # ── normalise ratios -----------------------------------------------------
    @staticmethod
    def _normalize(d: Dict[str, float], *, total: float = 3.0) -> Dict[str, float]:
        """Scale so that Σ=total ‑ keeps proportions, enforces min 0.05 mL each."""
        arr = np.array([max(0.05, d.get(k, 0.0)) for k in PIGMENTS])
        scale = total / arr.sum()
        arr *= scale
        return {k: float(arr[i]) for i, k in enumerate(PIGMENTS)}

    def set_target_hue(self, hue: float):
        self.target_hue = hue % 360
        log.info("🎯 Target hue %.1f°", self.target_hue)

    def add_measurement(self, ratios: Dict[str, float], measured_rgb: Tuple[int,int,int]):
        hue = self._rgb_to_hue(measured_rgb)
        dist = self._hue_distance(hue, self.target_hue) if self.target_hue is not None else None
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "ratios": ratios.copy(),
            "measured_rgb": measured_rgb,
            "hue": hue,
            "distance": dist
        })
        log.info("📊 Trial #%d  measured hue %.1f°  Δ=%.1f°",
                 len(self.history), hue, dist if dist is not None else -1)

    # ── initial heuristic ----------------------------------------------------
    def _hue_guess(self) -> Dict[str, float]:
        """Map desired hue to an initial RGB‑triangle interpolation."""
        h = self.target_hue % 360
        # vertices at 0° (R), 60° (Y), 240° (B)
        if   0   <= h < 60:   r, y, b = 1.0, h/60, 0.0
        elif 60  <= h < 120:  r, y, b = (120-h)/60, 1.0, 0.0
        elif 120 <= h < 180:  r, y, b = 0.0, (180-h)/60, (h-120)/60
        elif 180 <= h < 240:  r, y, b = 0.0, 0.0, 1.0          # cyan‑blue strip
        elif 240 <= h < 300:  r, y, b = (h-240)/60, 0.0, 1.0
        else:                 r, y, b = 1.0, 0.0, (360-h)/60
        return self._normalize(dict(red=r, yellow=y, blue=b))

    # ── GP proposal ----------------------------------------------------------
    def _gp_next(self) -> Dict[str, float]:
        if not ML_AVAILABLE or len(self.history) < 2:
            # random Dirichlet sample
            w = np.random.dirichlet([1,1,1])
            return self._normalize(dict(zip(PIGMENTS, w * 3.0)))
        # prepare training data
        X = np.array([[h["ratios"]["red"],
                       h["ratios"]["yellow"],
                       h["ratios"]["blue"]] for h in self.history])
        y = np.array([h["distance"] for h in self.history])
        self.gp = GaussianProcessRegressor(
            ConstantKernel(1.0, (1e-2, 1e3)) * RBF(length_scale=1.0),
            alpha=1e-4, normalize_y=True)
        self.gp.fit(X, y)
        f_best = y.min()

        def acq(x):
            m, s = self.gp.predict(x.reshape(1,-1), return_std=True)
            # Expected‑improvement
            z = (f_best - m) / (s + 1e-9)
            from scipy.stats import norm
            return -(f_best - m) * norm.cdf(z) - s * norm.pdf(z)

        # multi‑start optim
        starts = np.random.uniform(0.05, 3.0, size=(8,3))
        best_x, best_v = None, 1e9
        for s0 in starts:
            res = minimize(acq, s0, bounds=[(0.05,3.0)]*3, method='L-BFGS-B')
            if res.success and res.fun < best_v:
                best_v, best_x = res.fun, res.x
        choice = best_x if best_x is not None else starts[0]
        return self._normalize(dict(zip(PIGMENTS, choice)))

    # ── main decision --------------------------------------------------------
    def recommend_next_ratios(self) -> Dict[str, float]:
        if self.target_hue is None:
            return self._normalize(dict(red=1,yellow=1,blue=1))
        if len(self.history) == 0:
            return self._hue_guess()
        return self._gp_next()

    # ── simple stats ---------------------------------------------------------
    def get_stats(self):
        d = [h["distance"] for h in self.history]
        return {
            "total_attempts": len(d),
            "best_distance":  min(d) if d else None,
            "current_distance": d[-1] if d else None,
            "average_distance": float(np.mean(d)) if d else None
        }

# ╔═════════════════════════════════════╗
# ║        F A S T A P I   S E R V E R  ║
# ╚═════════════════════════════════════╝
opt = ColorOptimizer()

def _random_target_hue() -> float:
    """Pick a random hue angle with equal chance of R/Y/B sectors."""
    sector = random.choice([0, 60, 240])        # redish, yellowish, bluish
    return (sector + random.uniform(-20, 20)) % 360

@asynccontextmanager
async def lifespan(app: FastAPI):
    h = _random_target_hue()
    opt.set_target_hue(h)
    log.info("🆕  Initial target hue %.1f°", h)
    yield

app = FastAPI(title="Hue‑only Mixer Frontend",
              version="2.0-hue",
              lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"],
                   allow_methods=["*"], allow_credentials=True)

# ── utility ---------------------------------------------------------------
def _hue_hex(h: float) -> str:
    r, g, b = opt._hue_to_rgb(h)
    return f"#{r:02x}{g:02x}{b:02x}"

# ── endpoints -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("/home/hafnium/aloha-lite/frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(404, "index.html not found")

@app.get("/api/target-color")
async def api_target():
    hue = _random_target_hue()
    opt.set_target_hue(hue)
    rgb = opt._hue_to_rgb(hue)
    return {"status":"success", "target_rgb":rgb, "target_hue":hue,
            "target_hex":_hue_hex(hue)}

@app.post("/api/target-color")
async def api_set_target(req: Request):
    data = await req.json()
    hue = float(data.get("hue", 0.0))
    opt.set_target_hue(hue)
    rgb = opt._hue_to_rgb(hue)
    return {"status":"success", "target_rgb":rgb, "target_hue":hue,
            "target_hex":_hue_hex(hue)}

@app.post("/api/recommend-ratios")
async def api_rec(req: Request):
    if req.headers.get("content-type","").startswith("application/json"):
        body = await req.json()
        if "measured_rgb" in body and "ratios" in body:
            opt.add_measurement(body["ratios"], tuple(body["measured_rgb"]))
    ratios = opt.recommend_next_ratios()
    return {"status":"success",
            "recommended_ratios":ratios,
            "statistics":opt.get_stats(),
            "ml_available":ML_AVAILABLE}

@app.get("/api/optimization-history")
async def api_hist():
    return {"status":"success",
            "history":opt.history,
            "statistics":opt.get_stats()}

@app.post("/api/reset-optimization")
async def api_reset():
    opt.history.clear(); opt.gp = None
    return {"status":"success","message":"history reset"}

@app.get("/api/color-space-data")
async def hue_space_data():
    """Return hue history for plotting."""
    if opt.target_hue is None or not opt.history:
        return {"status":"success","data":{"available":False}}
    return {"status":"success","data":{
        "available":True,
        "target":{"hue":opt.target_hue,
                  "rgb":opt._hue_to_rgb(opt.target_hue)},
        "trail":[{"hue":h["hue"], "rgb":h["measured_rgb"]} for h in opt.history]
    }}

# ── simple proxy pass‑throughs to robot / vision (unchanged) --------------
async def _proxy(req: Request, base_url: str, subpath: str):
    url = f"{base_url}/{subpath}"
    async with httpx.AsyncClient(timeout=600.0) as client:
        r = await client.request(req.method, url,
                                 params=req.query_params,
                                 headers={k:v for k,v in req.headers.items()
                                          if k.lower()!='host'},
                                 content=await req.body())
        return r

@app.post("/robot/dispense")
async def dispense_robot(request: Request):
    """Handle dispense requests with format transformation for robot service."""
    body = await request.json()
    log.info("Frontend received dispense request: %s", body)
    
    # Transform simple {red, yellow, blue} format to robot service format
    if isinstance(body, dict) and all(k in body for k in ['red', 'yellow', 'blue']):
        # Extract ratios
        red = float(body.get('red', 0))
        yellow = float(body.get('yellow', 0)) 
        blue = float(body.get('blue', 0))
        
        # Calculate normalized percentages
        total = red + yellow + blue
        if total > 0:
            norm_red = (red / total) * 100
            norm_yellow = (yellow / total) * 100
            norm_blue = (blue / total) * 100
        else:
            norm_red = norm_yellow = norm_blue = 0
        
        # Create robot service format
        robot_request = {
            "mix_id": 1,
            "run_id": 1,
            "colour": "red",  # Default dominant color
            "color_ratios": {
                "red": red,
                "yellow": yellow,
                "blue": blue
            },
            "normalized_percentages": {
                "red": norm_red,
                "yellow": norm_yellow,
                "blue": norm_blue
            }
        }
        
        log.info("Transformed to robot service format: %s", robot_request)
        
        # Forward to robot service
        url = f"{ROBOT_SERVICE_URL}/robot/dispense"
        async with httpx.AsyncClient(timeout=600.0) as client:
            r = await client.post(url, json=robot_request)
            return JSONResponse(r.json() if r.status_code == 200 else {"error": r.text}, 
                              status_code=r.status_code)
    else:
        # Pass through other formats unchanged
        r = await _proxy(request, ROBOT_SERVICE_URL, "robot/dispense")
        return HTMLResponse(r.content, status_code=r.status_code, headers=r.headers)

@app.api_route("/robot/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def proxy_robot(request: Request, path: str):
    r = await _proxy(request, ROBOT_SERVICE_URL, f"robot/{path}")
    return HTMLResponse(r.content, status_code=r.status_code,
                        headers=r.headers)

@app.post("/vision/capture")
async def capture_image():
    """Capture image using vision bridge snapshot endpoint."""
    cmd_id = str(uuid.uuid4())
    
    snapshot_request = {
        "cmd_id": cmd_id,
        "cam_id": "top_cam"
    }
    
    url = f"{VISION_SERVICE_URL}/snapshot"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=snapshot_request)
        if r.status_code != 200:
            raise HTTPException(r.status_code, f"Vision service error: {r.text}")
        
        # The snapshot endpoint returns a URL, but we want to return the actual image
        # Let's fetch the image from the camera directly for the frontend
        camera_url = f"http://phosphobot/camera/snapshot/top_cam?format=jpeg"
        try:
            image_response = await client.get(camera_url, timeout=10.0)
            if image_response.status_code == 200:
                return HTMLResponse(
                    image_response.content,
                    status_code=200,
                    headers={
                        "Content-Type": "image/jpeg",
                        "Content-Length": str(len(image_response.content))
                    }
                )
        except Exception as e:
            log.warning(f"Failed to fetch image directly: {e}")
        
        # Fallback: return the JSON response from snapshot endpoint
        return JSONResponse(r.json())

@app.post("/vision/analyze")
async def analyze_image(request: Request):
    """Analyze uploaded image using vision bridge analyze-beaker endpoint."""
    # Get the form data from the request
    form = await request.form()
    image_file = form.get("image")
    
    if not image_file:
        raise HTTPException(400, "No image file provided")
    
    # Forward to vision bridge analyze-beaker endpoint
    url = f"{VISION_SERVICE_URL}/analyze-beaker"
    
    # Prepare the multipart form data for the vision bridge
    files = {"file": (image_file.filename, await image_file.read(), image_file.content_type)}
    data = {
        "algorithm": "space_mask",  # Use fast space_mask algorithm by default
        "n_clusters": 5
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, files=files, data=data)
        return JSONResponse(r.json() if r.status_code == 200 else {"error": r.text}, 
                          status_code=r.status_code)

@app.api_route("/vision/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def proxy_vision(request: Request, path: str):
    r = await _proxy(request, VISION_SERVICE_URL, path)
    return HTMLResponse(r.content, status_code=r.status_code,
                        headers=r.headers)

@app.get("/status")
async def status():
    return {"frontend":"healthy"}

# ── run directly -----------------------------------------------------------
if __name__ == "__main__":
    import uvicorn, random
    hue0 = _random_target_hue()
    opt.set_target_hue(hue0)
    log.info("▶  Starting with target hue %.1f°", hue0)
    uvicorn.run(app, host="0.0.0.0", port=3000)
