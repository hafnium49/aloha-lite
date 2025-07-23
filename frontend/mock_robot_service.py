#!/usr/bin/env python3
"""
Mock Robot Service for Frontend Integration Testing

This is a simple HTTP server that simulates the robot service API
to test the frontend/index.html beaker analysis integration.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime

class MockRobotHandler(BaseHTTPRequestHandler):
    # Class variables to store state
    tasks = {}
    task_counter = 0
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Health check
        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'ok', 'service': 'mock-robot-service'}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Get task status
        if path.startswith('/robot/') and path.endswith('/status'):
            cmd_id = path.split('/')[2]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if cmd_id in self.tasks:
                task = self.tasks[cmd_id]
                response = {
                    'status': task['status'],
                    'message': task['message'],
                    'beaker_analysis_results': task.get('beaker_analysis_results')
                }
            else:
                response = {'status': 'not_found', 'message': 'Task not found'}
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Get beaker analysis results
        if path.startswith('/robot/') and path.endswith('/beaker-analysis'):
            cmd_id = path.split('/')[2]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if cmd_id in self.tasks and 'beaker_analysis_results' in self.tasks[cmd_id]:
                response = {
                    'analysis_results': self.tasks[cmd_id]['beaker_analysis_results']
                }
            else:
                response = {'analysis_results': None}
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Get pose snapshot
        if path.startswith('/robot/') and path.endswith('/pose-snapshot'):
            cmd_id = path.split('/')[2]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Mock pose snapshot data
            response = {
                'pose_snapshot': {
                    'timestamp': datetime.now().isoformat(),
                    'left_arm': [0.1, -0.5, 0.3, 1.2, -0.8, 0.2, 0.0],
                    'right_arm': [-0.1, -0.5, -0.3, -1.2, 0.8, -0.2, 0.0],
                    'base': 0.15
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Dispense endpoint (legacy)
        if path == '/robot/dispense':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                
                # Generate task ID
                self.task_counter += 1
                cmd_id = f"dispense_{self.task_counter}"
                
                # Simulate task execution
                task = {
                    'status': 'completed',
                    'message': f'Dispensed {request_data.get("color", "unknown")} color',
                    'start_time': time.time()
                }
                
                self.tasks[cmd_id] = task
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {'cmd_id': cmd_id, 'status': 'ok'}
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON')
            return
        
        # Execute task
        if path == '/robot/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                
                # Generate task ID
                self.task_counter += 1
                cmd_id = f"mock_{self.task_counter}"
                
                # Simulate task execution
                task = {
                    'status': 'running',
                    'message': f'Executing {request_data.get("sequence_name", "unknown sequence")}',
                    'start_time': time.time()
                }
                
                # If it's a laboratory procedure, simulate beaker analysis
                if 'laboratory' in request_data.get('sequence_name', '').lower():
                    # Simulate completion after a short delay
                    task['status'] = 'completed'
                    task['message'] = 'Laboratory procedure completed successfully'
                    task['beaker_analysis_results'] = {
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
                else:
                    task['status'] = 'completed'
                    task['message'] = 'Task completed successfully'
                
                self.tasks[cmd_id] = task
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {'cmd_id': cmd_id, 'status': 'accepted'}
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON')
            return
        
        # Default 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_mock_server(port=8001):
    """Run the mock robot service server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockRobotHandler)
    
    print(f"🤖 Mock Robot Service starting on port {port}")
    print(f"   Health check: http://localhost:{port}/health")
    print(f"   Frontend can connect to: http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Mock Robot Service stopped")

if __name__ == '__main__':
    run_mock_server()
