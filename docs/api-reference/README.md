# Freepik - WaveSpeed API Reference

This document provides details about the API endpoints available in the Freepik WaveSpeed image processing system.

## Celery API

### Task Submission Endpoints

#### Submit a Flux Task

- **URL**: `/flux`
- **Method**: `POST`
- **Description**: Submit a flux task that will test the inference-balancer for image processing
- **Request Body**: None
- **Response**:
  ```json
  {
    "task_id": "task-uuid",
    "status": "pending"
  }
  ```

### Task Status Endpoints

#### Check Task Status

- **URL**: `/tasks/{task_id}`
- **Method**: `GET`
- **Description**: Get the status of a previously submitted image processing task
- **URL Parameters**:
  - `task_id`: The ID of the task to check
- **Response**:
  ```json
  {
    "task_id": "task-uuid",
    "status": "SUCCESS"
  }
  ```
  - Possible status values: "PENDING", "STARTED", "SUCCESS", "FAILURE", "REVOKED", "RETRY"
  - Note: This endpoint only returns the status, not the result

## Result Delivery

Task results are not retrieved via the API. Instead:

- Results are forwarded directly from workers to a webhook or websocket server
- Clients should connect to the webhook/websocket server to receive real-time notifications when tasks are completed
- This approach provides immediate result delivery without polling

## Example Usage

### Submit a Flux Task

```bash
curl -X POST http://localhost:8000/flux
```

### Check Task Status

```bash
curl -X GET http://localhost:8000/tasks/task-uuid
``` 