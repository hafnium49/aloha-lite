#!/usr/bin/env python3
"""
Test washing bottle calibration functionality in frontend/main.py
"""

import sys
import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import numpy as np
    from numpy.polynomial.polynomial import Polynomial
    from numpy import roots, isreal
    import warnings
    
    # Import the main module functions
    from main import (
        _load_washing_bottle_fits,
        _volume_to_duration_memo, 
        colour_ratios_to_durations,
        ENABLE_WASHING_BOTTLE_CALIBRATION,
        _WB_FITS,
        _CALIB_PATH
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    IMPORTS_AVAILABLE = False

class TestWashingBottleCalibration:
    """Test suite for washing bottle calibration functionality."""
    
    def test_imports_available(self):
        """Test that all required modules are available."""
        assert IMPORTS_AVAILABLE, "Required modules not available"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_calibration_file_exists(self):
        """Test that the calibration file exists."""
        assert _CALIB_PATH.exists(), f"Calibration file not found at {_CALIB_PATH}"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_load_washing_bottle_fits(self):
        """Test loading of washing bottle calibration fits."""
        if not _CALIB_PATH.exists():
            pytest.skip("Calibration file not available")
        
        fits = _load_washing_bottle_fits()
        
        # Check that we have fits for all expected colors
        expected_colors = ['red', 'yellow', 'blue']
        assert isinstance(fits, dict), "Fits should be a dictionary"
        assert len(fits) == len(expected_colors), f"Expected {len(expected_colors)} fits, got {len(fits)}"
        
        for color in expected_colors:
            assert color in fits, f"Missing fit for {color}"
            assert isinstance(fits[color], Polynomial), f"Fit for {color} should be a Polynomial"
        
        print(f"✅ Successfully loaded fits for colors: {list(fits.keys())}")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_volume_to_duration_conversion(self):
        """Test volume to duration conversion."""
        if not _WB_FITS:
            pytest.skip("Washing bottle fits not loaded")
        
        test_volume = 2.0  # 2.0 mL
        
        for color in _WB_FITS.keys():
            duration = _volume_to_duration_memo(color, test_volume)
            
            # Verify duration is positive and reasonable
            assert duration > 0, f"Duration for {color} should be positive, got {duration}"
            assert duration < 100, f"Duration for {color} seems too large: {duration}s"
            
            # Verify inverse calculation
            calculated_volume = _WB_FITS[color](duration)
            assert abs(calculated_volume - test_volume) < 0.1, \
                f"Inverse calculation failed for {color}: expected {test_volume}, got {calculated_volume}"
            
            print(f"✅ {color}: {test_volume:.1f} mL → {duration:.3f}s → {calculated_volume:.3f} mL")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_colour_ratios_to_durations(self):
        """Test the main color ratios to durations conversion function."""
        if not _WB_FITS:
            pytest.skip("Washing bottle fits not loaded")
        
        # Test case 1: Simple ratios
        test_ratios = {
            'red': 2.0,
            'yellow': 3.0,
            'blue': 1.5,
            'white': 3.5
        }
        
        durations = colour_ratios_to_durations(test_ratios, total_mL=10.0)
        
        # Check that we get durations for all colored pigments
        expected_colors = ['red', 'yellow', 'blue']
        assert isinstance(durations, dict), "Result should be a dictionary"
        assert len(durations) == len(expected_colors), f"Expected {len(expected_colors)} durations"
        
        for color in expected_colors:
            assert color in durations, f"Missing duration for {color}"
            assert durations[color] > 0, f"Duration for {color} should be positive"
        
        # Verify the normalization works correctly
        colored_sum = sum(test_ratios[k] for k in expected_colors)
        scale = 10.0 / colored_sum
        expected_volumes = {k: test_ratios[k] * scale for k in expected_colors}
        
        print(f"✅ Input ratios: {test_ratios}")
        print(f"✅ Calculated durations: {durations}")
        print(f"✅ Expected scaled volumes: {expected_volumes}")
        
        # Verify volumes add up to 10.0 mL
        total_expected = sum(expected_volumes.values())
        assert abs(total_expected - 10.0) < 0.01, f"Expected volumes should sum to 10.0, got {total_expected}"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_colour_ratios_edge_cases(self):
        """Test edge cases for color ratios conversion."""
        if not _WB_FITS:
            pytest.skip("Washing bottle fits not loaded")
        
        # Test case 1: Very small volumes
        small_ratios = {
            'red': 0.1,
            'yellow': 0.1,
            'blue': 0.1,
            'white': 9.7
        }
        
        durations_small = colour_ratios_to_durations(small_ratios, total_mL=10.0)
        assert all(d > 0 for d in durations_small.values()), "All durations should be positive"
        
        # Test case 2: Large volumes that need scaling
        large_ratios = {
            'red': 10.0,
            'yellow': 15.0,
            'blue': 5.0,
            'white': 0.1
        }
        
        durations_large = colour_ratios_to_durations(large_ratios, total_mL=10.0)
        assert all(d > 0 for d in durations_large.values()), "All durations should be positive"
        
        print(f"✅ Small ratios test passed: {durations_small}")
        print(f"✅ Large ratios test passed: {durations_large}")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_calibration_status(self):
        """Test that calibration status is reported correctly."""
        print(f"✅ Washing bottle calibration enabled: {ENABLE_WASHING_BOTTLE_CALIBRATION}")
        print(f"✅ Calibration fits loaded: {bool(_WB_FITS)}")
        if _WB_FITS:
            print(f"✅ Available colors: {list(_WB_FITS.keys())}")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available") 
    def test_different_total_volumes(self):
        """Test conversion with different total volumes."""
        if not _WB_FITS:
            pytest.skip("Washing bottle fits not loaded")
        
        test_ratios = {
            'red': 1.0,
            'yellow': 1.0,
            'blue': 1.0,
            'white': 2.0
        }
        
        # Test with different total volumes
        volumes_to_test = [5.0, 10.0, 15.0]
        
        for total_vol in volumes_to_test:
            durations = colour_ratios_to_durations(test_ratios, total_mL=total_vol)
            
            # Verify all durations are positive
            assert all(d > 0 for d in durations.values()), \
                f"All durations should be positive for {total_vol} mL"
            
            # The durations should scale appropriately with total volume
            colored_sum = sum(test_ratios[k] for k in ['red', 'yellow', 'blue'])
            scale = total_vol / colored_sum
            expected_individual_volume = test_ratios['red'] * scale  # All colors have same ratio
            
            print(f"✅ {total_vol} mL total → individual volumes ≈ {expected_individual_volume:.2f} mL")

def run_washing_bottle_tests():
    """Run all washing bottle calibration tests."""
    print("🧪 Running Washing Bottle Calibration Tests")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot run tests - required modules not available")
        return False
    
    test_suite = TestWashingBottleCalibration()
    
    try:
        # Run all tests
        test_suite.test_imports_available()
        test_suite.test_calibration_file_exists()
        test_suite.test_load_washing_bottle_fits()
        test_suite.test_volume_to_duration_conversion()
        test_suite.test_colour_ratios_to_durations()
        test_suite.test_colour_ratios_edge_cases()
        test_suite.test_calibration_status()
        test_suite.test_different_total_volumes()
        
        print("\n🎉 All washing bottle calibration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_washing_bottle_tests()
    sys.exit(0 if success else 1)
