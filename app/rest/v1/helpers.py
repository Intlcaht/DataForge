
import os
import tempfile
from typing import List
import uuid
from fastapi import BackgroundTasks, UploadFile, logger
from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """Standard response model for task execution"""
    task_id: str = Field(..., description="Unique identifier for the task")
    status: str = Field(..., description="Task status (pending, completed, failed)")
    message: str = Field(..., description="Informational message about the task")

class FileUploadResponse(BaseModel):
    """Response model for file uploads"""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    temp_path: str = Field(..., description="Temporary storage path")

# In-memory storage for task results and temporary files
task_results = {}
temp_files = {}

def cleanup_temp_files(background_tasks: BackgroundTasks, file_ids: List[str]):
    """Schedule cleanup of temporary files"""
    def _cleanup():
        for file_id in file_ids:
            if file_id in temp_files:
                try:
                    os.remove(temp_files[file_id])
                    del temp_files[file_id]
                    logger.info(f"Cleaned up temporary file: {file_id}")
                except Exception as e:
                    logger.error(f"Failed to clean up file {file_id}: {e}")
    
    background_tasks.add_task(_cleanup)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file to a temporary location and return its ID"""
    content = await upload_file.read()
    # Generate a unique ID
    file_id = f"{uuid.uuid4()}"
    temp_path = os.path.join(tempfile.gettempdir(), f"{file_id}_{upload_file.filename}")
    
    with open(temp_path, "wb") as f:
        f.write(content)
    
    # Track the temporary file
    temp_files[file_id] = {
        "path": temp_path,
        "original_filename": upload_file.filename
    }
    
    logger.info(f"Saved uploaded file {upload_file.filename} to {temp_path}")
    return file_id
