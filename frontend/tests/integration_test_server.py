#!/usr/bin/env python3
"""
Integration Test Server

This server serves the frontend and proxies robot service requests to the mock service.
This allows testing the actual frontend/index.html integration with a simulated robot service.
"""

import json
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import mimetypes
from datetime import datetime

class IntegrationTestHandler(BaseHTTPRequestHandler):
    # Mock robot service URL
    ROBOT_SERVICE_URL = "http://localhost:8001"
    FRONTEND_DIR = "/home/hafnium/aloha-lite/frontend"
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Robot service API endpoints
        if path.startswith('/robot/'):
            self.proxy_to_robot_service('GET')
            return
        
        # Serve frontend files
        if path == '/' or path == '/index.html':
            self.serve_file('index.html')
        else:
            # Try to serve other static files
            file_path = path.lstrip('/')
            self.serve_file(file_path)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Robot service API endpoints
        if path.startswith('/robot/'):
            self.proxy_to_robot_service('POST')
            return
        
        # Default 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def proxy_to_robot_service(self, method):
        """Proxy requests to the mock robot service"""
        try:
            url = f"{self.ROBOT_SERVICE_URL}{self.path}"
            
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b''
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, data=post_data, headers=headers, timeout=5)
            
            # Forward response
            self.send_response(response.status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
            self.end_headers()
            self.wfile.write(response.content)
            
        except requests.exceptions.RequestException as e:
            # Mock robot service not available, provide fallback
            self.send_response(503)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                'error': 'Robot service unavailable',
                'message': 'Mock robot service is not running on port 8001'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def serve_file(self, filename):
        """Serve static files from frontend directory"""
        file_path = os.path.join(self.FRONTEND_DIR, filename)
        
        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
            return
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_integration_server(port=3000):
    """Run the integration test server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, IntegrationTestHandler)
    
    print(f"🌐 Integration Test Server starting on port {port}")
    print(f"   Frontend: http://localhost:{port}")
    print(f"   Robot Service Proxy: http://localhost:{port}/robot/*")
    print(f"   Expected Mock Robot Service: http://localhost:8001")
    print("   Press Ctrl+C to stop")
    print()
    print("💡 To start the mock robot service:")
    print("   python3 /home/hafnium/aloha-lite/frontend/tests/mock_robot_service.py")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Integration Test Server stopped")

if __name__ == '__main__':
    run_integration_server()
