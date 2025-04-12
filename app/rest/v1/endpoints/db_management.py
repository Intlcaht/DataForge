import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, logger
from pydantic import BaseModel, Field
from typing import Optional
from services.storage.local import local_db_controller as db_controller
from rest.v1.helpers import  TaskResponse,  task_results

class ServiceCommandRequest(BaseModel):
    """Request model for database service commands"""
    service: str = Field(..., description="Database service identifier (p=PostgreSQL, m=MariaDB, g=MongoDB, f=InfluxDB, n=Neo4j, r=Redis)")
    command: str = Field(..., description="Command to execute (s=start, k=stop, r=restart, l=logs, b=backup, c=connect, h=health, t=stats)")

class AllServicesCommandRequest(BaseModel):
    """Request model for commands that affect all services"""
    command: str = Field(..., description="Command to execute on all services (s=start, k=stop, t=status, b=backup)")

class InitializeStackRequest(BaseModel):
    """Request model for initializing the database stack"""
    root_password: Optional[str] = Field(None, description="Optional root password for database initialization")

router = APIRouter()

@router.post("/api/db/initialize", response_model=TaskResponse)
async def initialize_stack(request: InitializeStackRequest, background_tasks: BackgroundTasks):
    """Initialize the database stack with Terraform"""
    task_id = str(uuid.uuid4())
    
    async def _run_task():
        try:
            args = ["-i"]
            if request.root_password:
                args.append(request.root_password)
                
            result = await db_controller.initialize_stack(request.root_password)
            task_results[task_id] = {
                "status": "completed",
                "result": result
            }
        except Exception as e:
            logger.error(f"Task failed: {e}")
            task_results[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    background_tasks.add_task(_run_task)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Stack initialization started"
    }

@router.post("/api/db/service", response_model=TaskResponse)
async def manage_service(request: ServiceCommandRequest, background_tasks: BackgroundTasks):
    """Execute a command on a specific database service"""
    task_id = str(uuid.uuid4())
    
    async def _run_task():
        try:
            result = await db_controller.manage_service(request.service, request.command)
            task_results[task_id] = {
                "status": "completed",
                "result": result
            }
        except Exception as e:
            logger.error(f"Task failed: {e}")
            task_results[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    background_tasks.add_task(_run_task)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": f"Service command '{request.command}' for '{request.service}' started"
    }

@router.post("/api/db/all", response_model=TaskResponse)
async def manage_all_services(request: AllServicesCommandRequest, background_tasks: BackgroundTasks):
    """Execute a command on all database services"""
    task_id = str(uuid.uuid4())
    
    async def _run_task():
        try:
            result = await db_controller.manage_all_services(request.command)
            task_results[task_id] = {
                "status": "completed",
                "result": result
            }
        except Exception as e:
            logger.error(f"Task failed: {e}")
            task_results[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    background_tasks.add_task(_run_task)
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": f"Command '{request.command}' for all services started"
    }
