# Celery API and Worker

This is a Celery-based task processing system with a FastAPI frontend for submitting tasks, Redis for message queueing, and Celery workers for task processing.

## Components

- **API Server**: FastAPI server that provides endpoints for submitting tasks and checking task status
- **Celery Worker**: Worker process that consumes tasks from Redis queue and executes them
- **Redis**: Message broker that handles task queueing
- **Flower**: Web-based monitoring tool for Celery tasks and workers

## Getting Started

### Prerequisites

- A Kubernetes cluster (k3d setup via Makefile)
- kubectl
- Helm/Helmfile (installed via Makefile)

### Deployment with Kubernetes

1. Build and deploy the application to k3d:

```bash
# Setup the Kubernetes cluster and core infrastructure
make setup-cluster
make scaffold-deploy

# Build and deploy Celery application
make build-celery-app
make deploy-celery-app
```

2. Access the services:

```bash
# Access the Celery API
make celery-api-ui  # Access at http://localhost:8000

# Access the Flower monitoring dashboard
make celery-flower-ui  # Access at http://localhost:5555
```

3. View logs for debugging:

```bash
# Check all Celery pod statuses and information
make celery-pod-logs

# Check logs for a specific pod
kubectl logs -n workshop <pod-name>
```

## Monitoring with Flower

Flower provides a web-based dashboard for monitoring Celery tasks and workers. 

- Access the Flower dashboard at: http://localhost:5555 (after running `make celery-flower-ui`)
- Default credentials: admin/admin

The dashboard shows:
- Active workers and their status
- Queued, active, and completed tasks
- Task history and results
- Ability to cancel or revoke tasks

## API Endpoints

- **POST /tasks/add**: Submit an addition task
  - Request body: `{"x": 5, "y": 3}`
  - Response: `{"task_id": "task-uuid", "status": "pending"}`

- **POST /tasks/long-running**: Submit a long-running task
  - Request body: `{"seconds": 10}`
  - Response: `{"task_id": "task-uuid", "status": "pending"}`

- **GET /tasks/{task_id}**: Check task status
  - Response: `{"task_id": "task-uuid", "status": "SUCCESS", "result": 8}`

## Example Usage

### Submit an Addition Task

```bash
curl -X POST http://localhost:8000/tasks/add \
  -H "Content-Type: application/json" \
  -d '{"x": 5, "y": 3}'
```

### Check Task Status

```bash
curl -X GET http://localhost:8000/tasks/task-uuid
```

## Development

### Project Structure

```
app/
├── Dockerfile         # Container definition for all components
├── requirements.txt   # Python dependencies
└── src/
    ├── api/
    │   └── celery_api.py     # FastAPI endpoints
    ├── api_server.py         # API server entry point
    ├── celery.py             # Celery configuration
    ├── flower_server.py      # Flower server entry point
    ├── tasks.py              # Celery task definitions
    └── worker.py             # Worker entry point
```

### Adding New Tasks

1. Define new task functions in `src/tasks.py`
2. Create API endpoints in `src/api/celery_api.py` 