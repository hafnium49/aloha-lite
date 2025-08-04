#!/usr/bin/env python3
"""
utilities/washing_bottle_calibration_fitter.py

Fits a third‑order (cubic) polynomial to washing‑bottle calibration data
(duration_s → weight_g) and stores the coefficients and their standard
errors in a summary JSON file.

By default, the polynomial is constrained to pass through the origin (0,0)
since zero squeeze duration should result in zero dispensed weight. This
constraint can be disabled with the --no-zero-intercept flag.

Usage
-----
    # Default: Force polynomial through origin (physically realistic)
    python utilities/washing_bottle_calibration_fitter.py \
        frontend/washing_bottle_calibration/washing_bottle_blue_calibration.json

    # Optional: Allow non-zero y-intercept (unconstrained fit)
    python utilities/washing_bottle_calibration_fitter.py \
        frontend/washing_bottle_calibration/washing_bottle_blue_calibration.json \
        --no-zero-intercept

The script will create / update
`frontend/washing_bottle_calibration/washing_bottle_calibration_summary.json`.
If the summary file already contains an entry for the same solution
("red", "yellow", or "blue"), that entry will be replaced with the new
fit results.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

import numpy as np

SUMMARY_PATH = Path("frontend/washing_bottle_calibration/"
                    "washing_bottle_calibration_summary.json")


def _load_measurements(calib_path: Path):
    """Return durations and weights as NumPy arrays from a calibration file."""
    with calib_path.open("r", encoding="utf-8") as fp:
        calib = json.load(fp)

    measurements = calib.get("measurements", [])
    if not measurements:
        raise ValueError(f"No 'measurements' found in {calib_path}")

    x = np.array([m["duration_s"] for m in measurements], dtype=float)
    y = np.array([m["weight_g"] for m in measurements], dtype=float)
    return calib, x, y


def _fit_cubic(x: np.ndarray, y: np.ndarray, force_zero_intercept: bool = True):
    """
    Fit y = a·x³ + b·x² + c·x + d and return coeffs and stderr arrays.
    
    Args:
        x: Duration values (seconds)
        y: Weight values (grams)
        force_zero_intercept: If True (default), force the polynomial to pass through (0,0)
                             by setting d=0 and fitting y = a·x³ + b·x² + c·x
    
    Returns:
        coeffs: Polynomial coefficients [a, b, c, d] (highest power first)
        stderr: Standard errors for each coefficient
    """
    if force_zero_intercept:
        # Fit y = a·x³ + b·x² + c·x (no constant term, forces through origin)
        # Create design matrix for cubic without constant term
        X = np.column_stack([x**3, x**2, x])  # [x³, x², x]
        
        # Use least squares to solve X @ coeffs_reduced = y
        coeffs_reduced, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
        
        # Calculate covariance matrix manually for reduced model
        if len(residuals) > 0 and len(x) > X.shape[1]:
            # Calculate residual variance
            mse = residuals[0] / (len(x) - X.shape[1])
            # Covariance matrix: mse * (X^T X)^-1
            try:
                cov_reduced = mse * np.linalg.inv(X.T @ X)
                stderr_reduced = np.sqrt(np.diag(cov_reduced))
            except np.linalg.LinAlgError:
                # Fallback if matrix is singular
                stderr_reduced = np.zeros(len(coeffs_reduced))
        else:
            stderr_reduced = np.zeros(len(coeffs_reduced))
        
        # Reconstruct full coefficient array [a, b, c, d] with d=0
        coeffs = np.append(coeffs_reduced, 0.0)  # [a, b, c, 0]
        stderr = np.append(stderr_reduced, 0.0)  # [stderr_a, stderr_b, stderr_c, 0]
        
    else:
        # Original unconstrained cubic fit
        coeffs, cov = np.polyfit(x, y, deg=3, cov=True)
        stderr = np.sqrt(np.diag(cov))
    
    return coeffs, stderr


def _update_summary(result: dict):
    """Append/replace a single calibration fit result in the summary file."""
    summary: List[dict] = []
    if SUMMARY_PATH.exists():
        try:
            with SUMMARY_PATH.open("r", encoding="utf-8") as fp:
                summary = json.load(fp)
        except json.JSONDecodeError:
            # Corrupt or empty file → overwrite with new summary list
            summary = []

    # Drop any existing entry for the same solution (if key exists)
    solution = result.get("solution")
    summary = [entry for entry in summary if entry.get("solution") != solution]
    summary.append(result)

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2)



def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.exit(
            "Usage: python utilities/washing_bottle_calibration_fitter.py "
            "<calibration_json> [--no-zero-intercept]\n"
            "  --no-zero-intercept: Allow non-zero y-intercept (default: force through origin)"
        )

    calib_path = Path(sys.argv[1])
    if not calib_path.is_file():
        sys.exit(f"Calibration file not found: {calib_path}")
    
    # Check for optional flag to disable zero intercept constraint
    force_zero_intercept = True
    if len(sys.argv) == 3:
        if sys.argv[2] == "--no-zero-intercept":
            force_zero_intercept = False
        else:
            sys.exit(f"Unknown argument: {sys.argv[2]}")

    try:
        calib, x, y = _load_measurements(calib_path)
        coeffs, stderr = _fit_cubic(x, y, force_zero_intercept=force_zero_intercept)
    except Exception as exc:
        sys.exit(f"Error processing {calib_path}: {exc}")

    result = {
        "solution": calib.get("solution", calib_path.stem.split("_")[-2]),
        "source_file": str(calib_path),
        "poly_order": 3,
        "coefficients": coeffs.tolist(),  # [a, b, c, d]
        "std_errors": stderr.tolist(),    # same order as coefficients
        "zero_intercept_forced": force_zero_intercept,  # Record the constraint used
    }

    _update_summary(result)
    
    # Print fitting information
    intercept_info = "forced through origin (0,0)" if force_zero_intercept else "unconstrained"
    print(f"Fitted cubic polynomial ({intercept_info}):")
    print(f"  y = {coeffs[0]:.6e}·x³ + {coeffs[1]:.6e}·x² + {coeffs[2]:.6e}·x + {coeffs[3]:.6e}")
    print(f"Summary updated → {SUMMARY_PATH}")
    
    # Validate the fit makes physical sense
    if force_zero_intercept:
        # Check that small durations give reasonable weights
        test_duration = 0.1  # 0.1 seconds
        test_weight = coeffs[0] * test_duration**3 + coeffs[1] * test_duration**2 + coeffs[2] * test_duration
        print(f"Validation: {test_duration}s duration → {test_weight:.4f}g weight")
    else:
        print(f"Validation: y-intercept = {coeffs[3]:.4f}g (unconstrained fit)")


if __name__ == "__main__":
    main()
