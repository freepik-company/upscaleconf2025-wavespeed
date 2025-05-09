.PHONY: help check-dependencies install-k3d install-k6 setup-cluster clean-cluster run-load-test

# Default target
help:
	@echo "UpscaleConf 2025 WaveSpeed Workshop"
	@echo "---------------------------------"
	@echo "Available commands:"
	@echo "  make help                  - Show this help message"
	@echo "  make install-k3d           - Install k3d (k3s in Docker) for local development"
	@echo "  make install-k6            - Install k6 load testing tool"
	@echo "  make check-dependencies    - Check required dependencies"
	@echo "  make setup-cluster         - Set up local k3d cluster"
	@echo "  make clean-cluster         - Remove local k3d cluster"
	@echo "  make run-load-test         - Run basic load test on the deployed services"

# Check dependencies
check-dependencies:
	@echo "Checking dependencies..."
	@if ! command -v curl > /dev/null; then echo "curl is not installed"; exit 1; fi
	@if ! command -v docker > /dev/null; then echo "docker is not installed"; exit 1; fi
	@if ! command -v kubectl > /dev/null; then echo "kubectl is not installed"; exit 1; fi
	@echo "All dependencies are satisfied."

# Install k3d locally (works on macOS, Linux, Windows)
install-k3d: check-dependencies
	@echo "Installing k3d..."
	@if command -v k3d > /dev/null; then \
		echo "k3d is already installed."; \
	else \
		curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash; \
		echo "k3d has been installed successfully."; \
	fi

# Install k6 load testing tool
install-k6:
	@echo "Installing k6..."
	@if command -v k6 > /dev/null; then \
		echo "k6 is already installed."; \
	else \
		if [ "$(uname)" = "Darwin" ]; then \
			brew install k6; \
		elif [ "$(uname)" = "Linux" ]; then \
			curl -L https://github.com/grafana/k6/releases/download/v0.42.0/k6-v0.42.0-linux-amd64.tar.gz -o k6.tar.gz && \
			tar -xzf k6.tar.gz && \
			sudo cp k6-v0.42.0-linux-amd64/k6 /usr/local/bin/k6 && \
			rm -rf k6-v0.42.0-linux-amd64 k6.tar.gz; \
		else \
			echo "Please install k6 manually: https://k6.io/docs/getting-started/installation/"; \
		fi; \
		echo "k6 has been installed successfully."; \
	fi

# Set up local k3d cluster
setup-cluster: install-k3d
	@echo "Setting up k3d cluster..."
	@k3d cluster create workshop-cluster --agents 2 --api-port 6550 --port "8080:80@loadbalancer"
	@kubectl create namespace workshop || true
	@kubectl apply -f infrastructure/kubernetes/deployments/nginx-deployment.yaml
	@echo "k3d cluster is set up and running."
	@echo "You can access the cluster with: kubectl get nodes"
	@echo "The nginx service is available at: http://localhost:8080"

# Clean up
clean-cluster:
	@echo "Removing k3d cluster..."
	@if command -v k3d > /dev/null; then \
		k3d cluster delete workshop-cluster; \
		echo "k3d cluster has been removed."; \
	else \
		echo "k3d not found. Cluster might not exist."; \
	fi

# Run load test
run-load-test: install-k6
	@echo "Running basic load test..."
	@if ! curl -s http://localhost:8080 > /dev/null; then \
		echo "Error: Service is not available at http://localhost:8080"; \
		echo "Please make sure your cluster is running with: make setup-cluster"; \
		exit 1; \
	fi
	@k6 run load-testing/k6/http-test.js 