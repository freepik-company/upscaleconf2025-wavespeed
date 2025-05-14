# Freepik - WaveSpeed Celery API and Worker

This is a Celery-based task processing system with a FastAPI frontend for submitting image processing tasks, Redis for message queueing, and Celery workers for task processing.

## Components

- **API Server**: FastAPI server that provides endpoints for submitting image processing tasks and checking task status
- **Celery Worker**: Worker process that consumes tasks from Redis queue and executes image transformations
- **Redis**: Message broker that handles task queueing (not used for storing results)
- **Flower**: Web-based monitoring tool for Celery tasks and workers
- **Inference Balancer**: Component that processes inference requests for image transformation
- **Load Testing**: Tools for testing system performance under load
- **Webhook/WebSocket Server**: Receives processed results from workers and notifies clients in real-time
- **Nginx with Lua**: Optional component for transforming async requests to sync for client simplicity

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
make deploy-services

# Build and deploy Celery application
make deploy-app

# Deploy the inference balancer
make deploy-balancer

# Alternatively, use a single command for complete setup
make start-workshop
```

2. Access the services:

```bash
# Access the Celery API
make api-ui  # Access at http://localhost:8000

# Access the Flower monitoring dashboard
make flower-ui  # Access at http://localhost:5555

# See all UI endpoints
make show-ui
```

3. View logs for debugging:

```bash
# Check logs for a specific pod
kubectl logs -n workshop <pod-name>
```

## Monitoring with Flower

Flower provides a web-based dashboard for monitoring Celery tasks and workers. 

- Access the Flower dashboard at: http://localhost:5555 (after running `make flower-ui`)
- Default credentials: admin/admin

The dashboard shows:
- Active workers and their status
- Queued, active, and completed tasks
- Task history and results
- Ability to cancel or revoke tasks

## Load Testing

You can run load tests against your deployment:

```bash
make run-loadtest
```

## API Endpoints

- **POST /flux**: Submit a flux task to test the inference-balancer for image processing
  - Response: `{"task_id": "task-uuid", "status": "pending"}`
  - Note: Results are not retrieved via API but forwarded to configured webhook/websocket endpoints

- **GET /tasks/{task_id}**: Check task status
  - Response: `{"task_id": "task-uuid", "status": "SUCCESS"}`
  - Note: This endpoint only returns the task status, not the result

## Result Notification

Results are not stored in Redis or retrieved via the API. Instead:

1. Workers forward results directly to a configured webhook or websocket server
2. Clients connect to the webhook/websocket server to receive real-time notifications
3. This approach eliminates polling and provides immediate result delivery

## API Flexibility with Nginx and Lua

The system supports flexible request handling using Nginx with Lua scripts:

### Synchronous Client Experience with Asynchronous Processing

- Nginx can be configured with Lua scripts to provide a synchronous API experience to clients
- This allows clients to make regular synchronous requests while the backend operates asynchronously
- The Lua script:
  - Forwards the client request to the Celery API
  - Subscribes to the webhook/websocket server for the specific task's result
  - Holds the connection open until the result is received
  - Returns the result to the client as if it were a direct synchronous response

### Implementation

To implement this pattern:

1. Configure Nginx with the appropriate Lua scripts
2. Set up the webhook/websocket server for result notification
3. No changes needed to the Celery backend or task processing

This approach preserves all the benefits of asynchronous processing (scalability, resilience) while providing a simple synchronous API for clients that prefer or require it.

## Example Usage

### Submit a Flux Task

```bash
curl -X POST http://localhost:8000/flux
```

### Check Task Status

```bash
curl -X GET http://localhost:8000/tasks/task-uuid
```

## Development

### Project Structure

```
apps/backend/
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
3. Configure webhook/websocket endpoints for result forwarding