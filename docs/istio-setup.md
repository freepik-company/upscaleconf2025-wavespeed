# Istio Setup Guide for Wave Speed Conference

This guide explains how to use Istio to gather metrics regarding request time from the inference-balancer service.

## What is Istio?

Istio is a service mesh that provides a way to control how microservices share data with one another. It includes features like traffic management, security, and observability without requiring changes to your application code.

For this project, we're using Istio primarily for its observability features - specifically to gather detailed metrics about request times and traffic patterns.

## Installation

We've integrated Istio into the Helmfile setup for easy deployment. The installation includes:

1. Istio base components (CRDs)
2. Istiod (control plane)
3. Configuration to inject Istio sidecars into the inference-balancer namespace

## Components and Configuration

### 1. Istio Components

- **istio-base**: Provides CRDs and cluster-wide resources
- **istiod**: The control plane that manages and configures proxies to route traffic

### 2. Sidecar Injection

We've configured automatic sidecar injection for the inference-balancer namespace by adding the `istio-injection: enabled` label to the namespace.

### 3. Metrics Collection

Istio automatically collects metrics from all proxied traffic, including:
- Request count
- Request duration
- Request size
- Response size
- Error rates by response code

These metrics are exposed through Prometheus and visualized in Grafana.

## Deployment Steps

1. Install all services including Istio:
   ```bash
   make deploy-services
   ```

2. Ensure Istio injection is enabled for the namespace:
   ```bash
   make enable-istio-injection
   ```

3. Deploy the inference-balancer with Istio sidecar injection:
   ```bash
   make deploy-balancer
   ```

4. Verify Istio installation and sidecar injection:
   ```bash
   make istio-verify
   ```

5. If you don't see the Istio proxy in the pods, restart the deployments:
   ```bash
   make restart-inference-balancer
   ```

6. Generate test traffic:
   ```bash
   make run-istio-test
   ```

## Viewing Metrics

1. Access Grafana:
   ```bash
   make grafana-ui
   ```

2. Navigate to the Dashboards section and find the Istio dashboards:
   - Istio Mesh Dashboard: Overview of all services in the mesh
   - Istio Service Dashboard: Details about the inference-balancer service
   - Istio Workload Dashboard: Details about the inference-balancer pods
   - Istio Performance Dashboard: Performance metrics of the service mesh

## Troubleshooting

### No Istio Sidecars

If pods aren't showing Istio sidecars:

1. Verify and add the namespace label:
   ```bash
   make enable-istio-injection
   ```

2. Restart the deployments:
   ```bash
   make restart-inference-balancer
   ```

### No Metrics in Grafana

If you don't see metrics in Grafana:

1. Verify Prometheus is scraping Istio metrics:
   ```bash
   kubectl port-forward -n monitoring svc/prometheus-server 9090:80
   ```
   Then visit http://localhost:9090/targets and check if Istio targets are up.

2. Generate more traffic:
   ```bash
   make run-istio-test
   ```

## Customizing Metrics Collection

You can customize what metrics Istio collects by editing the `infrastructure/deployment/helmfile/values/istio-values.yaml` file and updating the telemetry settings. 