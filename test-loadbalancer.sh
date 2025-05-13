#!/bin/bash

# Number of requests to send
NUM_REQUESTS=100

# Counter for successful requests
success_count=0

echo "Sending $NUM_REQUESTS requests to the load balancer..."

for i in $(seq 1 $NUM_REQUESTS); do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/flux)
  
  if [ "$response" == "200" ]; then
    success_count=$((success_count + 1))
    echo -n "."
  else
    echo -n "x"
  fi
  
  # Small delay to prevent overwhelming the service
  sleep 0.1
done

echo ""
echo "Test completed. Successful requests: $success_count/$NUM_REQUESTS" 