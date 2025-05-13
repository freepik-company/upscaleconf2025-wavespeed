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
    
    @task(8)
    def add_task(self):
        """Submit a simple addition task - higher weight for more frequency"""
        x = random.randint(1, 100)
        y = random.randint(1, 100)
        
        payload = {"x": x, "y": y}
        response = self.client.post("/tasks/add", json=payload)
        
        if response.status_code == 200:
            # Optionally check the task status after a delay
            time.sleep(0.5)  # Give the task time to process
    
    @task(2)
    def long_running_task(self):
        """Submit a long running task - lower weight for less frequency"""
        seconds = random.randint(2, 5)  # Keep it short for load testing
        
        payload = {"seconds": seconds}
        response = self.client.post("/tasks/long-running", json=payload)
        
        if response.status_code == 200:
            task_id = response.json().get("task_id")
            # We don't wait for the long task to complete, just fire and forget 