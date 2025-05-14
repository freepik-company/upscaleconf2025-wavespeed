# Freepik - WaveSpeed Celery API and Worker

This is a Celery-based task processing system with a FastAPI frontend for submitting image processing tasks, Redis for message queueing, and Celery workers for task processing.

## Project Structure

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

## Documentation

For detailed documentation, please refer to the centralized documentation in the `docs` directory:

- [Backend Component Documentation](/docs/components/backend/README.md)
- [API Reference](/docs/api-reference/README.md)
- [Deployment Guide](/docs/deployment/kubernetes.md)
- [Main Documentation Index](/docs/README.md) 