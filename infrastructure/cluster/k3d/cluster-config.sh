#!/bin/bash
# K3D Cluster configuration for WaveSpeed Workshop

# Cluster configuration
CLUSTER_NAME="workshop-cluster"
SERVERS=1
AGENTS=3
API_PORT=6550
# Port mapping disabled as requested
# PORT_MAPPING="8080:80@loadbalancer"
PORT_MAPPING=""
AGENTS_MEMORY="6G"
SERVERS_MEMORY="4G"

# Export variables so they can be used in Makefile
export CLUSTER_NAME
export SERVERS
export AGENTS
export API_PORT
export PORT_MAPPING
export AGENTS_MEMORY
export SERVERS_MEMORY 