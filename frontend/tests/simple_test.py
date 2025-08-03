#!/usr/bin/env python3
"""
Simple Test Runner for Frontend Integration

This creates a simple test environment to validate the frontend/index.html 
beaker analysis integration without needing the full robot service.
"""

import json
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from datetime import datetime

class SimpleTestHandler(BaseHTTPRequestHandler):
    FRONTEND_DIR = "/home/hafnium/aloha-lite/frontend"
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_frontend()
        elif self.path.startswith('/robot/') and '/status' in self.path:
            self.mock_status_response()
        elif self.path.startswith('/robot/') and '/beaker-analysis' in self.path:
            self.mock_beaker_analysis()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/robot/dispense' or self.path == '/robot/execute':
            self.mock_execute_response()
        else:
            self.send_error(404)
    
    def serve_frontend(self):
        try:
            with open(f"{self.FRONTEND_DIR}/index.html", 'r') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, f"Error serving frontend: {e}")
    
    def mock_execute_response(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'cmd_id': 'test_123',
            'status': 'accepted'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def mock_status_response(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'completed',
            'message': 'Laboratory procedure completed successfully',
            'beaker_analysis_results': {
                'timestamp': datetime.now().isoformat(),
                'colors_detected': ['red', 'blue', 'yellow'],
                'dominant_color': 'purple',
                'color_percentages': {
                    'red': 35.2,
                    'blue': 28.7,
                    'yellow': 15.3,
                    'purple': 20.8
                },
                'analysis_confidence': 0.94,
                'beaker_position': {'x': 0.15, 'y': 0.22, 'z': 0.08},
                'volume_estimate': '45ml',
                'clarity': 'slightly turbid',
                'temperature': '22.3°C',
                'ph_estimate': 'neutral (7.1)',
                'mixing_quality': 'well-mixed'
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
    def mock_beaker_analysis(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'analysis_results': {
                'timestamp': datetime.now().isoformat(),
                'colors_detected': ['red', 'blue', 'yellow'],
                'dominant_color': 'purple',
                'color_percentages': {
                    'red': 35.2,
                    'blue': 28.7,
                    'yellow': 15.3,
                    'purple': 20.8
                },
                'analysis_confidence': 0.94,
                'beaker_position': {'x': 0.15, 'y': 0.22, 'z': 0.08},
                'volume_estimate': '45ml',
                'clarity': 'slightly turbid',
                'temperature': '22.3°C',
                'ph_estimate': 'neutral (7.1)',
                'mixing_quality': 'well-mixed'
            }
        }
        self.wfile.write(json.dumps(response).encode())

def run_test():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, SimpleTestHandler)
    
    print("🧪 Frontend Integration Test Server")
    print("   URL: http://localhost:3000")
    print("   Testing: robot_service/main.py ↔ frontend/index.html integration")
    print("   Press Ctrl+C to stop")
    print()
    print("📋 Test Instructions:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Click any color dispense button (red, blue, yellow)")
    print("   3. Check if beaker analysis results appear")
    print("   4. Verify the analysis visualization works correctly")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Test completed")

if __name__ == '__main__':
    run_test()
