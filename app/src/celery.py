from celery import Celery
import os

# Get broker and backend URLs from environment variables or use defaults
BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
BACKEND_URL = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Configure Celery app
app = Celery(
    'tasks',
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=['src.tasks']
)

# Optional configuration
app.conf.update(
    result_expires=3600,  # Results expire after 1 hour
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_default_queue='default',  # Ensure tasks go to the default queue
)

if __name__ == '__main__':
    app.start() 