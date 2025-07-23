#!/usr/bin/env python3
"""
Frontend FastAPI Server

A simple FastAPI server that serves the frontend HTML interface and acts as a proxy 
to the robot service and vision bridge to avoid CORS issues.
"""

import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ROBOT_SERVICE_URL = os.getenv("ROBOT_SERVICE_URL", "http://localhost:8000")
VISION_SERVICE_URL = os.getenv("VISION_SERVICE_URL", "http://localhost:5000")

app = FastAPI(
    title="Aloha Lite Frontend",
    description="Web interface for robot control and beaker analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend HTML file."""
    try:
        with open("/home/hafnium/aloha-lite/frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend HTML file not found")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "frontend",
        "robot_service": ROBOT_SERVICE_URL,
        "vision_service": VISION_SERVICE_URL
    }

@app.api_route("/robot/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_robot_service(request: Request, path: str):
    """Proxy requests to the robot service."""
    url = f"{ROBOT_SERVICE_URL}/robot/{path}"
    logger.info(f"Proxying {request.method} request to: {url}")
    
    # Forward query parameters
    if request.query_params:
        url += "?" + str(request.query_params)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Get request body if present
            body = await request.body() if request.method in ["POST", "PUT"] else None
            if body:
                logger.info(f"Request body: {body.decode()}")
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=body
            )
            
            logger.info(f"Robot service response status: {response.status_code}")
            logger.info(f"Robot service response headers: {dict(response.headers)}")
            
            # Return the response properly
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    response_json = response.json()
                    logger.info(f"Robot service response JSON: {response_json}")
                    return response_json
                else:
                    response_text = response.text
                    logger.info(f"Robot service response text: {response_text}")
                    return response_text
            except Exception as parse_error:
                logger.error(f"Error parsing response: {parse_error}")
                # Try to get raw response content
                try:
                    raw_content = response.content.decode()
                    logger.error(f"Raw response content: {raw_content}")
                    return {"error": "Response parsing failed", "raw_status": response.status_code, "raw_content": raw_content}
                except:
                    return {"error": "Response parsing failed", "raw_status": response.status_code}
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Robot service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Robot service unavailable")
        except Exception as e:
            logger.error(f"Robot service proxy error: {e}")
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# Proxy endpoints for vision service
@app.api_route("/vision/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_vision_service(request: Request, path: str):
    """Proxy requests to the vision service."""
    url = f"{VISION_SERVICE_URL}/{path}"
    
    # Forward query parameters
    if request.query_params:
        url += "?" + str(request.query_params)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Handle multipart form data (for image uploads)
            if request.headers.get("content-type", "").startswith("multipart/form-data"):
                form = await request.form()
                files = {}
                data = {}
                
                for key, value in form.items():
                    if hasattr(value, 'read'):  # File upload
                        files[key] = (value.filename, await value.read(), value.content_type)
                    else:  # Regular form field
                        data[key] = value
                
                response = await client.request(
                    method=request.method,
                    url=url,
                    files=files,
                    data=data
                )
            else:
                # Get request body if present
                body = await request.body() if request.method in ["POST", "PUT"] else None
                
                # Forward the request
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=dict(request.headers),
                    content=body
                )
            
            # Return the response properly
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Vision service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Vision service unavailable")
        except Exception as e:
            logger.error(f"Vision service proxy error: {e}")
            raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

@app.get("/status")
async def system_status():
    """Check the status of all backend services."""
    status = {
        "frontend": "healthy",
        "services": {}
    }
    
    # Check robot service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ROBOT_SERVICE_URL}/health")
            status["services"]["robot"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        status["services"]["robot"] = "unavailable"
    
    # Check vision service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{VISION_SERVICE_URL}/health")
            status["services"]["vision"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        status["services"]["vision"] = "unavailable"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
