# K3D Cluster Configuration

This directory contains the configuration for the k3d Kubernetes cluster used in the WaveSpeed Workshop.

## Files

- `cluster-config.sh`: Shell script containing cluster configuration variables

## Usage

The cluster configuration is used by the Makefile to create and manage the k3d cluster. The configuration can be modified by editing the `cluster-config.sh` file.

### Configuration Variables

| Variable        | Description                          | Default Value              |
|-----------------|--------------------------------------|----------------------------|
| CLUSTER_NAME    | Name of the k3d cluster              | "workshop-cluster"         |
| SERVERS         | Number of server nodes               | 1                          |
| AGENTS          | Number of agent nodes                | 3                          |
| API_PORT        | Port for the Kubernetes API          | 6550                       |
| PORT_MAPPING    | Port mapping for ingress             | "8080:80@loadbalancer"     |
| AGENTS_MEMORY   | Memory allocation for agent nodes    | "6G"                       |
| SERVERS_MEMORY  | Memory allocation for server nodes   | "4G"                       |

## Integration with Makefile

The Makefile sources this configuration when creating or deleting the cluster.

```makefile
setup-cluster:
	@source infrastructure/cluster/k3d/cluster-config.sh && \
		k3d cluster create $${CLUSTER_NAME} \
		--servers $${SERVERS} \
		--agents $${AGENTS} \
		--api-port $${API_PORT} \
		--port "$${PORT_MAPPING}" \
		--agents-memory $${AGENTS_MEMORY} \
		--servers-memory $${SERVERS_MEMORY}
``` 