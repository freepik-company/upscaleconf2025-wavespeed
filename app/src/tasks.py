import requests
from src.celery import app
import logging

logger = logging.getLogger(__name__)

# Log at module level that tasks are being registered
logger.info("Registering Celery tasks...")

@app.task(bind=True, name='tasks.flux', queue='default')
def flux(self):
    """Task that makes a request to the inference-balancer endpoint."""
    logger.info(f"Task ID: {self.request.id} - Sending request to inference-balancer")
    try:
        response = requests.get("http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux")
        status_code = response.status_code
        response_text = response.text
        logger.info(f"Task ID: {self.request.id} - Got response: {status_code}, content: {response_text}")
        return {"status_code": status_code, "response": response_text}
    except Exception as e:
        logger.error(f"Task ID: {self.request.id} - Error calling inference-balancer: {str(e)}")
        return {"error": str(e)} 