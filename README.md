# UpscaleConf 2025 - WaveSpeed Workshop

## Managing High-Volume Requests at Scale

This repository contains the infrastructure and application code for the UpscaleConf 2025 workshop on handling high-volume requests in large-scale applications.

## Getting Started

### Prerequisites

- Docker
- curl
- kubectl
- helm
- helmfile
- k3d

### Setup

First, check your environment for all required dependencies:

```bash
# Check if you have all required tools
make check-dependencies

# Install all required tools at once
make install-tools
```

The workshop environment can be set up using the provided Makefile:

```bash
# Option 1: Basic setup - just the Kubernetes cluster
make setup-cluster

# Option 2: Complete setup - cluster + all services (Redis, etc.)
make start-workshop
```

This will:
1. Install k3d (a lightweight wrapper to run k3s in Docker)
2. Create a local Kubernetes cluster with 2 agent nodes
3. Deploy the base applications in the workshop namespace
4. Deploy Redis with 2Gi memory allocation (with option 2)
5. Deploy Prometheus and Grafana for monitoring (with option 2)

### Infrastructure as Code with Helmfile

The workshop includes Helmfile configurations to deploy additional services:

```bash
# Install Helmfile and its dependencies (included in make install-tools)
make install-tools

# Deploy services defined in the Helmfile (Redis, etc.)
make deploy-services

# Deploy only the core infrastructure (labeled as "scaffolding")
cd infrastructure/deployment/helmfile && helmfile apply --selector category=scaffolding

# Remove all workshop resources
make clean-all
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
make clean-all
```

## Repository Structure

- `docs/`: Documentation resources
  - `architecture/`: System architecture diagrams and explanations
  - `workshop-guide/`: Guides for workshop instructors and participants
- `workshop/`: Workshop materials
  - `hands-on/`: Google Colab notebooks
  - `exercises/`: Guided exercises
  - `resources/`: Workshop resources and references
- `infrastructure/`: Infrastructure code
  - `cluster/`: Cluster configuration
    - `k3d/`: k3d cluster configuration
  - `platform/`: Core platform services
    - `observability/`: Monitoring and logging
      - `grafana/`: Grafana configurations
      - `prometheus/`: Prometheus configurations
    - `messaging/`: Message broker services
      - `redis/`: Redis configurations
    - `scaling/`: Autoscaling configuration
      - `keda/`: KEDA configurations
  - `services/`: Application services
    - `celery-app/`: Celery application
      - `helm/`: Celery app Helm chart
    - `balancer/`: Load balancer service
      - `helm/`: Inference balancer Helm chart
      - `nginx/`: Nginx configuration
  - `deployment/`: Deployment configurations
    - `helmfile/`: Helmfile deployment definitions
    - `kubernetes/`: Raw Kubernetes manifests
- `apps/`: Application code
  - `backend/`: Backend Celery application
  - `frontend/`: Frontend application (placeholder)
- `testing/`: Testing tools and configurations
  - `load-testing/`: Load testing scripts
  - `performance/`: Performance benchmarks
  - `results/`: Directory for test results

## Workshop Exercises

The workshop will guide you through:

1. Setting up a local Kubernetes cluster using k3d
2. Deploying basic services and infrastructure with Helmfile
3. Implementing scalable application patterns
4. Load testing and optimization with real-time monitoring
