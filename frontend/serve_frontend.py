#!/usr/bin/env python3
"""
Simple HTTP Server for Frontend Testing

Serves the frontend/index.html and provides CORS support for testing
the robot service integration.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_frontend_server(port=3000):
    """Run the frontend server"""
    # Change to frontend directory
    frontend_dir = '/home/hafnium/aloha-lite/frontend'
    os.chdir(frontend_dir)
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    print(f"🌐 Frontend Server starting on port {port}")
    print(f"   Open: http://localhost:{port}")
    print(f"   Serving: {frontend_dir}")
    print("   Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Frontend Server stopped")

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_frontend_server(port)
