import time
import json
import random
from locust import HttpUser, task, between

class CeleryTaskUser(HttpUser):
    """
    Locust user that continuously submits tasks to the Celery API
    """
    wait_time = between(1, 3)  # Wait between 1 and 3 seconds between tasks
    
    def on_start(self):
        """Initialize the user session"""
        self.client.headers = {'Content-Type': 'application/json'}
    
    @task(1)
    def check_health(self):
        """Check the health endpoint provided by nginx sidecar"""
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"Health check failed with status: {response.status_code}")
    
    @task(10)
    def flux_task(self):
        """Submit a flux task to test the inference-balancer"""
        response = self.client.post("/flux", json={})
        
        if response.status_code == 200:
            task_id = response.json().get("task_id")
            print(f"Task ID: {task_id}")
        else:
            print(f"Failed to submit task: {response.status_code}")