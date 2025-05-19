# Freepik - WaveSpeed Architecture Documentation

This document provides an overview of the Freepik WaveSpeed system architecture, explaining how the various components work together to provide a scalable, high-throughput task processing system for Freepik's image processing needs.

## System Overview

Freepik WaveSpeed is designed as a scalable, distributed system for processing high-volume image transformation requests, with the following key components:


## Core Components

### API Layer

- **Celery API Server**: FastAPI-based service that provides REST endpoints for image processing task submission and status checking
- **Inference Balancer**: Load balancer that distributes inference requests across available processing nodes for efficient image handling

### Processing Layer

- **Celery Workers**: Distributed task processing nodes that execute the actual image transformations
- **Autoscaling (KEDA)**: Kubernetes Event-Driven Autoscaler that scales workers based on Redis queue depth to handle varying image processing loads

### Infrastructure Layer

- **Redis**: Message broker and result backend for Celery tasks, storing image processing requests and results
- **Kubernetes**: Container orchestration platform that runs all system components

### Monitoring Layer

- **Prometheus**: Metrics collection and storage for monitoring system performance
- **Grafana**: Visualization and dashboards for system metrics to track image processing efficiency
- **Flower**: Web-based monitoring specific to Celery tasks and workers, showing task processing details

## Data Flow

1. **Task Submission**:
   - Client sends image processing request to Celery API
   - API creates a task and submits it to Redis queue
   - API returns task ID to client

2. **Task Processing**:
   - Celery worker picks up image task from Redis queue
   - Worker processes image (which may involve calling the inference balancer)
   - Worker forwards the result directly to a configured webhook or websocket server
   - No results are stored in Redis

3. **Result Notification**:
   - The webhook or websocket server receives the processed result
   - Connected clients are notified of the completed task
   - This real-time notification eliminates the need for clients to poll for results

## Scaling Mechanism

The system scales horizontally using KEDA (Kubernetes Event-Driven Autoscaler) to handle Freepik's varying image processing loads:

1. KEDA monitors the depth of the Redis task queues
2. When queue depth exceeds thresholds, KEDA scales up Celery worker pods
3. When queue depth decreases, KEDA scales down worker pods
4. This provides automatic, event-driven scaling based on actual workload

## Deployment Architecture

In Kubernetes, the Freepik WaveSpeed system is deployed as follows:

- **Namespaces**:
  - `workshop`: Contains application components (Celery API, Workers, Redis)
  - `monitoring`: Contains monitoring tools (Prometheus, Grafana)
  - `keda`: Contains autoscaling components
  - `inference-balancer`: Contains the inference balancer

- **Deployments**:
  - Celery API Server
  - Celery Workers
  - Celery Flower
  - Inference Balancer
  - Redis
  - Prometheus and Grafana

## Resilience Features

- Kubernetes provides automatic restarts of failed pods
- Redis persistence ensures image task data survives Redis pod restarts
- Celery task retry mechanisms handle transient failures during image processing

## Performance Considerations

- Redis is configured with 2Gi memory for optimal performance with large image queues
- Celery workers can be configured for concurrency to handle multiple image processing tasks
- The inference balancer distributes load across processing nodes for efficient resource utilization
- KEDA ensures efficient resource utilization by scaling with image processing demand

## API Flexibility and Request Handling

The Freepik WaveSpeed system is designed with flexibility as a key principle, particularly in how it handles client requests:

### Async-to-Sync Transformation

- The system can be configured with Nginx and Lua scripts to transform asynchronous requests into synchronous ones
- This allows clients to make standard synchronous API calls while the backend operates asynchronously
- The Lua script in Nginx handles:
  1. Accepting the initial client request
  2. Submitting the asynchronous task to the Celery API
  3. Listening for the result notification from the webhook/websocket
  4. Holding the connection open until the result arrives
  5. Returning the result to the client as if it were a synchronous call

### Benefits of This Approach

- **Client Simplicity**: Clients can use familiar synchronous API patterns without implementing webhook/websocket listeners
- **Implementation Flexibility**: The async-to-sync transformation happens at the infrastructure level, not in the application code
- **No Front API Changes**: Changes to the processing architecture don't require changes to client integration
- **Backward Compatibility**: Support for both synchronous and asynchronous client interactions
- **Scalability Preservation**: The core system remains asynchronous internally, maintaining all scaling benefits
