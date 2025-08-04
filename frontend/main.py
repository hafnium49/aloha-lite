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
from math import atan2, degrees
from typing import List, Tuple, Dict, Optional
from contextlib import asynccontextmanager
from pathlib import Path
from collections import deque

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

# Washing bottle calibration control
ENABLE_WASHING_BOTTLE_CALIBRATION = os.getenv("ENABLE_WASHING_BOTTLE_CALIBRATION", "true").lower() == "true"

# ── NEW GLOBALS (add near the other module‑level constants) ──────────
PIGMENTS = ("red", "yellow", "blue", "white")   # 4 liquids; white = solvent
N_PIG    = len(PIGMENTS)

# ── GLOBAL CONSTANTS & RUNTIME STATE ────────────────────
PRIMARY_HUES    = (0, 60, 240)      # rough LAB-hue angles for R, Y, B
HUE_EXCLUSION   = 8                 # degrees to exclude around primaries (reduced from 15)
MAX_DIFFICULTY  = 0.85              # ≤ 0.85 means "easy-to-reach" (increased from 0.75)
HUE_HISTORY_LEN = 60                # how many past targets we remember

_hue_history = deque(maxlen=HUE_HISTORY_LEN)   # rolling list of past hues
_cum_vol     = np.zeros(3)                     # Σ of red, yellow, blue mL

# ── Washing-bottle calibration helper ─────────────────────────────────────────
import warnings
from numpy.polynomial.polynomial import Polynomial
from numpy import roots, isreal

_CALIB_PATH = Path(__file__).parent / "washing_bottle_calibration" / \
              "washing_bottle_calibration_summary.json"

def _load_washing_bottle_fits() -> Dict[str, Polynomial]:
    """
    Read cubic-fit coefficients from the calibration summary.

    Returns
    -------
    dict :  {"red": Polynomial, "yellow": Polynomial, "blue": Polynomial}
            where each Polynomial p(dur) ≈ dispensed_mass_g.
    """
    if not _CALIB_PATH.exists():
        raise FileNotFoundError(f"Calibration summary not found: {_CALIB_PATH}")

    with _CALIB_PATH.open() as fp:
        summary = json.load(fp)

    fits = {}
    for entry in summary:
        sol = entry["solution"]          # "red" / "yellow" / "blue"
        # NOTE: numpy.polyfit gave coeffs [a,b,c,d] for a·x³+b·x²+c·x+d
        # The Polynomial class expects coefficients in ascending order.
        a, b, c, d = entry["coefficients"]
        fits[sol] = Polynomial([d, c, b, a])   # p(x) = d + c x + b x² + a x³
    return fits

def _volume_to_duration_memo(colour: str, vol_mL: float) -> float:
    """
    Invert the fitted cubic to find the squeeze duration that yields vol_mL.

    Uses real, positive root closest to zero.  Falls back to linear Newton
    iteration if the cubic inversion fails (rare for monotonic fits).
    """
    fit = _WB_FITS[colour]
    # Solve p(dur) - vol = 0
    r = roots(list((fit - vol_mL).coef[::-1]))  # Polynomial -> numpy.roots expects descending
    real_pos = [float(z.real) for z in r if isreal(z) and z.real > 0]
    if real_pos:
        return min(real_pos)      # the physically valid root
    # Fallback – one Newton step from vol/linear_slope
    lin = fit.coef[1] if len(fit.coef) >= 2 else 1.0
    guess = max(1e-3, vol_mL / lin)
    for _ in range(6):
        f  = fit(guess) - vol_mL
        fp = fit.deriv()(guess)
        guess -= f / (fp or 1e-6)
        if guess > 0 and abs(f) < 1e-3:
            return guess
    warnings.warn(f"[{colour}] duration solve fallback; returning {guess:.3f}s")
    return max(0.05, guess)

def colour_ratios_to_durations(ratios: Dict[str, float],
                               *, total_mL: float = 10.0
                               ) -> Dict[str, float]:
    """
    Convert a {'red':…, 'yellow':…, 'blue':…} colour-ratio dict to
    {'red': dur_s, 'yellow': dur_s, 'blue': dur_s}.

    Steps
    -----
    1. Compute scale so Σvol = total_mL.
    2. For each colour, invert its cubic fit to find the duration.
    3. Return {'red': …, 'yellow': …, 'blue': …}.
    """
    coloured = {k: ratios.get(k, 0.0) for k in ('red', 'yellow', 'blue')}
    s = sum(coloured.values()) or 1.0
    scale = total_mL / s
    scaled_vols = {k: v * scale for k, v in coloured.items()}

    durations = {k: _volume_to_duration_memo(k, v) for k, v in scaled_vols.items()}
    return durations

# Initialize washing bottle fits if calibration is enabled
_WB_FITS = {}
if ENABLE_WASHING_BOTTLE_CALIBRATION:
    try:
        _WB_FITS = _load_washing_bottle_fits()
        logger.info("✅ Washing bottle calibration loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load washing bottle calibration: {e}")
        logger.info("🔄 Washing bottle calibration disabled")
        ENABLE_WASHING_BOTTLE_CALIBRATION = False

