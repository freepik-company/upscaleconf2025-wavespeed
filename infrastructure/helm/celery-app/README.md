# Celery App Helm Chart

This Helm chart deploys a Celery application with FastAPI, Celery workers, and Flower monitoring.

## Components

The chart deploys the following components:

- **API Server**: FastAPI-based API for submitting tasks to Celery
- **Celery Workers**: Workers that process tasks from the Redis queue
- **Flower Dashboard**: Monitoring and management UI for Celery

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Redis installed (the chart expects Redis to be available at `redis-master:6379`)

## Installing the Chart

To install the chart with the release name `celery-app`:

```bash
helm install celery-app ./celery-app
```

## Configuration

The following table lists the configurable parameters for the Celery chart:

| Parameter                         | Description                            | Default                   |
|-----------------------------------|----------------------------------------|---------------------------|
| `image.repository`                | Image repository                       | `celery-app`              |
| `image.tag`                       | Image tag                              | `latest`                  |
| `image.pullPolicy`                | Image pull policy                      | `IfNotPresent`            |
| `celery.api.enabled`              | Enable API deployment                  | `true`                    |
| `celery.api.replicas`             | Number of API replicas                 | `1`                       |
| `celery.api.port`                 | API container port                     | `8000`                    |
| `celery.worker.enabled`           | Enable worker deployment               | `true`                    |
| `celery.worker.replicas`          | Number of worker replicas              | `2`                       |
| `celery.flower.enabled`           | Enable Flower deployment               | `true`                    |
| `celery.flower.replicas`          | Number of Flower replicas              | `1`                       |
| `celery.flower.port`              | Flower container port                  | `5555`                    |
| `service.type`                    | API service type                       | `ClusterIP`               |
| `service.port`                    | API service port                       | `80`                      |
| `ingress.enabled`                 | Enable API ingress                     | `true`                    |
| `ingress.className`               | Ingress class name                     | `nginx`                   |
| `ingress.hosts[0].host`           | Hostname for API                       | `celery-api.local`        |
| `resources`                       | CPU/Memory resource requests/limits    | See `values.yaml`         |
| `env`                             | Environment variables                  | See `values.yaml`         |

## Usage with Helmfile

This chart is typically deployed using Helmfile. The relevant configuration is in `infrastructure/helmfile/helmfile.yaml` and values in `infrastructure/helmfile/values/celery-app-values.yaml`.

To deploy using Helmfile:

```bash
cd infrastructure/helmfile
helmfile apply -l name=celery-app
```

## Accessing the Services

After deployment, you can access:

1. **API**: Port-forward the API service
   ```bash
   kubectl port-forward svc/celery-app-api 8000:80 -n workshop
   ```

2. **Flower UI**: Port-forward the Flower service
   ```bash
   kubectl port-forward svc/celery-app-flower 5555:5555 -n workshop
   ``` 