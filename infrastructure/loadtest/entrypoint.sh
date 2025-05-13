#!/bin/bash
set -e

# Set default values for environment variables
HOST=${LOCUST_HOST:-http://celery-app-api}
USERS=${LOCUST_USERS:-10}
SPAWN_RATE=${LOCUST_SPAWN_RATE:-1}
RUN_TIME=${LOCUST_RUN_TIME:-24h}

# Run locust with the processed environment variables
exec locust --host "$HOST" --headless --users "$USERS" --spawn-rate "$SPAWN_RATE" --run-time "$RUN_TIME" 