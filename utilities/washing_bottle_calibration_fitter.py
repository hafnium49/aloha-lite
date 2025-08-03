#!/usr/bin/env python3
"""
utilities/washing_bottle_calibration_fitter.py

Fits a third‑order (cubic) polynomial to washing‑bottle calibration data
(duration_s → weight_g) and stores the coefficients and their standard
errors in a summary JSON file.

Usage
-----
    python utilities/washing_bottle_calibration_fitter.py \
        frontend/washing_bottle_calibration/washing_bottle_blue_calibration.json

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


def _fit_cubic(x: np.ndarray, y: np.ndarray):
    """Fit y = a·x³ + b·x² + c·x + d and return coeffs and stderr arrays."""
    # numpy.polyfit returns coeffs highest power first; cov=True gives covariance
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
    if len(sys.argv) != 2:
        sys.exit(
            "Usage: python utilities/washing_bottle_calibration_fitter.py "
            "<calibration_json>"
        )

    calib_path = Path(sys.argv[1])
    if not calib_path.is_file():
        sys.exit(f"Calibration file not found: {calib_path}")

    try:
        calib, x, y = _load_measurements(calib_path)
        coeffs, stderr = _fit_cubic(x, y)
    except Exception as exc:
        sys.exit(f"Error processing {calib_path}: {exc}")

    result = {
        "solution": calib.get("solution", calib_path.stem.split("_")[-2]),
        "source_file": str(calib_path),
        "poly_order": 3,
        "coefficients": coeffs.tolist(),  # [a, b, c, d]
        "std_errors": stderr.tolist(),    # same order as coefficients
    }

    _update_summary(result)
    print(f"Summary updated → {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
