"""
ALOHA-Lite MCP Server
Implements Model Context Protocol for robot control via Claude Desktop
"""
import json
import sys
import logging
import asyncio
import requests
from typing import Dict, List, Any, Optional

# Configure logging to stderr so it appears in Claude Desktop logs
logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("aloha-mcp")

class AlohaLiteMCPServer:
    def __init__(self):
        self.robot_service_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    async def handle_initialize(self, request: Dict) -> Dict:
        """Handle MCP initialize request"""
        logger.info("Handling initialize request")
        
        return {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "aloha-lite-mcp",
                    "version": "1.0.0",
                    "description": "ALOHA-Lite robot control server"
                }
            }
        }
    
    async def handle_tools_list(self, request: Dict) -> Dict:
        """List available robot control tools"""
        tools = [
            {
                "name": "move_robot_joints",
                "description": "Move robot arm joints to specified positions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "arm": {"type": "string", "enum": ["left", "right"]},
                        "joints": {"type": "array", "items": {"type": "number"}},
                        "configuration": {"type": "string", "description": "Named configuration"}
                    }
                }
            },
            {
                "name": "read_joint_positions",
                "description": "Read current robot joint positions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "arm": {"type": "string", "enum": ["left", "right", "both"]}
                    }
                }
            },
            {
                "name": "execute_sequence",
                "description": "Execute a predefined robot sequence",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sequence_name": {"type": "string"},
                        "parameters": {"type": "object"}
                    }
                }
            },
            {
                "name": "dispense_solution",
                "description": "Dispense colored solution with volume optimization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "colors": {"type": "object", "description": "Color ratios"},
                        "total_volume": {"type": "number"}
                    }
                }
            },
            {
                "name": "analyze_beaker_color",
                "description": "Analyze the color of solution in beaker using vision",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "capture_image": {"type": "boolean", "default": True}
                    }
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "tools": tools
            }
        }
    
    async def handle_tool_call(self, request: Dict) -> Dict:
        """Handle tool execution"""
        tool_name = request["params"]["name"]
        arguments = request["params"].get("arguments", {})
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "read_joint_positions":
                result = await self.read_joint_positions(arguments)
            elif tool_name == "move_robot_joints":
                result = await self.move_robot_joints(arguments)
            elif tool_name == "execute_sequence":
                result = await self.execute_sequence(arguments)
            elif tool_name == "dispense_solution":
                result = await self.dispense_solution(arguments)
            elif tool_name == "analyze_beaker_color":
                result = await self.analyze_beaker_color(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def read_joint_positions(self, args: Dict) -> Dict:
        """Read current joint positions from robot"""
        try:
            # Call the joint reader utility
            import subprocess
            import os
            
            joint_reader_path = os.path.join(os.path.dirname(__file__), "..", "utilities", "joint_reader.py")
            arm = args.get("arm", "both")
            
            cmd = ["python3", joint_reader_path, "--arm", arm]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(joint_reader_path))
            
            if result.returncode == 0:
                return {
                    "status": "success", 
                    "message": f"Joint positions read for {arm} arm(s)",
                    "output": result.stdout,
                    "arm": arm
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to read joint positions: {result.stderr}",
                    "arm": arm
                }
        except Exception as e:
            return {"status": "error", "message": f"Joint reader error: {str(e)}"}
    
    async def move_robot_joints(self, args: Dict) -> Dict:
        """Move robot joints"""
        try:
            # Call execute_rules.py with the specified configuration
            import subprocess
            import os
            
            config_name = args.get("configuration")
            if config_name:
                execute_rules_path = os.path.join(os.path.dirname(__file__), "..", "execute_rules.py")
                cmd = ["python3", execute_rules_path, "--config", config_name]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(execute_rules_path))
                
                if result.returncode == 0:
                    return {
                        "status": "success",
                        "message": f"Robot moved to configuration: {config_name}",
                        "output": result.stdout,
                        "configuration": config_name
                    }
                else:
                    return {
                        "status": "error", 
                        "message": f"Failed to move robot: {result.stderr}",
                        "configuration": config_name
                    }
            else:
                return {"status": "error", "message": "No configuration specified"}
        except Exception as e:
            return {"status": "error", "message": f"Robot movement error: {str(e)}"}
    
    async def execute_sequence(self, args: Dict) -> Dict:
        """Execute robot sequence"""
        try:
            # Call sequential_execute.py
            import subprocess
            import os
            
            sequence_name = args.get("sequence_name")
            if sequence_name:
                sequential_path = os.path.join(os.path.dirname(__file__), "..", "sequential_execute.py")
                cmd = ["python3", sequential_path, sequence_name]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(sequential_path))
                
                if result.returncode == 0:
                    return {
                        "status": "success",
                        "message": f"Sequence executed: {sequence_name}",
                        "output": result.stdout,
                        "sequence": sequence_name
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Failed to execute sequence: {result.stderr}",
                        "sequence": sequence_name
                    }
            else:
                return {"status": "error", "message": "No sequence specified"}
        except Exception as e:
            return {"status": "error", "message": f"Sequence execution error: {str(e)}"}
    
    async def dispense_solution(self, args: Dict) -> Dict:
        """Dispense solution with ML optimization"""
        try:
            # Call the frontend service for ML-optimized dispensing
            colors = args.get("colors", {})
            total_volume = args.get("total_volume", 5.0)
            
            payload = {
                "color_ratios": colors,
                "total_volume": total_volume
            }
            
            response = requests.post(f"{self.frontend_url}/dispense", json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Solution dispensed successfully",
                    "result": response.json(),
                    "colors": colors,
                    "volume": total_volume
                }
            else:
                return {
                    "status": "error",
                    "message": f"Dispensing failed: {response.status_code}",
                    "colors": colors,
                    "volume": total_volume
                }
        except Exception as e:
            return {"status": "error", "message": f"Dispensing error: {str(e)}"}
    
    async def analyze_beaker_color(self, args: Dict) -> Dict:
        """Analyze beaker color using vision"""
        try:
            # Call the vision bridge service
            capture_image = args.get("capture_image", True)
            
            if capture_image:
                # First capture an image
                response = requests.post(f"http://localhost:8001/capture", timeout=30)
                if response.status_code != 200:
                    return {"status": "error", "message": f"Failed to capture image: {response.status_code}"}
            
            # Then analyze the color
            response = requests.post(f"http://localhost:8001/analyze_color", timeout=30)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Color analysis completed",
                    "result": response.json(),
                    "captured_image": capture_image
                }
            else:
                return {
                    "status": "error",
                    "message": f"Color analysis failed: {response.status_code}",
                    "captured_image": capture_image
                }
        except Exception as e:
            return {"status": "error", "message": f"Color analysis error: {str(e)}"}
    
    async def handle_request(self, request: Dict) -> Dict:
        """Route requests to appropriate handlers"""
        method = request.get("method")
        
        if method == "initialize":
            return await self.handle_initialize(request)
        elif method == "tools/list":
            return await self.handle_tools_list(request)
        elif method == "tools/call":
            return await self.handle_tool_call(request)
        elif method == "notifications/initialized":
            # Just acknowledge - no response needed
            logger.info("Client initialized")
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def run(self):
        """Main server loop - read from stdin, write to stdout"""
        logger.info("ALOHA-Lite MCP Server starting...")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                logger.info(f"Received request: {request.get('method', 'unknown')}")
                
                response = await self.handle_request(request)
                
                if response:
                    print(json.dumps(response), flush=True)
                    logger.info(f"Sent response for: {request.get('method', 'unknown')}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Server error: {e}")
                break

async def main():
    """Main entry point"""
    server = AlohaLiteMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
