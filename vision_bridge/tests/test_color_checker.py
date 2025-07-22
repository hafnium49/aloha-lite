import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from unittest.mock import patch
import importlib


def load_app():
    with patch('prometheus_client.start_http_server', lambda *a, **k: None):
        mod = importlib.import_module('vision_bridge.main')
    return mod.app


def test_circle_colour_sample():
    """Test the new circle-colour endpoint with a sample image."""
    app = load_app()
    client = TestClient(app)
    with open('vision_bridge/samples/ColorCheckerClassic_24patch_sRGB.png', 'rb') as f:
        resp = client.post('/circle-colour', files={'file': ('img.png', f, 'image/png')})
    
    # Should succeed with 200 or fail with 422 if no circle is detected
    assert resp.status_code in [200, 422]
    
    if resp.status_code == 200:
        data = resp.json()
        assert 'circle' in data
        assert 'mean_color' in data
        assert 'center' in data['circle']
        assert 'radius' in data['circle']
        assert 'bgr' in data['mean_color']
        assert 'rgb' in data['mean_color'] 
        assert 'hex' in data['mean_color']

