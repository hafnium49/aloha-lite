#!/usr/bin/env python3
"""
Frontend Test Runner

Simple script to run different types of frontend tests.
"""

import sys
import subprocess
import time
import signal
import os
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.processes = []
    
    def cleanup(self):
        """Clean up any running processes"""
        for proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                try:
                    proc.kill()
                except:
                    pass
    
    def run_mock_service(self):
        """Start mock robot service in background"""
        print("🤖 Starting mock robot service on port 8001...")
        cmd = [sys.executable, str(self.test_dir / "mock_robot_service.py")]
        proc = subprocess.Popen(cmd, cwd=self.test_dir)
        self.processes.append(proc)
        time.sleep(2)  # Give it time to start
        return proc
    
    def run_integration_test(self):
        """Run full integration test"""
        print("🔄 Running full integration test...")
        
        # Start mock service
        mock_proc = self.run_mock_service()
        
        # Start integration server
        print("🌐 Starting integration test server on port 3000...")
        cmd = [sys.executable, str(self.test_dir / "integration_test_server.py")]
        proc = subprocess.Popen(cmd, cwd=self.test_dir)
        self.processes.append(proc)
        
        print("\n✅ Integration test environment ready!")
        print("   Frontend: http://localhost:3000")
        print("   Mock Robot Service: http://localhost:8001")
        print("   Press Ctrl+C to stop")
        
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping integration test...")
            self.cleanup()
    
    def run_simple_test(self):
        """Run simple test"""
        print("🧪 Running simple test...")
        cmd = [sys.executable, str(self.test_dir / "simple_test.py")]
        proc = subprocess.Popen(cmd, cwd=self.test_dir)
        self.processes.append(proc)
        
        print("\n✅ Simple test environment ready!")
        print("   URL: http://localhost:3000")
        print("   Press Ctrl+C to stop")
        
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping simple test...")
            self.cleanup()
    
    def run_simulation(self):
        """Run integration simulation"""
        print("📊 Running integration simulation...")
        cmd = [sys.executable, str(self.test_dir / "test_integration_simulation.py")]
        result = subprocess.run(cmd, cwd=self.test_dir)
        return result.returncode == 0
    
    def run_validation(self):
        """Run integration validation"""
        print("🔍 Running integration validation...")
        cmd = [sys.executable, str(self.test_dir / "validate_integration.py")]
        result = subprocess.run(cmd, cwd=self.test_dir)
        return result.returncode == 0
    
    def serve_frontend(self):
        """Serve frontend only"""
        print("🌐 Serving frontend on port 3000...")
        cmd = [sys.executable, str(self.test_dir / "serve_frontend.py")]
        proc = subprocess.Popen(cmd, cwd=self.test_dir)
        self.processes.append(proc)
        
        print("\n✅ Frontend server ready!")
        print("   URL: http://localhost:3000")
        print("   Note: Robot service calls will fail (no backend)")
        print("   Press Ctrl+C to stop")
        
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping frontend server...")
            self.cleanup()
    
    def show_help(self):
        """Show available commands"""
        print("🧪 Frontend Test Runner")
        print("=" * 40)
        print()
        print("Usage: python3 run_tests.py <command>")
        print()
        print("Commands:")
        print("  integration  - Run full integration test (mock service + frontend)")
        print("  simple       - Run simple test (self-contained)")
        print("  simulation   - Run API call simulation (no servers)")
        print("  validation   - Validate integration implementation")
        print("  frontend     - Serve frontend only (no backend)")
        print("  mock         - Start mock robot service only")
        print("  help         - Show this help")
        print()
        print("Examples:")
        print("  python3 run_tests.py integration  # Full test environment")
        print("  python3 run_tests.py simple       # Quick test")
        print("  python3 run_tests.py validation   # Check implementation")
        print()
        print("For more details, see README.md")

def main():
    runner = TestRunner()
    
    # Handle cleanup on exit
    def signal_handler(sig, frame):
        print("\n🛑 Cleaning up...")
        runner.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if len(sys.argv) < 2:
        runner.show_help()
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "integration":
            runner.run_integration_test()
        elif command == "simple":
            runner.run_simple_test()
        elif command == "simulation":
            success = runner.run_simulation()
            sys.exit(0 if success else 1)
        elif command == "validation":
            success = runner.run_validation()
            sys.exit(0 if success else 1)
        elif command == "frontend":
            runner.serve_frontend()
        elif command == "mock":
            runner.run_mock_service()
            print("\n✅ Mock robot service ready!")
            print("   URL: http://localhost:8001")
            print("   Health: http://localhost:8001/health")
            print("   Press Ctrl+C to stop")
            try:
                runner.processes[0].wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping mock service...")
                runner.cleanup()
        elif command == "help":
            runner.show_help()
        else:
            print(f"❌ Unknown command: {command}")
            runner.show_help()
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        runner.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
