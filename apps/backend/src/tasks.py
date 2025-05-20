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
        # Create a payload with the car prompt for DataCrunch API
        payload = {
            "input": {
                "prompt": "A car"
            }
        }
        
        # Use POST with the payload instead of GET
        response = requests.post(
            "http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        status_code = response.status_code
        response_text = response.text
        logger.info(f"Task ID: {self.request.id} - Got response: {status_code}")
        return {"status_code": status_code, "response": response_text}
    except Exception as e:
        logger.error(f"Task ID: {self.request.id} - Error calling inference-balancer: {str(e)}")
        return {"error": str(e)}

@app.task(bind=True, name='tasks.webhook_flux', queue='default')
def webhook_flux(self, webhook_url=None, prompt=None, seed=None, enable_base64_output=None, cache_threshold=None, size=None):
    """
    Task that makes a request to the inference-balancer endpoint 
    and forwards the response to a webhook endpoint.
    
    Args:
        webhook_url: Optional URL to send the webhook response to.
                    Defaults to webhook.webhook.svc.cluster.local/publish-response
        prompt: The prompt text to send to the inference-balancer
        seed: The seed value to use for the inference
        enable_base64_output: Whether to return base64 encoded image
        cache_threshold: Threshold for caching
        size: Size of the generated image
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
        if enable_base64_output is not None:
            payload["enable_base64_output"] = enable_base64_output
        if cache_threshold is not None:
            payload["cache_threshold"] = cache_threshold
        if size is not None:
            payload["size"] = size
            
        # Special handling for input.prompt format required by DataCrunch API
        datacrunch_payload = {}
        if "prompt" in payload:
            datacrunch_payload = {
                "input": {
                    "prompt": payload["prompt"]
                }
            }

            if "seed" in payload:
                datacrunch_payload["input"]["seed"] = payload["seed"]
            if "enable_base64_output" in payload:
                datacrunch_payload["input"]["enable_base64_output"] = payload["enable_base64_output"]
            if "cache_threshold" in payload:
                datacrunch_payload["input"]["cache_threshold"] = payload["cache_threshold"]
            if "size" in payload:
                datacrunch_payload["input"]["size"] = payload["size"]
        
        # Call the inference balancer
        if payload:
            logger.info(f"Task ID: {self.request.id} - Sending payload: {datacrunch_payload or payload}")
            response = requests.post(
                "http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux",
                headers={"Content-Type": "application/json"},
                data=json.dumps(datacrunch_payload or payload)
            )
        else:
            response = requests.get("http://inference-balancer-main.inference-balancer.svc.cluster.local:80/flux")
            
        status_code = response.status_code
        response_text = response.text
        logger.info(f"Task ID: {self.request.id} - Got response: {status_code}")
        
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
        if enable_base64_output is not None:
            webhook_payload["enable_base64_output"] = enable_base64_output
        if cache_threshold is not None:
            webhook_payload["cache_threshold"] = cache_threshold
        if size is not None:
            webhook_payload["size"] = size
        
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
def websocket_flux(self, websocket_url=None, prompt=None, seed=None, enable_base64_output=None, cache_threshold=None, size=None):
    """
    Task that makes a request to the inference-balancer endpoint 
    and forwards the response to a websocket endpoint.
    
    Args:
        websocket_url: Optional URL to send the websocket response to.
                      Defaults to visualize-websocket.frontend.svc.cluster.local/publish
        prompt: The prompt text to send to the inference-balancer
        seed: The seed value to use for the inference
        enable_base64_output: Whether to return base64 encoded image
        cache_threshold: Threshold for caching
        size: Size of the generated image
    """
    # Use default websocket URL if none provided
    if websocket_url is None:
        websocket_url = "http://visualize-websocket.frontend.svc.cluster.local:8766/publish"
    
    logger.info(f"Task ID: {self.request.id} - Sending request to inference-balancer (websocket)")
    try:
        # Prepare request payload
        payload = {}
        if prompt is not None:
            payload["prompt"] = prompt
        if seed is not None:
            payload["seed"] = seed
        if enable_base64_output is not None:
            payload["enable_base64_output"] = enable_base64_output
        if cache_threshold is not None:
            payload["cache_threshold"] = cache_threshold
        if size is not None:
            payload["size"] = size
            
        # Special handling for input.prompt format required by DataCrunch API
        datacrunch_payload = {}
        if "prompt" in payload:
            datacrunch_payload = {
                "input": {
                    "prompt": payload["prompt"]
                }
            }
            if "seed" in payload:
                datacrunch_payload["input"]["seed"] = payload["seed"]
            if "enable_base64_output" in payload:
                datacrunch_payload["input"]["enable_base64_output"] = payload["enable_base64_output"]
            if "cache_threshold" in payload:
                datacrunch_payload["input"]["cache_threshold"] = payload["cache_threshold"]
            if "size" in payload:
                datacrunch_payload["input"]["size"] = payload["size"]
        
        # Call the inference balancer
        if payload:
            logger.info(f"Task ID: {self.request.id} - Sending payload: {datacrunch_payload or payload}")
            response = requests.post(
                "http://inference-balancer.inference-balancer.svc.cluster.local/flux",
                headers={"Content-Type": "application/json"},
                data=json.dumps(datacrunch_payload or payload)
            )
        else:
            response = requests.get("http://inference-balancer.inference-balancer.svc.cluster.local/flux")
            
        status_code = response.status_code
        response_text = response.text
        logger.info(f"Task ID: {self.request.id} - Got response: {status_code}")
        
        # Parse the DataCrunch API response to extract the image URL
        try:
            datacrunch_response = json.loads(response_text)
            # Extract image URL from the response
            image_url = None
            if datacrunch_response.get('output') and datacrunch_response['output'].get('outputs'):
                image_url = datacrunch_response['output']['outputs'][0]
                
            # Enhance the response with the image URL
            enhanced_response = {
                "status": datacrunch_response.get('status', 'UNKNOWN'),
                "id": datacrunch_response.get('id', ''),
                "image_url": image_url,  # Direct reference to image URL
                "seed": datacrunch_response.get('output', {}).get('seed', None),
                "has_nsfw": datacrunch_response.get('output', {}).get('has_nsfw_contents', [False])[0]
            }
            
            # Prepare the payload for the websocket
            websocket_payload = {
                "task_id": self.request.id,
                "status_code": status_code,
                "response": enhanced_response,
                "original_response": datacrunch_response
            }
        except json.JSONDecodeError:
            logger.warning(f"Task ID: {self.request.id} - Could not parse response as JSON: {response_text}")
            # If we can't parse the response, just send it as-is
            websocket_payload = {
                "task_id": self.request.id,
                "status_code": status_code,
                "response": response_text
            }
        
        # Include original request in the websocket payload
        if prompt is not None:
            websocket_payload["prompt"] = prompt
        if seed is not None:
            websocket_payload["seed"] = seed
        if enable_base64_output is not None:
            websocket_payload["enable_base64_output"] = enable_base64_output
        if cache_threshold is not None:
            websocket_payload["cache_threshold"] = cache_threshold
        if size is not None:
            websocket_payload["size"] = size
        
        # Send the response to the websocket endpoint
        logger.info(f"Task ID: {self.request.id} - Sending to WebSocket: {websocket_url}")
        websocket_response = requests.post(
            websocket_url,
            headers={"Content-Type": "application/json"},
            json=websocket_payload
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