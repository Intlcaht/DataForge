
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from rest.v1.helpers import task_results, temp_files
router = APIRouter()

@router.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the status and result of a previously submitted task"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_results[task_id]
    return task

@router.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a processed file"""
    if file_id not in temp_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = temp_files[file_id]
    return FileResponse(
        path=file_info["path"],
        filename=file_info["original_filename"],
        media_type="application/octet-stream"
    )

@router.delete("/api/files/{file_id}")
async def delete_temp_file(file_id: str):
    """Delete a temporary file"""
    if file_id not in temp_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = temp_files[file_id]["path"]
    try:
        os.remove(file_path)
        del temp_files[file_id]
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "temp_files_count": len(temp_files),
        "tasks_count": len(task_results)
    }
