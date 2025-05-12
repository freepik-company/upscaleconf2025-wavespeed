#!/usr/bin/env python
import os
import logging
from src.celery import app, BROKER_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Flower server...")
    logger.info(f"Monitoring broker: {BROKER_URL}")
    
    # Use the app instance directly from celery.py
    argv = [
        'flower',
        f'--broker={BROKER_URL}',
        '--port=5555',
        '--address=0.0.0.0',  # Bind to all interfaces
        '--basic_auth=admin:admin',  # Basic auth protection (optional)
    ]
    app.start(argv) 