# ╔══════════════════════════════════════╗
# ║          C O L O R  O P T I M I S E R          ║  (UPDATED)
# ╚══════════════════════════════════════╝
class ColorOptimizer:
    """
    Hybrid optimiser with 4 phases.
    Phase schedule  (N = len(history) *before* proposing a mix)
      0     : heuristic single‑shot (dominant pigment guess)
      1     : GP only
      2     : rough α‑calibration  +  GP  (0.6 / 0.4)
      3‑8   : full NNLS (9‑param when white locked) +  GP   – weights shift from GP→calib
      3‑11  : full NNLS (12‑param when white learnable) +  GP   – weights shift from GP→calib
      ≥9/12 : NNLS only
    The model matrix P ∈ ℝ^(4×3) now includes a 4th "white" row
    (locked to zero absorbance by default, assuming pure RGB(255,255,255) background).
    """

    # ---------- init ----------
    def __init__(self, allow_white_absorbance: bool = False, hue_only_mode: bool = True):
        """
        Initialize ColorOptimizer.
        
        Args:
            allow_white_absorbance: If False (default), white-solvent absorbance is locked to zero
                                  assuming pure RGB(255,255,255) background. If True, allows
                                  the optimizer to learn white-solvent absorbance parameters.
            hue_only_mode: If True (default), use hue-only optimization for early phases.
                          If False, use RGB-based optimization.
        """
        self.history: List[Dict] = []
        self.target_color: Optional[Tuple[int, int, int]] = None
        self.hue_target_deg: Optional[float] = None
        self.P_est: Optional[np.ndarray] = None    # (4,3) absorbance/volume
        self.std_error: Optional[float] = None
        self.gp_model: Optional[GaussianProcessRegressor] = None
        self.epsilon_rgb = 10.0                   # diagnostic only
        self.allow_white_absorbance = allow_white_absorbance
        self.hue_only_mode = hue_only_mode

    # ---------- low‑level helpers ----------
    @staticmethod
    def _lin_rgb(rgb):
        arr = np.asarray(rgb) / 255.0
        return np.power(arr, 2.2).clip(1e-4, 1)

    @classmethod
    def _rgb_to_absorb(cls, rgb):
        return -np.log10(cls._lin_rgb(rgb))

    # RGB → CIELAB → hue conversion for hue-only optimization
    @staticmethod
    def _rgb_to_lab(rgb):
        """Convert RGB to CIELAB."""
        # Normalize RGB to [0, 1]
        r, g, b = np.array(rgb) / 255.0
        
        # sRGB to XYZ conversion
        def gamma_correct(c):
            return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
        
        r, g, b = map(gamma_correct, [r, g, b])
        
        # XYZ using sRGB matrix
        X = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        Y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        Z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        # XYZ to CIELAB
        Xn, Yn, Zn = 0.95047, 1.00000, 1.08883  # D65 illuminant
        
        def f(t):
            return t ** (1/3) if t > 0.008856 else (7.787 * t + 16/116)
        
        fx = f(X / Xn)
        fy = f(Y / Yn)
        fz = f(Z / Zn)
        
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        
        return L, a, b

    @classmethod
    def _hue_deg(cls, rgb):
        """Extract hue angle in degrees from RGB."""
        L, a, b = cls._rgb_to_lab(rgb)
        return degrees(atan2(b, a)) % 360

    @staticmethod
    def _signed_hue_diff(h_from, h_to):
        """Return signed shortest distance h_from → h_to  (deg, –180…+180)."""
        d = (h_to - h_from + 180) % 360 - 180
        return d

    @staticmethod
    def _ang_diff(h1, h2):
        """Angular difference between two hue angles (in degrees)."""
        diff = abs(h1 - h2)
        return min(diff, 360 - diff)

    # dict ⇆ ndarray conversions (4 components)
    def _ratios_to_array(self, d):
        return np.array([d.get(k, 0.0) for k in PIGMENTS])

    def _array_to_ratios(self, a):
        return {k: float(a[i]) for i, k in enumerate(PIGMENTS)}

    # volume‐normalisation: coloured liquids are rescaled to ≤ max_total;
    # leftover volume is assigned to "white" (never <0.1 mL)
    def _normalize(self, d, *, max_total: float = 10.0):
        coloured = {k: v for k, v in d.items() if k != "white"}
        s = sum(coloured.values()) or 1.0
        f = min(1.0, max_total / s)
        out = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
        out["white"] = max_total - sum(out.values())
        if out["white"] < 0.1:                     # enforce minimum solvent
            deficit = 0.1 - out["white"]
            scale = (sum(out.values()) - deficit) / sum(out.values())
            for k in ('red', 'yellow', 'blue'):
                out[k] *= scale
            out["white"] = 0.1
        return out

    # ---------- public API ----------
    def set_target_color(self, rgb):
        self.target_color = rgb
        self.hue_target_deg = self._hue_deg(rgb)
        logger.info("🎯 New target colour RGB%s (hue: %.1f°)", rgb, self.hue_target_deg)

    def add_measurement(self, ratios, measured_rgb):
        if self.hue_target_deg is not None:
            measured_hue = self._hue_deg(measured_rgb)
            d = self._ang_diff(measured_hue, self.hue_target_deg)
        else:
            d = euclidean(measured_rgb, self.target_color) if self.target_color else 0
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "ratios": ratios.copy(),
            "measured_rgb": measured_rgb,
            "distance_to_target": d
        })
        
        # Store hue data for visualization
        h = self._hue_deg(measured_rgb)
        self.history[-1]["measured_hue_deg"] = h
        if self.hue_target_deg is not None:
            self.history[-1]["hue_error_deg"] = self._ang_diff(h, self.hue_target_deg)
        
        logger.info("📊 Logged trial #%d  dist≈%.2f", len(self.history), d)

    # ---------- calibration ----------
    def _rough_scale_calibration(self):
        if len(self.history) < 2:
            return
        P_hue = np.array([[0.8, 0.1, 0.1],       # red
                          [0.2, 0.9, 0.1],       # yellow
                          [0.1, 0.1, 0.9],       # blue
                          [0.0, 0.0, 0.0]])      # white (locked to zero)
        W = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])  # (n_history, 4)
        A = np.stack([self._rgb_to_absorb(h['measured_rgb']) for h in self.history])  # (n_history, 3)
        
        # For rough calibration, we solve for a single scale factor per RGB channel
        # We want: A ≈ W @ (alpha * P_hue) where alpha is a 3-element vector
        # This means we need to solve: A.flatten() ≈ (W @ P_hue @ diag(alpha)).flatten()
        
        # Compute W @ P_hue to get (n_history, 3) matrix
        WP = W @ P_hue  # (n_history, 3)
        
        # For each RGB channel, solve for the scaling factor
        alpha = np.zeros(3)
        for ch in range(3):
            if np.sum(WP[:, ch]**2) > 1e-12:  # Avoid division by zero
                alpha[ch] = np.sum(WP[:, ch] * A[:, ch]) / np.sum(WP[:, ch]**2)
            else:
                alpha[ch] = 1.0
        
        alpha = alpha.clip(1e-6)  # Ensure positive values
        self.P_est = P_hue * alpha[np.newaxis, :]  # Broadcast scaling
        
        # Lock white-solvent absorbance to zero unless explicitly allowed
        if not self.allow_white_absorbance:
            self.P_est[3, :] = 0.0

    def _first_order_correction(self) -> Optional[Dict[str, float]]:
        """
        Single‑step Newton / least‑squares correction based on the *hue prototype*
        matrix P_hue.  Uses only the last trial, so it is well‑posed with N = 1.
        Returns a normalised pigment‑ratio dict or None on failure.
        """
        if not self.history or self.target_color is None:
            return None

        # Prototype per‑unit‑volume absorbance (same as in _rough_scale_calibration)
        P_hue = np.array([[0.8, 0.1, 0.1],   # red
                          [0.2, 0.9, 0.1],   # yellow
                          [0.1, 0.1, 0.9]])  # blue   (white omitted)

        last = self.history[-1]
        w_old = self._ratios_to_array(last["ratios"])[:3]           # (3,)
        A_old = self._rgb_to_absorb(last["measured_rgb"])           # (3,)
        A_tgt = self._rgb_to_absorb(self.target_color)              # (3,)
        dA    = A_tgt - A_old                                       # desired change

        # Solve P_hue.T @ Δw ≈ dA   (bounded, allow negative Δw but small)
        if not ML_AVAILABLE:
            return None
            
        res = lsq_linear(P_hue.T, dA,
                         bounds=(-1.0, 1.0),  # safety bounds per pigment
                         lsmr_tol=1e-4)

        if not res.success:
            return None

        w_new_coloured = np.clip(w_old + res.x, 0.0, 15.0)           # keep ≥0
        ratios = dict(zip(('red', 'yellow', 'blue'), w_new_coloured))
        return self._normalize(ratios)                              # adds white

    def _fit_full_calibration(self):
        if len(self.history) < 3 or not ML_AVAILABLE:
            return
        W = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        A = np.stack([self._rgb_to_absorb(h['measured_rgb']) for h in self.history])
        P = np.zeros((N_PIG, 3))
        for ch in range(3):
            res = lsq_linear(W, A[:, ch], bounds=(0, np.inf))
            P[:, ch] = res.x
        self.P_est = P
        
        # Lock white-solvent absorbance to zero unless explicitly allowed
        if not self.allow_white_absorbance:
            self.P_est[3, :] = 0.0
            
        resid = A - W @ self.P_est
        self.std_error = float(np.sqrt(np.mean(resid ** 2)))

    def _inverse_weights(self):
        if self.P_est is None or not ML_AVAILABLE:
            return None
        res = lsq_linear(self.P_est.T,
                         self._rgb_to_absorb(self.target_color),
                         bounds=(0, 25))
        return self._normalize(self._array_to_ratios(res.x))

    # ---------- GP helper ----------
    def _gp_next(self, seed=None):
        if not ML_AVAILABLE:
            return self._get_random()
        X = np.stack([self._ratios_to_array(h['ratios']) for h in self.history])
        y = np.array([h['distance_to_target'] for h in self.history])
        X += np.random.normal(0, 1e-6, X.shape)
        gp = GaussianProcessRegressor(
            ConstantKernel(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-2, 1e2)),
            alpha=1e-4, normalize_y=True, n_restarts_optimizer=3)
        gp.fit(X, y)
        self.gp_model = gp
        f_best = y.min()

        def acq(x):
            m, s = gp.predict(x.reshape(1, -1), return_std=True)
            xi = 0.01  # Reduced exploration magnitude by 10x (was 0.1)
            z = (f_best - m - xi) / (s + 1e-9)
            return -(f_best - m - xi) * norm.cdf(z) - s * norm.pdf(z)

        starts = [np.random.uniform(0.1, 15.0, (N_PIG,)) for _ in range(6)]
        if seed is not None:
            starts.append(self._ratios_to_array(seed))

        best_x, best_v = None, np.inf
        for s0 in starts:
            res = minimize(acq, s0, method='L-BFGS-B',
                           bounds=[(0.05, 25.0)] * N_PIG)
            if res.success and res.fun < best_v:
                best_v, best_x = res.fun, res.x

        choice = best_x if best_x is not None else starts[0]
        return self._normalize(self._array_to_ratios(choice))

    def _estimate_hue_jacobian(self, k: int = 4) -> Optional[np.ndarray]:
        """
        Return approximate ∂hue/∂w  (shape 3) using the last k≳3 distinct moves.
        Least-squares fit:  Δhue ≈ J · Δw_coloured
        """
        if len(self.history) < 2:
            return None

        # build lists of Δw (R,Y,B only) and Δhue between successive trials
        dw, dh = [], []
        for h_prev, h_next in zip(self.history[-k-1:-1], self.history[-k:]):
            w_prev = self._ratios_to_array(h_prev["ratios"])[:3]
            w_next = self._ratios_to_array(h_next["ratios"])[:3]
            hue_prev = h_prev["measured_hue_deg"]
            hue_next = h_next["measured_hue_deg"]
            # skip near-zero moves
            if np.linalg.norm(w_next - w_prev) < 1e-3:
                continue
            dw.append(w_next - w_prev)
            dh.append(self._signed_hue_diff(hue_prev, hue_next))

        if len(dw) < 3:      # under-determined
            return None

        # LSQ:  minimise ||DW·J - dH||²
        DW = np.vstack(dw)             # (m,3)
        dH = np.array(dh)              # (m,)
        J, *_ = np.linalg.lstsq(DW, dH, rcond=None)
        return J          # shape (3,)

    def _hue_based_correction(self) -> Optional[Dict[str, float]]:
        if self.hue_target_deg is None or not self.history:
            return None

        J = self._estimate_hue_jacobian()
        if J is None:
            return None

        last = self.history[-1]
        w_old = self._ratios_to_array(last["ratios"])[:3]
        hue_old = last["measured_hue_deg"]
        d_hue   = self._signed_hue_diff(hue_old, self.hue_target_deg)

        # Solve   J·Δw  ≈  d_hue        (1×3 LS, bound –Δmax … +Δmax)
        try:
            Δw, *_ = np.linalg.lstsq(J.reshape(1, -1), np.array([d_hue]), rcond=None)
        except Exception:
            return None

        w_new_coloured = np.clip(w_old + Δw, 0.0, 25.0)
        return self._normalize(dict(zip(('red', 'yellow', 'blue'), w_new_coloured)))

    # ---------- misc helpers ----------
    def _get_random(self):
        coloured = {c: random.uniform(0.1, 10.0) for c in ('red', 'yellow', 'blue')}
        return self._normalize(coloured)

    # ---------- main decision ----------
    def recommend_next_ratios(self):
        N = len(self.history)

        if self.target_color is None:
            logger.warning("⚠️  No target color set – random ratios returned")
            return self._get_random()

        # --- phase 0 (first shot) ---
        if N == 0:
            r, g, b = self.target_color
            guess = {
                'red':    max(0.1, (r - g - b + 255) / 255.0 * 2.0),
                'yellow': max(0.1, (r + g - 2 * b + 255) / 255.0 * 1.5),
                'blue':   max(0.1, (b - r - g + 255) / 255.0 * 2.0)
            }
            return self._normalize(guess)

        # --- phase 1 (after the very first measurement) ---
        if N == 1:
            if self.hue_only_mode:
                step = self._hue_based_correction() or self._first_order_correction()
            else:
                step = self._first_order_correction()
            return step if step else self._get_random()

        # --- phase 2 (after two measurements) ---
        if N == 2:
            self._rough_scale_calibration()
            w_cal = self._inverse_weights()               # 3‑α rough calib
            if self.hue_only_mode:
                w_lin = self._hue_based_correction() or self._first_order_correction()
            else:
                w_lin = self._first_order_correction()        # deterministic step
            if w_cal is None and w_lin is None:
                return self._get_random()
            if w_cal is None:                 # fall back if inverse failed
                return w_lin
            if w_lin is None:
                return w_cal
            # Blend 70% linear‑step, 30% rough‑calib for added stability
            mix = {c: 0.7 * w_lin[c] + 0.3 * w_cal[c] for c in w_cal}
            return self._normalize(mix)

        # --- phase 3‑8/11 (hybrid) ---
        # Shorter hybrid phase when white-solvent locked (fewer effective parameters)
        hybrid_end = 8 if not self.allow_white_absorbance else 11
        if 3 <= N <= hybrid_end:
            self._fit_full_calibration()
            w_cal = self._inverse_weights()
            w_gp = self._gp_next(seed=w_cal)
            if w_cal is None:
                return w_gp
            # smoothly increase calibration weight from 0.25 → 0.85 over trials 3‑hybrid_end
            hybrid_range = hybrid_end - 3
            w_cal_w = 0.25 + 0.60 * (N - 3) / hybrid_range
            w_gp_w = 1.0 - w_cal_w
            mix = {c: w_cal_w * w_cal[c] + w_gp_w * w_gp[c] for c in w_cal}
            return self._normalize(mix)

        # --- phase ≥9/12 (calibration only) ---
        self._fit_full_calibration()
        res = self._inverse_weights()
        return res if res else self._get_random()

    # ---------- lightweight stats ----------
    def get_statistics(self):
        d = [h['distance_to_target'] for h in self.history]
        return {
            "total_attempts": len(self.history),
            "best_distance": min(d) if d else None,
            "current_distance": d[-1] if d else None,
            "std_error_absorb": self.std_error
        }

    def get_hue_series(self):
        return [h["measured_hue_deg"] for h in self.history if "measured_hue_deg" in h]

    def get_hue_error_series(self):
        return [h["hue_error_deg"] for h in self.history if "hue_error_deg" in h]

