# Inference Balancer Service

This service provides load balancing across the inference services, including a proxy to the external DataCrunch API.

## Configuration

### DataCrunch API Token

The Flux Service A requires a DataCrunch API token to proxy requests to their API. For security reasons, this token should **not** be committed to Git.

Instead, provide the token during Helm installation or upgrade:

```bash
# Installation
helm install inference-balancer ./infrastructure/services/balancer/helm \
  --set fluxServices.a.datacrunch.bearerToken=your-actual-token-here \
  --namespace inference-balancer

# Upgrade
helm upgrade inference-balancer ./infrastructure/services/balancer/helm \
  --set fluxServices.a.datacrunch.bearerToken=your-actual-token-here \
  --namespace inference-balancer
```

Alternatively, you can create a `values-secret.yaml` file (add it to .gitignore) containing:

```yaml
fluxServices:
  a:
    datacrunch:
      bearerToken: your-actual-token-here
```

And then install/upgrade with:

```bash
helm install/upgrade inference-balancer ./infrastructure/services/balancer/helm \
  -f values-secret.yaml \
  --namespace inference-balancer
``` 