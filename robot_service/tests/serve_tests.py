#!/usr/bin/env python3
"""
Test Server for Robot Service
Serves the test files including the beaker integration test HTML file.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    # Set the working directory to robot_service
    script_dir = Path(__file__).parent
    robot_service_dir = script_dir.parent
    os.chdir(robot_service_dir)
    
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port {port}")
    
    print(f"🌐 Starting Robot Service Test Server")
    print(f"📁 Serving from: {robot_service_dir}")
    print(f"🚀 Server running on port: {port}")
    print(f"")
    print(f"📋 Available Test URLs:")
    print(f"   🧪 Beaker Integration Test: http://localhost:{port}/tests/test_beaker_integration.html")
    print(f"   📄 Tests README: http://localhost:{port}/tests/README.md")
    print(f"   📖 Main README: http://localhost:{port}/README.md")
    print(f"")
    print(f"💡 Press Ctrl+C to stop the server")
    print(f"=" * 70)
    
    try:
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port:")
            print(f"   python3 tests/serve_tests.py 8081")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
