#!/usr/bin/env python3
"""
Multi-Color Dispenser Backend Service

This service handles multi-color dispensing operations with squeeze durations
proportional to color ratios from the frontend interface.
"""

import os
import sys
import json
import time
import logging
import asyncio
import subprocess
import uuid
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Multi-Color Dispenser Service", version="1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ColorRatios(BaseModel):
    red: float = Field(ge=0.0, le=100.0)
    yellow: float = Field(ge=0.0, le=100.0) 
    blue: float = Field(ge=0.0, le=100.0)

class NormalizedPercentages(BaseModel):
    red: float = Field(ge=0.0, le=100.0)
    yellow: float = Field(ge=0.0, le=100.0)
    blue: float = Field(ge=0.0, le=100.0)

class MultiColorDispenseRequest(BaseModel):
    mix_id: int
    run_id: int
    colour: str = Field(pattern="^(red|yellow|blue)$")  # dominant color for compatibility
    color_ratios: ColorRatios
    normalized_percentages: NormalizedPercentages
    base_duration: float = Field(default=3.0, gt=0.0, le=10.0, description="Base duration in seconds")

class ColorOperation(BaseModel):
    color: str
    ratio: float
    duration: float
    config: str
    status: str = "pending"

class DispenseStatus(BaseModel):
    status: str  # pending, running, completed, failed
    cmd_id: str
    created_at: float = Field(default_factory=time.time)
    color_operations: List[ColorOperation] = []
    total_duration: float = 0.0
    current_operation: Optional[str] = None
    error_message: Optional[str] = None

class DispenseResponse(BaseModel):
    cmd_id: str
    status: str
    message: str

# In-memory task storage (use database in production)
TASKS: Dict[str, DispenseStatus] = {}
TASKS_LOCK = asyncio.Lock()

# Color configuration mapping
COLOR_CONFIGS = {
    "red": "dispensing_red_to_beaker",
    "yellow": "dispensing_yellow_to_beaker", 
    "blue": "dispensing_blue_to_beaker"
}