def _hue_gap_deg(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)

# ╔══════════════════════════════════════╗
# ║    H I D D E N   B O T T L E   M O D E L     ║
# ╚══════════════════════════════════════╝
class BottleModel(ColorOptimizer):
    """Fixed pigment matrix known only to the backend (for target sampling)."""
    def __init__(self, P_true: np.ndarray, allow_white_absorbance: bool = False, hue_only_mode: bool = True):
        super().__init__(allow_white_absorbance=allow_white_absorbance, hue_only_mode=hue_only_mode)
        self.P_est = P_true.copy()   # never changes

def load_ground_truth_calibration(allow_white_absorbance: bool = False):
    """
    Load ground truth calibration data from JSON files and construct the calibration matrix.
    
    Args:
        allow_white_absorbance: If False (default), white-solvent absorbance is locked to zero
                              assuming pure RGB(255,255,255) background. If True, allows
                              loading of actual white-solvent absorbance parameters.
    
    Returns:
        A 4x3 numpy array representing the true pigment absorbance matrix.
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
                P_loaded = np.array(matrix_data)
                
                # Ensure matrix is 4x3 (add white row if needed)
                if P_loaded.shape == (3, 3):
                    P_true = np.vstack([P_loaded, np.array([0.0, 0.0, 0.0])])  # Add white pigment row
                    logger.info("🎯 Loaded 3x3 ground truth matrix from calibration summary, extended to 4x3")
                elif P_loaded.shape == (4, 3):
                    P_true = P_loaded
                    logger.info("🎯 Loaded 4x3 ground truth matrix from calibration summary")
                else:
                    logger.warning("⚠️  Invalid matrix shape %s in calibration summary", P_loaded.shape)
                    P_true = None
                
                if P_true is not None:
                    logger.info("📊 Matrix shape: %s, mean absorbance: %.3f", P_true.shape, P_true.mean())
                    return P_true

            solutions_block = summary_data.get("calibration_summary", {}).get("solutions", {})
            for colour in ("red", "yellow", "blue"):
                if colour in solutions_block and "rgb" in solutions_block[colour]:
                    summary_rgb[colour] = solutions_block[colour]["rgb"]

        # Next try individual solution files which may contain coefficients or RGB values
        solutions = ["red", "yellow", "blue", "white"]  # Include white solution
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
        
        # Priority 1: use absorbance coefficients if all colored pigments are available
        # (white is optional and defaults to 0.0 if not provided)
        colored_coeffs = absorbance_coefficients[:3]  # red, yellow, blue
        white_coeff = absorbance_coefficients[3] if len(absorbance_coefficients) > 3 else None
        
        if all(c is not None for c in colored_coeffs):
            # Use white coefficient if available and allowed, otherwise default to 0.0
            if allow_white_absorbance and white_coeff is not None:
                white_absorbance = white_coeff
                logger.info("✅ Using white solution calibration: abs_coeff=%s", white_coeff)
            else:
                white_absorbance = 0.0
                if not allow_white_absorbance:
                    logger.info("🔒 White-solvent absorbance locked to zero (pure RGB(255,255,255) background assumed)")
                else:
                    logger.info("📝 White solution not found, using default zero absorbance")
            
            P_true = np.array([
                [absorbance_coefficients[0], 0.1, 0.08],
                [0.15, absorbance_coefficients[1], 0.1],
                [0.12, 0.15, absorbance_coefficients[2]],
                [white_absorbance, white_absorbance, white_absorbance]  # white solvent
            ])
            logger.info("🔧 Constructed ground truth matrix from individual files")
            logger.info("📊 Matrix:\n%s", P_true)
            return P_true

        # Priority 2: compute matrix from RGB measurements (including white if available)
        rgb_source = summary_rgb if len(summary_rgb) >= 3 else {
            c: rgb_colors[i] for i, c in enumerate(solutions[:3]) if rgb_colors[i] is not None
        }
        white_rgb = rgb_colors[3] if len(rgb_colors) > 3 and rgb_colors[3] is not None else None
        
        if len(rgb_source) == 3:
            # Ground truth calibration uses single solutions at total volume 10.0
            # For w = [10.0, 0.0, 0.0, 0.0], we want A = w @ P_est = rgb_to_absorb(red_rgb)
            # This means P_est[0,0] = rgb_to_absorb(red_rgb)[0] / 10.0, P_est[0,1] = rgb_to_absorb(red_rgb)[1] / 10.0, etc.
            # The matrix now includes white pigment as the 4th row
            
            # Calculate white row: use white solution data if available and allowed, 
            # otherwise lock to zero absorbance for pure RGB(255,255,255) background
            if allow_white_absorbance and white_rgb is not None:
                white_absorbance_row = ColorOptimizer._rgb_to_absorb(white_rgb) / 10.0
                logger.info("✅ Using white solution RGB measurement: RGB%s", white_rgb)
            else:
                # Lock white absorbance to zero for ideal white background RGB(255,255,255)
                white_absorbance_row = np.array([0.0, 0.0, 0.0])
                if not allow_white_absorbance:
                    logger.info("🔒 White-solvent absorbance locked to zero (pure RGB(255,255,255) background assumed)")
                else:
                    logger.info("📝 White solution file not found, using zero absorbance")
            
            P_true = np.array([
                ColorOptimizer._rgb_to_absorb(rgb_source["red"]) / 10.0,    # Row 0: red color's absorbance per unit volume
                ColorOptimizer._rgb_to_absorb(rgb_source["yellow"]) / 10.0, # Row 1: yellow color's absorbance per unit volume  
                ColorOptimizer._rgb_to_absorb(rgb_source["blue"]) / 10.0,   # Row 2: blue color's absorbance per unit volume
                white_absorbance_row                                        # Row 3: white solvent absorbance
            ])  # Shape: (4,3) where rows are pigments (including white), columns are RGB channels
            
            logger.info("🔧 Constructed ground truth matrix from RGB measurements (normalized for volume 10.0)")
            logger.info("📊 Matrix:\n%s", P_true)
            return P_true
            
    except Exception as e:
        logger.warning("⚠️  Error loading ground truth calibration: %s", e)
        logger.info("🔄 Falling back to random matrix generation")
    
    # Final fallback: generate random matrix (original behavior) - now 4x3 for 4 pigments
    np.random.seed(42)
    P_fallback = np.abs(np.random.normal(loc=0.3, scale=0.15, size=(3,3)))
    # Add white pigment row (locked to zero unless explicitly allowed)
    white_row = np.array([0.0, 0.0, 0.0]) if not allow_white_absorbance else np.abs(np.random.normal(loc=0.05, scale=0.02, size=3))
    P_fallback = np.vstack([P_fallback, white_row])
    
    if allow_white_absorbance:
        logger.info("🎲 Using random fallback matrix (4x3 with learnable white)")
    else:
        logger.info("🎲 Using random fallback matrix (4x3 with white locked to zero)")
    return P_fallback

# --- Load ground truth calibration and create bottle model ---

# Configuration: Set to True if you want to allow white-solvent absorbance learning
ALLOW_WHITE_ABSORBANCE = False  # Default: lock white to zero for pure RGB(255,255,255) background

_P_TRUE = load_ground_truth_calibration(allow_white_absorbance=ALLOW_WHITE_ABSORBANCE)
bottle_model = BottleModel(_P_TRUE, allow_white_absorbance=ALLOW_WHITE_ABSORBANCE, hue_only_mode=True)

# ╔══════════════════════════════════════╗
# ║     Target-colour helper functions     ║
# ╚══════════════════════════════════════╝
def _sample_reachable_rgb(P_est: np.ndarray,
                          max_total: float = 10.0) -> Tuple[Tuple[int,int,int], np.ndarray]:
    """Return (rgb8, weights) inside the reachable gamut of P_est.
    
    Generates normalized color ratios for 4 pigments that sum to max_total (default 10.0)
    to match the ColorOptimizer's normalization scheme and ground truth calibration.
    P_est is now (4,3) including white pigment.
    
    Enhanced with better sampling distribution to avoid bias toward yellow colors.
    """
    # Use uniform distribution instead of exponential to reduce bias
    # This gives more equal probability to all color combinations
    raw_ratios = np.random.uniform(0.1, 5.0, N_PIG)
    
    # Create ratio dictionary for all 4 pigments
    ratio_dict = {PIGMENTS[i]: raw_ratios[i] for i in range(N_PIG)}
    
    # Apply ColorOptimizer._normalize() logic exactly for 4-pigment system
    coloured = {k: v for k, v in ratio_dict.items() if k != "white"}
    s = sum(coloured.values()) or 1.0
    f = min(1.0, max_total / s)
    normalized_dict = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
    normalized_dict["white"] = max_total - sum(normalized_dict.values())
    
    # Enforce minimum solvent (white) volume
    if normalized_dict["white"] < 0.1:
        deficit = 0.1 - normalized_dict["white"]
        scale = (sum(normalized_dict.values()) - deficit) / sum(normalized_dict.values())
        for k in ('red', 'yellow', 'blue'):
            normalized_dict[k] *= scale
        normalized_dict["white"] = 0.1
    
    # Convert back to array for matrix operations (4 components)
    w = np.array([normalized_dict[p] for p in PIGMENTS])
    
    # Calculate absorbance and convert to RGB
    A = w @ P_est
    rgb_lin = 10 ** (-A)
    rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
    return rgb8, w

def generate_random_target_color(n_samples: int = 500) -> Tuple[int, int, int]:
    """
    Pick a reachable colour that obeys design rules with improved diversity.

    1.  Easy-to-reach  →  balanced pigment volumes  (difficulty ≤ MAX_DIFFICULTY)
    2.  Even coverage  →  maximise min. hue distance from recent targets
    3.  Equal usage    →  favour choice that balances cumulative R/Y/B usage
    4.  Not a primary  →  exclude hues too close to pure R, Y, B
    
    Enhanced to generate more diverse colors across the full spectrum.
    """
    global _hue_history, _cum_vol

    if bottle_model.P_est is None:                      # last-chance fallback
        rgb, _ = _sample_reachable_rgb(np.eye(4, 3))    # should never happen
        return rgb

    candidates = []  # Store all valid candidates
    
    # Generate candidates with multiple sampling strategies
    for strategy in range(3):
        for _ in range(n_samples // 3):
            if strategy == 0:
                # Strategy 1: Uniform distribution favoring diversity
                raw_ratios = np.random.uniform(0.1, 8.0, N_PIG)
            elif strategy == 1:
                # Strategy 2: Beta distribution for more balanced mixes
                raw_ratios = np.random.beta(1.5, 1.5, N_PIG) * 6.0 + 0.2
            else:
                # Strategy 3: Log-normal for occasional extreme colors
                raw_ratios = np.random.lognormal(0.5, 0.8, N_PIG)
                raw_ratios = np.clip(raw_ratios, 0.1, 12.0)
            
            # Create ratio dictionary for all 4 pigments
            ratio_dict = {PIGMENTS[i]: raw_ratios[i] for i in range(N_PIG)}
            
            # Apply ColorOptimizer._normalize() logic
            coloured = {k: v for k, v in ratio_dict.items() if k != "white"}
            s = sum(coloured.values()) or 1.0
            f = min(1.0, 10.0 / s)
            normalized_dict = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
            normalized_dict["white"] = max(0.1, 10.0 - sum(normalized_dict.values()))
            
            # Enforce minimum solvent
            if normalized_dict["white"] < 0.1:
                deficit = 0.1 - normalized_dict["white"]
                scale = (sum(normalized_dict.values()) - deficit) / sum(normalized_dict.values())
                for k in ('red', 'yellow', 'blue'):
                    normalized_dict[k] *= scale
                normalized_dict["white"] = 0.1
            
            # Convert to array and calculate RGB
            w = np.array([normalized_dict[p] for p in PIGMENTS])
            A = w @ bottle_model.P_est
            rgb_lin = 10 ** (-A)
            rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
            hue = ColorOptimizer._hue_deg(rgb8)
            
            # Apply filters
            colored = w[:3]
            difficulty = colored.max() / colored.sum()
            if difficulty > MAX_DIFFICULTY:
                continue
                
            # More lenient primary exclusion
            if min(_hue_gap_deg(hue, p) for p in PRIMARY_HUES) < HUE_EXCLUSION:
                continue
            
            # Calculate hue spacing
            if _hue_history:
                hue_gap = min(_hue_gap_deg(hue, h) for h in _hue_history)
            else:
                hue_gap = 180
            
            # Calculate pigment balance
            projected_totals = _cum_vol + colored
            imbalance = np.std(projected_totals / (projected_totals.sum() + 1e-10))
            
            # Store candidate with scoring
            candidates.append({
                'rgb': rgb8,
                'vols': w,
                'hue': hue,
                'difficulty': difficulty,
                'hue_gap': hue_gap,
                'imbalance': imbalance,
                'strategy': strategy
            })
    
    if not candidates:
        # Ultimate fallback: generate a simple color without strict filtering
        logger.warning("⚠️ No candidates passed filters, generating fallback color")
        raw_ratios = np.random.uniform(0.5, 3.0, N_PIG)
        ratio_dict = {PIGMENTS[i]: raw_ratios[i] for i in range(N_PIG)}
        coloured = {k: v for k, v in ratio_dict.items() if k != "white"}
        s = sum(coloured.values()) or 1.0
        f = min(1.0, 10.0 / s)
        normalized_dict = {k: max(0.1, coloured.get(k, 0.0) * f) for k in ('red', 'yellow', 'blue')}
        normalized_dict["white"] = max(0.1, 10.0 - sum(normalized_dict.values()))
        w = np.array([normalized_dict[p] for p in PIGMENTS])
        A = w @ bottle_model.P_est
        rgb_lin = 10 ** (-A)
        rgb8 = tuple(int(x) for x in (rgb_lin ** (1/2.2) * 255).clip(0,255))
        hue = ColorOptimizer._hue_deg(rgb8)
        _hue_history.append(hue)
        _cum_vol[:3] += w[:3]
        return rgb8
    
    # Multi-objective scoring with emphasis on diversity
    def score_candidate(c):
        # Normalize scores to 0-1 range
        difficulty_score = 1.0 - (c['difficulty'] / MAX_DIFFICULTY)  # Higher is better (easier)
        hue_gap_score = min(c['hue_gap'] / 180.0, 1.0)  # Higher is better (more diverse)
        balance_score = 1.0 / (1.0 + c['imbalance'])  # Higher is better (more balanced)
        
        # Weight heavily toward hue diversity to solve the yellowish bias
        return 0.1 * difficulty_score + 0.7 * hue_gap_score + 0.2 * balance_score
    
    # Sort by composite score and pick the best
    candidates.sort(key=score_candidate, reverse=True)
    best = candidates[0]
    
    # Log the selection for debugging
    logger.info(f"🎨 Selected color strategy {best['strategy']}: hue={best['hue']:.1f}°, "
                f"gap={best['hue_gap']:.1f}°, difficulty={best['difficulty']:.3f}")
    
    # Update running statistics
    _hue_history.append(best['hue'])
    _cum_vol[:3] += best['vols'][:3]
    
    return best['rgb']

# ╔══════════════════════════════════════╗
# ║     FastAPI   +  endpoints (UNCHANGED)    ║
# ╚══════════════════════════════════════╝
color_optimizer = ColorOptimizer(allow_white_absorbance=ALLOW_WHITE_ABSORBANCE, hue_only_mode=True)

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
    color_optimizer.history.clear()
    color_optimizer.gp_model = None
    _hue_history.clear()
    _cum_vol[:] = 0
    return {"status": "success", "message": "history reset"}

@app.get("/api/color-space-data")
async def api_color_space_data():
    """Provide perceptual color space data for CAM02-UCS visualization."""
    if not color_optimizer.target_color or len(color_optimizer.history) == 0:
        return {"status": "success", "data": {"available": False}}
    
    def rgb_to_lab(rgb):
        """Convert RGB to LAB color space using simplified conversion."""
        # Normalize RGB to 0-1
        r, g, b = [x / 255.0 for x in rgb]
        
        # Convert to XYZ (simplified sRGB to XYZ conversion)
        # Apply gamma correction
        r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
        g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
        b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92
        
        # Convert to XYZ using sRGB matrix
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        # Convert XYZ to LAB (using D65 illuminant)
        xn, yn, zn = 0.95047, 1.00000, 1.08883  # D65 reference white
        x, y, z = x / xn, y / yn, z / zn
        
        fx = x ** (1/3) if x > 0.008856 else (7.787 * x + 16/116)
        fy = y ** (1/3) if y > 0.008856 else (7.787 * y + 16/116)
        fz = z ** (1/3) if z > 0.008856 else (7.787 * z + 16/116)
        
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        
        return [L, a, b]
    
    try:
        # Convert target color to LAB
        target_lab = rgb_to_lab(color_optimizer.target_color)
        
        # Convert optimization history to LAB
        trail_data = []
        for entry in color_optimizer.history:
            measured_rgb = entry['measured_rgb']
            lab_coords = rgb_to_lab(measured_rgb)
            trail_data.append({
                'rgb': measured_rgb,
                'lab': lab_coords
            })
        
        return {
            "status": "success",
            "data": {
                "available": True,
                "target": {
                    "rgb": list(color_optimizer.target_color),
                    "lab": target_lab
                },
                "trail": trail_data,
                "axis_labels": {
                    "x": "a* (緑 ← → 赤)",
                    "y": "b* (青 ← → 黄)",
                    "title": "CAM02-UCS 色空間での最適化軌跡"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error generating color space data: {e}")
        return {"status": "success", "data": {"available": False}}

@app.get("/api/hue-visual-data")
async def api_hue_visual_data():
    if color_optimizer.hue_target_deg is None or len(color_optimizer.history) == 0:
        return {"status": "success", "available": False}
    return {
        "status": "success",
        "available": True,
        "target_hue_deg": color_optimizer.hue_target_deg,
        "hue_series_deg": color_optimizer.get_hue_series(),
        "hue_error_deg": color_optimizer.get_hue_error_series(),
        "rgb_series": [h["measured_rgb"] for h in color_optimizer.history]
    }

# ╔══════════════════════════════════════╗
# ║        Robot & Vision Proxy Endpoints        ║
# ╚══════════════════════════════════════╝

@app.api_route("/robot/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_robot_service(request: Request, path: str):
    """Proxy requests to the robot service."""
    url = f"{ROBOT_SERVICE_URL}/robot/{path}"
    logger.info(f"🤖 Proxying {request.method} request to: {url}")

    # Forward query parameters
    if request.query_params:
        url += "?" + str(request.query_params)

    # Use longer timeout for robot operations (6+ minutes for laboratory procedures)
    async with httpx.AsyncClient(timeout=1000.0) as client:
        try:
            # Get request body if present
            body = await request.body() if request.method in ["POST", "PUT"] else None
            
            # Process washing bottle calibration for color ratio requests
            processed_body = body
            if body and ENABLE_WASHING_BOTTLE_CALIBRATION and request.method in ["POST", "PUT"]:
                try:
                    body_data = json.loads(body.decode())
                    
                    # Check if the request contains color ratios
                    if "ratios" in body_data or "color_ratios" in body_data:
                        ratios = body_data.get("ratios") or body_data.get("color_ratios")
                        
                        # Convert ratios to durations using washing bottle calibration
                        durations = colour_ratios_to_durations(ratios, total_mL=10.0)
                        
                        # Add durations to the request payload
                        body_data["washing_bottle_durations"] = durations
                        processed_body = json.dumps(body_data).encode()
                        
                        logger.info(f"🧪 Applied washing bottle calibration:")
                        logger.info(f"   Original ratios: {ratios}")
                        logger.info(f"   Calculated durations: {durations}")
                        
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.debug(f"Request body not processed for washing bottle calibration: {e}")
                    processed_body = body
            
            if processed_body:
                logger.info(f"Request body: {processed_body.decode()}")

            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=processed_body
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

@app.api_route("/vision/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_vision_service(request: Request, path: str):
    """Proxy requests to the vision service."""
    url = f"{VISION_SERVICE_URL}/{path}"
    logger.info(f"👁️ Proxying {request.method} request to: {url}")

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
        "washing_bottle_calibration": {
            "enabled": ENABLE_WASHING_BOTTLE_CALIBRATION,
            "calibration_loaded": bool(_WB_FITS),
            "available_colors": list(_WB_FITS.keys()) if _WB_FITS else []
        },
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
    rgb0 = generate_random_target_color()
    color_optimizer.set_target_color(rgb0)
    logger.info("🎯 Initial target RGB%s", rgb0)
    logger.info("🔧 White-solvent absorbance mode: %s", 
                "learnable" if ALLOW_WHITE_ABSORBANCE else "locked to zero")
    logger.info("🧪 Washing bottle calibration: %s", 
                "enabled" if ENABLE_WASHING_BOTTLE_CALIBRATION else "disabled")
    if ENABLE_WASHING_BOTTLE_CALIBRATION and _WB_FITS:
        logger.info("📊 Loaded calibration for colors: %s", list(_WB_FITS.keys()))
    uvicorn.run(app, host="0.0.0.0", port=3000)
