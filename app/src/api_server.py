#!/usr/bin/env python
import logging
import uvicorn
from src.api.celery_api import app
from prometheus_fastapi_instrumentator import Instrumentator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Add Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run("src.api.celery_api:app", host="0.0.0.0", port=8000, log_level="info", workers=4) 