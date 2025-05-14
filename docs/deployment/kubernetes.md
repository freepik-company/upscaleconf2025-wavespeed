# Freepik - WaveSpeed Kubernetes Deployment Guide

This guide provides instructions for deploying the Freepik WaveSpeed image processing system on Kubernetes using the provided Makefile commands.

## Prerequisites

- A Kubernetes cluster (k3d setup via Makefile)
- kubectl
- Helm/Helmfile (installed via Makefile)

## Setup the Kubernetes Cluster

```bash
# Check if you have all required tools
make check-dependencies

# Install tools if needed
make install-tools

# Create the k3d cluster
make setup-cluster
```

## Deploy Core Services

Deploy Redis, Prometheus, Grafana, and KEDA:

```bash
make deploy-services
```

## Deploy the Application

Build and deploy the Celery application for image processing:

```bash
make deploy-app
```

## Deploy the Inference Balancer

Deploy the inference balancer component for distributing image processing workload:

```bash
make deploy-balancer
```

## Complete Setup in One Step

Alternatively, you can do all of the above in a single command:

```bash
make start-workshop
```

## Access the Services

After deployment, you can access the various services:

```bash
# Show all UI endpoints
make show-ui

# Access Celery API
make api-ui  # http://localhost:8000

# Access Flower dashboard
make flower-ui  # http://localhost:5555

# Access Grafana dashboard
make grafana-ui  # http://localhost:3000

# Access Prometheus
make prometheus-ui  # http://localhost:9090

# Access Load Test UI (after running load tests)
make loadtest-ui  # http://localhost:8089
```

## Run Load Tests

To test the image processing system under load:

```bash
make run-loadtest
```

## View Logs

For debugging purposes, you can view the logs of the deployed pods:

```bash
# View logs for a specific pod
kubectl logs -n workshop <pod-name>
```

## Cleanup

When you're done, you can clean up all resources:

```bash
make clean-all
``` 