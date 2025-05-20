#!/usr/bin/env python
import os
import logging
from src.celery import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Celery worker...")
    logger.info(f"Broker URL: {app.conf.broker_url}")
    logger.info(f"Result Backend: {app.conf.result_backend}")
    logger.info(f"Default Queue: {app.conf.task_default_queue}")
    
    # Use the app instance directly from celery.py
    argv = [
        'worker',
        '--loglevel=INFO',
        '--concurrency=3',  # Adjust based on your needs
        '-Q', 'default',    # Queue name
    ]
    app.worker_main(argv) 