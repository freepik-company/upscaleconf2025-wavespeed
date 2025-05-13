# Helmfile for WaveSpeed Workshop

This directory contains the Helmfile configuration for deploying all required services for the UpscaleConf 2025 WaveSpeed workshop.

## Prerequisites

- [Helm](https://helm.sh/docs/intro/install/) (v3.x+)
- [Helmfile](https://helmfile.readthedocs.io/en/latest/#installation)
- Kubernetes cluster (k3d setup via `make setup-cluster`)

## Components

The Helmfile is configured to deploy the following services:

1. **Redis** - In-memory data store used for caching and message broker
   - 2Gi of memory (as requested)
   - No authentication required (for simplicity)
   - Metrics enabled for monitoring
   - Persistent storage for data
   - Labeled as "scaffolding" infrastructure

Additional components are configured as commented entries in the Helmfile and can be enabled as needed:

- **Prometheus** - Monitoring system (commented out)
- **Grafana** - Visualization and dashboard tool (commented out)

## Deployment Labels

Services in the Helmfile are organized using labels. Currently, we use the following labels:

- **category: scaffolding**: Core infrastructure components needed for the workshop

You can deploy only services with a specific label using the selector argument:

```bash
helmfile apply --selector category=scaffolding
```

Or using the make target:

```bash
make scaffold-deploy
```

## Usage

### Apply the Helmfile

To deploy all services:

```bash
cd infrastructure/helmfile
helmfile apply
```

To deploy a specific release:

```bash
helmfile -l name=redis apply
```

### Connecting to Redis

After deployment, Redis can be accessed by port-forwarding:

```bash
kubectl port-forward service/redis-master 6379:6379 -n workshop
```

Then connect to Redis at `localhost:6379` without authentication.

### List Deployed Releases

```bash
helmfile list
```

### Delete Releases

To remove all services:

```bash
helmfile destroy
```

## Configuration

- `helmfile.yaml` - Main Helmfile configuration
- `values/` - Directory containing Helm chart values files
  - `redis-values.yaml` - Redis configuration

## Adding New Services

To add a new service:

1. Add a new entry under the `releases` section in `helmfile.yaml`
2. Create a values file in the `values/` directory
3. Reference the values file in the release configuration
4. Add appropriate labels to categorize the service (e.g., `category: application`) 