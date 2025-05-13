from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.tasks import add, long_running_task

app = FastAPI(title="Celery Task API", description="API for submitting Celery tasks")

class AddTaskRequest(BaseModel):
    x: int
    y: int

class LongRunningTaskRequest(BaseModel):
    seconds: Optional[int] = 10

class TaskResponse(BaseModel):
    task_id: str
    status: str = "pending"

@app.post("/tasks/add", response_model=TaskResponse)
async def submit_add_task(request: AddTaskRequest):
    """Submit an addition task to Celery."""
    try:
        task = add.delay(request.x, request.y)
        return TaskResponse(task_id=task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@app.post("/tasks/long-running", response_model=TaskResponse)
async def submit_long_running_task(request: LongRunningTaskRequest):
    """Submit a long running task to Celery."""
    try:
        task = long_running_task.delay(request.seconds)
        return TaskResponse(task_id=task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@app.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """Get status of a submitted task."""
    try:
        # Create an AsyncResult instance to check task status
        from celery.result import AsyncResult
        task_result = AsyncResult(task_id)
        
        result = {
            "task_id": task_id,
            "status": task_result.status,
        }
        
        # Include result if task is successful
        if task_result.status == "SUCCESS":
            result["result"] = task_result.get()
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 