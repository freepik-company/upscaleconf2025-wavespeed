import time
from src.celery import app
import logging

logger = logging.getLogger(__name__)

# Log at module level that tasks are being registered
logger.info("Registering Celery tasks...")

@app.task(bind=True, name='tasks.add', queue='default')
def add(self, x, y):
    """Simple task that adds two numbers."""
    logger.info(f"Task ID: {self.request.id} - Adding {x} + {y}")
    return x + y

@app.task(bind=True, name='tasks.long_running_task', queue='default')
def long_running_task(self, seconds=10):
    """Example of a long running task."""
    logger.info(f"Task ID: {self.request.id} - Starting long running task for {seconds} seconds")
    time.sleep(seconds)
    logger.info(f"Task ID: {self.request.id} - Long running task completed")
    return f"Task completed after {seconds} seconds" 