async def execute_squeeze_operation(color: str, duration: float, config_name: str) -> bool:
    """
    Execute a single squeeze operation for a specific color.
    
    Args:
        color: Color name (red, yellow, blue)
        duration: Squeeze duration in seconds
        config_name: Robot configuration name
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Executing squeeze operation: {color} for {duration:.2f}s using {config_name}")
        
        # Build command to execute squeeze operation
        squeeze_bottle_path = os.path.join(os.path.dirname(__file__), "squeeze_bottle.py")
        cmd = [
            sys.executable,  # Use current Python interpreter
            squeeze_bottle_path,
            "--duration", str(duration),
            "--base-config", config_name
        ]
        
        # Execute the squeeze operation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=duration + 10,  # Add buffer time
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode != 0:
            logger.error(f"Squeeze operation failed for {color}: {result.stderr}")
            return False
        
        logger.info(f"Successfully completed squeeze operation for {color}")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"Squeeze operation timed out for {color}")
        return False
    except Exception as e:
        logger.error(f"Error during {color} squeeze operation: {e}")
        return False

async def execute_multi_color_dispensing_task(cmd_id: str, color_ratios: ColorRatios, base_duration: float):
    """
    Background task to execute multi-color dispensing with proportional squeeze durations.
    
    Args:
        cmd_id: Unique command identifier
        color_ratios: Color ratios from frontend
        base_duration: Base duration for scaling
    """
    try:
        async with TASKS_LOCK:
            if cmd_id not in TASKS:
                logger.error(f"Command ID {cmd_id} not found in TASKS")
                return
            TASKS[cmd_id].status = "running"
        
        # Convert ratios to dict for easier processing
        ratios_dict = {
            "red": color_ratios.red,
            "yellow": color_ratios.yellow,
            "blue": color_ratios.blue
        }
        
        # Calculate total parts and individual durations
        total_parts = sum(ratios_dict.values())
        if total_parts == 0:
            raise ValueError("Total color ratios cannot be zero")
        
        color_operations = []
        total_duration = 0
        
        # Process each color with non-zero ratio
        for color, ratio in ratios_dict.items():
            if ratio > 0:
                # Calculate squeeze duration proportional to ratio
                squeeze_duration = (ratio / total_parts) * base_duration
                squeeze_duration = max(squeeze_duration, 0.5)  # Minimum 0.5 seconds
                squeeze_duration = min(squeeze_duration, 8.0)   # Maximum 8.0 seconds
                
                config_name = COLOR_CONFIGS.get(color)
                if not config_name:
                    logger.warning(f"No configuration found for color: {color}")
                    continue
                
                operation = ColorOperation(
                    color=color,
                    ratio=ratio,
                    duration=squeeze_duration,
                    config=config_name,
                    status="pending"
                )
                color_operations.append(operation)
                total_duration += squeeze_duration + 1.0  # Add 1s between operations
        
        # Update task with operation details
        async with TASKS_LOCK:
            TASKS[cmd_id].color_operations = color_operations
            TASKS[cmd_id].total_duration = total_duration
        
        logger.info(f"Starting multi-color dispensing for cmd_id={cmd_id}")
        logger.info(f"Total operations: {len(color_operations)}, estimated duration: {total_duration:.2f}s")
        
        # Execute each color operation sequentially
        for i, operation in enumerate(color_operations):
            # Update current operation status
            async with TASKS_LOCK:
                TASKS[cmd_id].current_operation = f"{operation.color} ({operation.duration:.2f}s)"
                operation.status = "running"
            
            logger.info(f"Dispensing {operation.color} for {operation.duration:.2f}s (ratio: {operation.ratio})")
            
            # Execute squeeze operation
            success = await execute_squeeze_operation(
                operation.color,
                operation.duration,
                operation.config
            )
            
            if not success:
                async with TASKS_LOCK:
                    operation.status = "failed"
                    TASKS[cmd_id].status = "failed"
                    TASKS[cmd_id].error_message = f"Failed to dispense {operation.color}"
                raise RuntimeError(f"Failed to dispense {operation.color}")
            
            # Mark operation as completed
            async with TASKS_LOCK:
                operation.status = "completed"
            
            # Small delay between colors to allow settling
            if i < len(color_operations) - 1:  # Not the last operation
                logger.info("Waiting 1s between color operations...")
                await asyncio.sleep(1.0)
        
        # Mark entire task as completed
        async with TASKS_LOCK:
            TASKS[cmd_id].status = "completed"
            TASKS[cmd_id].current_operation = None
        
        logger.info(f"Multi-color dispensing completed successfully for cmd_id={cmd_id}")
        
    except Exception as e:
        logger.error(f"Multi-color dispensing failed for cmd_id={cmd_id}: {e}")
        async with TASKS_LOCK:
            if cmd_id in TASKS:
                TASKS[cmd_id].status = "failed"
                TASKS[cmd_id].error_message = str(e)
                TASKS[cmd_id].current_operation = None

@app.post("/dispense", response_model=DispenseResponse)
async def dispense_multi_color(request: MultiColorDispenseRequest, background_tasks: BackgroundTasks):
    """
    Start a multi-color dispensing operation with squeeze durations proportional to color ratios.
    
    Returns immediately with a command ID for status tracking.
    """
    try:
        # Generate unique command ID
        cmd_id = str(uuid.uuid4())
        
        # Validate that at least one color has a non-zero ratio
        total_ratio = request.color_ratios.red + request.color_ratios.yellow + request.color_ratios.blue
        if total_ratio <= 0:
            raise HTTPException(400, "At least one color ratio must be greater than 0")
        
        # Create task entry
        task_status = DispenseStatus(
            status="pending",
            cmd_id=cmd_id,
            total_duration=0.0
        )
        
        async with TASKS_LOCK:
            TASKS[cmd_id] = task_status
        
        # Start background task
        background_tasks.add_task(
            execute_multi_color_dispensing_task,
            cmd_id,
            request.color_ratios,
            request.base_duration
        )
        
        logger.info(f"Started multi-color dispensing task with cmd_id={cmd_id}")
        logger.info(f"Color ratios - Red:{request.color_ratios.red} Yellow:{request.color_ratios.yellow} Blue:{request.color_ratios.blue}")
        
        return DispenseResponse(
            cmd_id=cmd_id,
            status="pending",
            message=f"Multi-color dispensing started with ID {cmd_id}"
        )
        
    except Exception as e:
        logger.error(f"Error starting multi-color dispensing: {e}")
        raise HTTPException(500, f"Failed to start dispensing: {str(e)}")

@app.get("/status/{cmd_id}", response_model=DispenseStatus)
async def get_dispense_status(cmd_id: str):
    """
    Get the status of a multi-color dispensing operation.
    """
    async with TASKS_LOCK:
        if cmd_id not in TASKS:
            raise HTTPException(404, f"Command ID {cmd_id} not found")
        
        return TASKS[cmd_id]

@app.get("/tasks", response_model=Dict[str, DispenseStatus])
async def list_all_tasks():
    """
    List all tasks (for debugging purposes).
    """
    async with TASKS_LOCK:
        return TASKS.copy()

@app.delete("/tasks/{cmd_id}")
async def delete_task(cmd_id: str):
    """
    Delete a completed task from memory.
    """
    async with TASKS_LOCK:
        if cmd_id not in TASKS:
            raise HTTPException(404, f"Command ID {cmd_id} not found")
        
        task = TASKS[cmd_id]
        if task.status == "running":
            raise HTTPException(400, "Cannot delete a running task")
        
        del TASKS[cmd_id]
        return {"message": f"Task {cmd_id} deleted successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "multi-color-dispenser",
        "active_tasks": len(TASKS),
        "timestamp": time.time()
    }

# Cleanup old tasks periodically
async def cleanup_old_tasks():
    """
    Background task to cleanup old completed/failed tasks.
    """
    while True:
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # 1 hour ago
            
            async with TASKS_LOCK:
                tasks_to_remove = []
                for cmd_id, task in TASKS.items():
                    if (task.status in ["completed", "failed"] and 
                        task.created_at < cutoff_time):
                        tasks_to_remove.append(cmd_id)
                
                for cmd_id in tasks_to_remove:
                    del TASKS[cmd_id]
                    logger.info(f"Cleaned up old task: {cmd_id}")
            
        except Exception as e:
            logger.error(f"Error during task cleanup: {e}")
        
        # Run cleanup every 30 minutes
        await asyncio.sleep(1800)

@app.on_event("startup")
async def startup_event():
    """
    Start background tasks when the service starts.
    """
    logger.info("Multi-Color Dispenser Service starting up...")
    
    # Start cleanup task
    asyncio.create_task(cleanup_old_tasks())
    
    logger.info("Multi-Color Dispenser Service ready!")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Multi-Color Dispenser Service...")
    uvicorn.run(
        "multi_color_dispenser:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
