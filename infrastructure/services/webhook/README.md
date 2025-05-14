# Webhook Service

A simple Nginx-based service that receives webhook requests and logs them.

## Overview

This service provides an endpoint `/publish-response` that:
- Accepts any HTTP request
- Logs the request details
- Returns a 200 OK response

It's designed to receive responses from worker services like the Celery tasks and confirm their receipt.

## Usage

To install the chart:

```bash
helm install webhook ./infrastructure/services/webhook
```

## Endpoints

- `/health` - Health check endpoint, returns 200 OK
- `/publish-response` - Main webhook endpoint, logs the request and returns 200 OK

## How to use with Celery tasks

When submitting a task through the API, specify this service's URL as the webhook URL:

```
POST /webhook/flux
{
  "webhook_url": "http://webhook-service.default.svc.cluster.local/publish-response"
}
```

The Celery worker will make a request to this URL when the task completes. 