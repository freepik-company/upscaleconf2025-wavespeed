# UpscaleConf 2025 - WaveSpeed Workshop

## Managing High-Volume Requests at Scale

This repository contains the infrastructure and application code for the UpscaleConf 2025 workshop on handling high-volume requests in large-scale applications.

## Getting Started

### Prerequisites

- Docker
- curl
- kubectl

### Setup

First, check your environment for all required dependencies:

```bash
# Check if you have all required tools
make check-dependencies

# Install all required tools at once
make install-all
```

The workshop environment can be set up using the provided Makefile:

```bash
# Option 1: Basic setup - just the Kubernetes cluster
make setup-cluster

# Option 2: Complete setup - cluster + all services (Redis, etc.)
make setup-all
```

This will:
1. Install k3d (a lightweight wrapper to run k3s in Docker)
2. Create a local Kubernetes cluster with 2 agent nodes
3. Deploy the base applications in the workshop namespace
4. Deploy Redis with 2Gi memory allocation (with option 2)
5. Deploy Prometheus and Grafana for monitoring (with option 2)
6. Configure port forwarding to access the services

The nginx service will be available at: http://localhost:8080

### Infrastructure as Code with Helmfile

The workshop includes Helmfile configurations to deploy additional services:

```bash
# Install Helmfile and its dependencies
make install-helmfile

# Deploy services defined in the Helmfile (Redis, etc.)
make helm-deploy

# Deploy only the core infrastructure (labeled as "scaffolding")
make scaffold-deploy

# Remove Helmfile-deployed services
make helm-destroy
```

The Redis instance is configured with 2Gi of memory. no password authentication.

To connect to Redis after deployment:
```bash
kubectl port-forward service/redis-master 6379:6379 -n workshop
# Then connect to localhost:6379 with your Redis client (no password required)
```

### Monitoring

The workshop includes Prometheus and Grafana for monitoring Redis:

```bash
# Access Grafana UI (no authentication required)
make grafana-ui

# Access Prometheus UI
make prometheus-ui
```

Grafana comes pre-configured with Redis dashboards to monitor performance, memory usage, and other metrics.

### Load Testing


### Cleanup

To clean up the environment when you're done:

```bash
# This removes all Helm releases and the Kubernetes cluster
make clean-cluster
```

## Repository Structure

- `infrastructure/`: Infrastructure-related files
  - `kubernetes/`: Kubernetes configuration
    - `deployments/`: Kubernetes deployment manifests
  - `helmfile/`: Helmfile configurations for service deployment
    - `values/`: Helm chart values
- `app/`: Application code (to be developed during the workshop)
- `load-testing/`: Load testing scripts and configurations

## Workshop Exercises

The workshop will guide you through:

1. Setting up a local Kubernetes cluster using k3d
2. Deploying basic services and infrastructure with Helmfile
3. Implementing scalable application patterns
4. Load testing and optimization with real-time monitoring
5. Advanced scaling techniques
