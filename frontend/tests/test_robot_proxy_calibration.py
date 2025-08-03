#!/usr/bin/env python3
"""
Test robot proxy integration with washing bottle calibration.
"""

import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import httpx
    from fastapi.testclient import TestClient
    from fastapi import Request
    
    # Import the main module
    from main import (
        app, 
        proxy_robot_service,
        colour_ratios_to_durations,
        ENABLE_WASHING_BOTTLE_CALIBRATION,
        _WB_FITS
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    IMPORTS_AVAILABLE = False

class TestRobotProxyIntegration:
    """Test robot proxy integration with washing bottle calibration."""
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_robot_proxy_without_calibration(self):
        """Test robot proxy when calibration is disabled."""
        with patch('main.ENABLE_WASHING_BOTTLE_CALIBRATION', False):
            client = TestClient(app)
            
            # Test payload without washing bottle calibration
            test_payload = {
                "ratios": {
                    "red": 2.0,
                    "yellow": 3.0,
                    "blue": 1.0,
                    "white": 4.0
                }
            }
            
            # Mock the robot service response
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "success"}
                mock_response.headers.get.return_value = "application/json"
                
                mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
                
                # Make request through proxy
                response = client.post("/robot/test-endpoint", json=test_payload)
                
                # Verify response
                assert response.status_code == 200
                
                # Verify that the original payload was sent (no calibration applied)
                call_args = mock_client.return_value.__aenter__.return_value.request.call_args
                assert call_args is not None
                
                # The content should be the original payload
                sent_content = call_args[1]['content']
                sent_data = json.loads(sent_content.decode())
                assert "washing_bottle_durations" not in sent_data
                assert sent_data["ratios"] == test_payload["ratios"]
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_robot_proxy_with_calibration(self):
        """Test robot proxy when calibration is enabled."""
        if not _WB_FITS:
            pytest.skip("Washing bottle fits not loaded")
        
        with patch('main.ENABLE_WASHING_BOTTLE_CALIBRATION', True):
            client = TestClient(app)
            
            # Test payload with color ratios
            test_payload = {
                "ratios": {
                    "red": 2.0,
                    "yellow": 3.0,
                    "blue": 1.0,
                    "white": 4.0
                }
            }
            
            # Mock the robot service response
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "success"}
                mock_response.headers.get.return_value = "application/json"
                
                mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
                
                # Make request through proxy
                response = client.post("/robot/test-endpoint", json=test_payload)
                
                # Verify response
                assert response.status_code == 200
                
                # Verify that calibration was applied
                call_args = mock_client.return_value.__aenter__.return_value.request.call_args
                assert call_args is not None
                
                # The content should include washing bottle durations
                sent_content = call_args[1]['content']
                sent_data = json.loads(sent_content.decode())
                
                assert "washing_bottle_durations" in sent_data, "Washing bottle durations should be added"
                assert "ratios" in sent_data, "Original ratios should be preserved"
                
                durations = sent_data["washing_bottle_durations"]
                assert isinstance(durations, dict), "Durations should be a dictionary"
                assert "red" in durations, "Red duration should be present"
                assert "yellow" in durations, "Yellow duration should be present"
                assert "blue" in durations, "Blue duration should be present"
                
                # Verify all durations are positive numbers
                for color, duration in durations.items():
                    assert isinstance(duration, (int, float)), f"Duration for {color} should be numeric"
                    assert duration > 0, f"Duration for {color} should be positive"
                
                print(f"✅ Original ratios: {test_payload['ratios']}")
                print(f"✅ Calculated durations: {durations}")
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_robot_proxy_with_color_ratios_key(self):
        """Test robot proxy with 'color_ratios' key instead of 'ratios'."""
        if not _WB_FITS:
            pytest.skip("Washing bottle fits not loaded")
        
        with patch('main.ENABLE_WASHING_BOTTLE_CALIBRATION', True):
            client = TestClient(app)
            
            # Test payload with color_ratios key
            test_payload = {
                "color_ratios": {
                    "red": 1.5,
                    "yellow": 2.5,
                    "blue": 2.0,
                    "white": 4.0
                }
            }
            
            # Mock the robot service response
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "success"}
                mock_response.headers.get.return_value = "application/json"
                
                mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
                
                # Make request through proxy
                response = client.post("/robot/test-endpoint", json=test_payload)
                
                # Verify response
                assert response.status_code == 200
                
                # Verify that calibration was applied
                call_args = mock_client.return_value.__aenter__.return_value.request.call_args
                sent_content = call_args[1]['content']
                sent_data = json.loads(sent_content.decode())
                
                assert "washing_bottle_durations" in sent_data, "Washing bottle durations should be added"
                durations = sent_data["washing_bottle_durations"]
                
                # Verify all expected colors have durations
                for color in ["red", "yellow", "blue"]:
                    assert color in durations, f"Duration for {color} should be present"
                    assert durations[color] > 0, f"Duration for {color} should be positive"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_robot_proxy_without_ratios(self):
        """Test robot proxy with payload that doesn't contain ratios."""
        with patch('main.ENABLE_WASHING_BOTTLE_CALIBRATION', True):
            client = TestClient(app)
            
            # Test payload without ratios
            test_payload = {
                "command": "status",
                "parameters": {"check_health": True}
            }
            
            # Mock the robot service response
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "healthy"}
                mock_response.headers.get.return_value = "application/json"
                
                mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
                
                # Make request through proxy
                response = client.post("/robot/status", json=test_payload)
                
                # Verify response
                assert response.status_code == 200
                
                # Verify that no calibration was applied
                call_args = mock_client.return_value.__aenter__.return_value.request.call_args
                sent_content = call_args[1]['content']
                sent_data = json.loads(sent_content.decode())
                
                assert "washing_bottle_durations" not in sent_data, "No durations should be added for non-ratio requests"
                assert sent_data == test_payload, "Payload should be unchanged"
    
    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_status_endpoint(self):
        """Test that status endpoint includes washing bottle calibration info."""
        client = TestClient(app)
        
        response = client.get("/status")
        assert response.status_code == 200
        
        status_data = response.json()
        assert "washing_bottle_calibration" in status_data, "Status should include washing bottle calibration info"
        
        calib_info = status_data["washing_bottle_calibration"]
        assert "enabled" in calib_info, "Should report if calibration is enabled"
        assert "calibration_loaded" in calib_info, "Should report if calibration is loaded"
        assert "available_colors" in calib_info, "Should list available colors"
        
        print(f"✅ Washing bottle calibration status: {calib_info}")

def run_robot_proxy_tests():
    """Run all robot proxy integration tests."""
    print("🤖 Running Robot Proxy Integration Tests")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("❌ Cannot run tests - required modules not available")
        return False
    
    test_suite = TestRobotProxyIntegration()
    
    try:
        # Run all tests
        test_suite.test_robot_proxy_without_calibration()
        test_suite.test_robot_proxy_with_calibration()
        test_suite.test_robot_proxy_with_color_ratios_key()
        test_suite.test_robot_proxy_without_ratios()
        test_suite.test_status_endpoint()
        
        print("\n🎉 All robot proxy integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_robot_proxy_tests()
    sys.exit(0 if success else 1)
