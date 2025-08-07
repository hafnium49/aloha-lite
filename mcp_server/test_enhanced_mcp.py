#!/usr/bin/env python3
"""
Test script for the enhanced ALOHA-Lite MCP Server
"""

import asyncio
import json
import sys
import os

# Add the mcp_server directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from main import AlohaLitePlaywrightMCP, start_playwright_server, check_playwright_health, stop_playwright_server

async def test_process_management():
    """Test Playwright server process management"""
    print("🧪 Testing Enhanced MCP Server Process Management")
    print("=" * 50)
    
    print("1. Testing Playwright server startup...")
    success = await start_playwright_server()
    print(f"   ✅ Startup: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print("2. Testing health check...")
        healthy = await check_playwright_health()
        print(f"   ✅ Health: {'HEALTHY' if healthy else 'UNHEALTHY'}")
        
        print("3. Testing MCP server initialization...")
        mcp_server = AlohaLitePlaywrightMCP()
        running = await mcp_server.ensure_playwright_running()
        print(f"   ✅ MCP Init: {'SUCCESS' if running else 'FAILED'}")
        
        print("4. Testing server shutdown...")
        await stop_playwright_server()
        print("   ✅ Shutdown: COMPLETED")
    
    print("\n🎉 Test completed!")

async def test_mcp_protocol():
    """Test basic MCP protocol handling"""
    print("\n🧪 Testing MCP Protocol Handling")
    print("=" * 50)
    
    server = AlohaLitePlaywrightMCP()
    
    # Test initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    
    print("1. Testing initialize request...")
    response = await server.handle_initialize(init_request)
    print(f"   ✅ Initialize: {'SUCCESS' if response.get('result') else 'FAILED'}")
    
    # Test unknown method
    unknown_request = {
        "jsonrpc": "2.0", 
        "id": 2,
        "method": "unknown_method"
    }
    
    print("2. Testing unknown method handling...")
    response = await server.handle_request(unknown_request)
    has_error = response and 'error' in response
    print(f"   ✅ Unknown method: {'SUCCESS' if has_error else 'FAILED'}")
    
    print("\n🎉 MCP Protocol test completed!")

if __name__ == "__main__":
    print("🚀 ALOHA-Lite Enhanced MCP Server Test Suite")
    print("=" * 60)
    
    async def run_tests():
        try:
            await test_process_management()
            await test_mcp_protocol()
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
        finally:
            # Ensure cleanup
            await stop_playwright_server()
    
    asyncio.run(run_tests())
