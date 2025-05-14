import requests
from src.celery import app
import logging
import json

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

@app.task(bind=True, name='tasks.webhook_flux', queue='default')
def webhook_flux(self, webhook_url=None, prompt=None, seed=None):
    """
    Task that makes a request to the inference-balancer endpoint 
    and forwards the response to a webhook endpoint.
    
    Args:
        webhook_url: Optional URL to send the webhook response to.
                    Defaults to webhook.webhook.svc.cluster.local/publish-response
        prompt: The prompt text to send to the inference-balancer
        seed: The seed value to use for the inference
    """
    # Use default webhook URL if none provided
    if webhook_url is None:
        webhook_url = "http://webhook.webhook.svc.cluster.local/publish-response"
    
    logger.info(f"Task ID: {self.request.id} - Sending request to inference-balancer (webhook)")
    try:
        # Prepare request payload
        payload = {}
        if prompt is not None:
            payload["prompt"] = prompt
        if seed is not None:
            payload["seed"] = seed
            
        # Call the inference balancer
        if payload:
            logger.info(f"Task ID: {self.request.id} - Sending payload: {payload}")
            response = requests.post(
                "http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
        else:
            response = requests.get("http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux")
            
        status_code = response.status_code
        response_text = response.text
        logger.info(f"Task ID: {self.request.id} - Got response: {status_code}, content: {response_text}")
        
        # Prepare the payload for the webhook
        webhook_payload = {
            "task_id": self.request.id,
            "status_code": status_code,
            "response": response_text
        }
        
        # Include original request in the webhook payload
        if prompt is not None:
            webhook_payload["prompt"] = prompt
        if seed is not None:
            webhook_payload["seed"] = seed
        
        # Send the response to the webhook endpoint
        webhook_response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(webhook_payload)
        )
        
        logger.info(f"Task ID: {self.request.id} - Webhook delivery status: {webhook_response.status_code}")
        
        return {
            "status_code": status_code, 
            "response": response_text,
            "webhook_status": webhook_response.status_code
        }
    except Exception as e:
        logger.error(f"Task ID: {self.request.id} - Error in webhook_flux task: {str(e)}")
        return {"error": str(e)}

@app.task(bind=True, name='tasks.websocket_flux', queue='default')
def websocket_flux(self, websocket_url):
    """
    Task that makes a request to the inference-balancer endpoint 
    and forwards the response to a websocket endpoint.
    """
    logger.info(f"Task ID: {self.request.id} - Sending request to inference-balancer (websocket)")
    try:
        # Call the inference balancer
        response = requests.get("http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux")
        status_code = response.status_code
        response_text = response.text
        logger.info(f"Task ID: {self.request.id} - Got response: {status_code}, content: {response_text}")
        
        # Prepare the payload for the websocket
        payload = {
            "task_id": self.request.id,
            "status_code": status_code,
            "response": response_text
        }
        
        # Send the response to the websocket endpoint
        websocket_response = requests.post(
            websocket_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        logger.info(f"Task ID: {self.request.id} - Websocket delivery status: {websocket_response.status_code}")
        
        return {
            "status_code": status_code, 
            "response": response_text,
            "websocket_status": websocket_response.status_code
        }
    except Exception as e:
        logger.error(f"Task ID: {self.request.id} - Error in websocket_flux task: {str(e)}")
        return {"error": str(e)} 