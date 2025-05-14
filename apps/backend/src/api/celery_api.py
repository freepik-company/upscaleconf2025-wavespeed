from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import Optional, Dict, Any
from importlib import import_module
from src.tasks import flux, webhook_flux, websocket_flux

app = FastAPI(title="Celery Task API", description="API for submitting Celery tasks")

class TaskResponse(BaseModel):
    task_id: str
    status: str = "pending"

class WebhookRequest(BaseModel):
    webhook_url: Optional[str] = None
    prompt: Optional[str] = None
    seed: Optional[int] = None

class WebsocketRequest(BaseModel):
    websocket_url: Optional[str] = None
    prompt: Optional[str] = None
    seed: Optional[int] = None

@app.post("/flux", response_model=TaskResponse)
async def submit_flux_task():
    """Submit a flux task to test the inference-balancer."""
    try:
        task = flux.delay()
        return TaskResponse(task_id=task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@app.post("/webhook/{inference_model}", response_model=TaskResponse)
async def submit_webhook_task(
    request: WebhookRequest,
    inference_model: str = Path(..., description="The inference model to use (e.g., flux)")
):
    """
    Dynamic webhook task endpoint that forwards results to the specified webhook URL.
    The specific task is determined by the inference_model path parameter.
    """
    try:
        # Try to get the task dynamically
        task_name = f"webhook_{inference_model}"
        try:
            # First try to get it from already imported tasks
            task_module = import_module("src.tasks")
            task = getattr(task_module, task_name, None)
            
            if task is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Task for inference model '{inference_model}' not found"
                )
                
        except (ImportError, AttributeError):
            raise HTTPException(
                status_code=404, 
                detail=f"Task for inference model '{inference_model}' not found"
            )
            
        # Execute the task with all parameters
        celery_task = task.delay(
            webhook_url=request.webhook_url,
            prompt=request.prompt,
            seed=request.seed
        )
        return TaskResponse(task_id=celery_task.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit webhook task: {str(e)}")

@app.post("/websocket/{inference_model}", response_model=TaskResponse)
async def submit_websocket_task(
    request: WebsocketRequest,
    inference_model: str = Path(..., description="The inference model to use (e.g., flux)")
):
    """
    Dynamic websocket task endpoint that forwards results to the specified websocket URL.
    The specific task is determined by the inference_model path parameter.
    """
    try:
        # Try to get the task dynamically
        task_name = f"websocket_{inference_model}"
        try:
            # First try to get it from already imported tasks
            task_module = import_module("src.tasks")
            task = getattr(task_module, task_name, None)
            
            if task is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Task for inference model '{inference_model}' not found"
                )
                
        except (ImportError, AttributeError):
            raise HTTPException(
                status_code=404, 
                detail=f"Task for inference model '{inference_model}' not found"
            )
            
        # Execute the task with all parameters
        celery_task = task.delay(
            websocket_url=request.websocket_url,
            prompt=request.prompt,
            seed=request.seed
        )
        return TaskResponse(task_id=celery_task.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit websocket task: {str(e)}")

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