import asyncio
import os
import tempfile
from typing import Optional

# FastAPI imports
from fastapi import APIRouter, HTTPException, Depends, Query, Body, File, UploadFile, BackgroundTasks, logger
from pydantic import BaseModel, Field

from rest.v1.helpers import FileUploadResponse, TaskResponse, save_upload_file, task_results, temp_files

class ObfuscateRequest(BaseModel):
    """Request model for obfuscating an env file"""
    password: str = Field(..., description="Secret password for obfuscation")
    output_filename: Optional[str] = Field(None, description="Custom output filename (optional)")

class DeobfuscateRequest(BaseModel):
    """Request model for deobfuscating an env file"""
    password: str = Field(..., description="Secret password used during obfuscation")
    output_filename: Optional[str] = Field(None, description="Custom output filename (optional)")

router = APIRouter()

@router.post("/api/env/upload", response_model=FileUploadResponse)
async def upload_env_file(file: UploadFile = File(...)):
    """Upload an environment file for processing"""
    if not file.filename.endswith(('.env', '.env.obfuscated', '.json')):
        raise HTTPException(status_code=400, detail="File must be a .env, .env.obfuscated, or .json file")
    
    file_id = await save_upload_file(file)
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "temp_path": temp_files[file_id]["path"]
    }

@router.post("/api/env/obfuscate/{file_id}", response_model=TaskResponse)
async def obfuscate_env_file(
    file_id: str, 
    request: ObfuscateRequest,
    background_tasks: BackgroundTasks
):
    """Obfuscate an uploaded environment file"""
    if file_id not in temp_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    task_id = str(uuid.uuid4())
    input_path = temp_files[file_id]["path"]

    from services.env.obfuscator_service import env_obfuscator
    
    async def _run_task():
        try:
            output_path = None
            if request.output_filename:
                output_path = os.path.join(tempfile.gettempdir(), request.output_filename)
                
            result = await env_obfuscator.obfuscate(input_path, request.password, output_path)
            
            # Track output files
            if "output_files" in result and "output_file" in result["output_files"]:
                output_file_id = str(uuid.uuid4())
                output_path = result["output_files"]["output_file"]["path"]
                temp_files[output_file_id] = {
                    "path": output_path,
                    "original_filename": os.path.basename(output_path)
                }
                result["output_file_id"] = output_file_id
                
            if "output_files" in result and "mapping_file" in result["output_files"]:
                mapping_file_id = str(uuid.uuid4())
                mapping_path = result["output_files"]["mapping_file"]["path"]
                temp_files[mapping_file_id] = {
                    "path": mapping_path,
                    "original_filename": os.path.basename(mapping_path)
                }
                result["mapping_file_id"] = mapping_file_id
                
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
        "message": "File obfuscation started"
    }

@router.post("/api/env/deobfuscate", response_model=TaskResponse)
async def deobfuscate_env_file(
    background_tasks: BackgroundTasks,
    obfuscated_file_id: str = Query(..., description="ID of the uploaded obfuscated file"),
    mapping_file_id: str = Query(..., description="ID of the uploaded mapping file"),
    request: DeobfuscateRequest = Body(...),    
):
    """Deobfuscate an uploaded environment file using its mapping file"""
    if obfuscated_file_id not in temp_files:
        raise HTTPException(status_code=404, detail="Obfuscated file not found")
    if mapping_file_id not in temp_files:
        raise HTTPException(status_code=404, detail="Mapping file not found")
    
    task_id = str(uuid.uuid4())
    input_path = temp_files[obfuscated_file_id]["path"]
    mapping_path = temp_files[mapping_file_id]["path"]

    from services.env.obfuscator_service import env_obfuscator
    
    async def _run_task():
        try:
            output_path = None
            if request.output_filename:
                output_path = os.path.join(tempfile.gettempdir(), request.output_filename)
                
            result = await env_obfuscator.deobfuscate(
                input_path, 
                mapping_path, 
                request.password, 
                output_path
            )
            
            # Track output file
            if "output_files" in result and "output_file" in result["output_files"]:
                output_file_id = str(uuid.uuid4())
                output_path = result["output_files"]["output_file"]["path"]
                temp_files[output_file_id] = {
                    "path": output_path,
                    "original_filename": os.path.basename(output_path)
                }
                result["output_file_id"] = output_file_id
                
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
        "message": "File deobfuscation started"
    }

# Add missing imports for the async functionality
import uuid
