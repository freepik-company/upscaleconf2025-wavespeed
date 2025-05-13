.PHONY: help check-dependencies install-all-tools install-k3d install-helm install-helmfile setup-cluster setup-all clean-cluster helm-deploy scaffold-deploy helm-destroy grafana-ui prometheus-ui build-celery-app deploy-celery-app celery-api-ui celery-flower-ui celery-pod-logs celery-dashboards deploy-loadtest loadtest-ui health-check

# Default target
help:
	@echo "UpscaleConf 2025 WaveSpeed Workshop"
	@echo "---------------------------------"
	@echo "Available commands:"
	@echo "  make help                  - Show this help message"
	@echo "  make check-dependencies    - Check required dependencies"
	@echo "  make install-all-tools           - Install all required tools (k3d, Helm, Helmfile)"
	@echo "  make install-k3d           - Install k3d (k3s in Docker) for local development"
	@echo "  make install-helm          - Install Helm package manager"
	@echo "  make install-helmfile      - Install Helmfile for managing Helm releases"
	@echo "  make setup-cluster         - Set up local k3d cluster"
	@echo "  make setup-all             - Set up cluster and deploy all services"
	@echo "  make clean-cluster         - Remove local k3d cluster"
	@echo "  make helm-deploy           - Deploy services using Helmfile"
	@echo "  make scaffold-deploy       - Deploy only services labeled as scaffolding"
	@echo "  make helm-destroy          - Remove services deployed with Helmfile"
	@echo "  make grafana-ui            - Access Grafana UI (http://localhost:3000)"
	@echo "  make prometheus-ui         - Access Prometheus UI (http://localhost:9090)"
	@echo "  make build-celery-app      - Build Celery app Docker image"
	@echo "  make deploy-celery-app     - Deploy Celery app to k3d cluster"
	@echo "  make celery-api-ui         - Access Celery API UI (port-forward to 8000)"
	@echo "  make celery-flower-ui      - Access Celery Flower UI (port-forward to 5555)"
	@echo "  make celery-pod-logs       - Show logs from all Celery pods"
	@echo "  make celery-dashboards     - List Celery monitoring dashboards in Grafana"
	@echo "  make deploy-loadtest       - Build and deploy load test for Celery app"
	@echo "  make loadtest-ui           - Access Load Test UI (port-forward to 8089)"
	@echo "  make health-check          - Check the health endpoint of the nginx sidecar"

# Check dependencies
check-dependencies:
	@echo "Checking dependencies..."
	@if ! command -v curl > /dev/null; then echo "curl is not installed"; exit 1; fi
	@if ! command -v docker > /dev/null; then echo "docker is not installed"; exit 1; fi
	@if ! command -v kubectl > /dev/null; then echo "kubectl is not installed"; exit 1; fi
	@if command -v helm > /dev/null; then echo "Helm is installed"; else echo "Helm is not installed - run 'make install-helm'"; fi
	@if command -v helmfile > /dev/null; then echo "Helmfile is installed"; else echo "Helmfile is not installed - run 'make install-helmfile'"; fi
	@if command -v k3d > /dev/null; then echo "k3d is installed"; else echo "k3d is not installed - run 'make install-k3d'"; fi
	@echo "All required dependencies checked."

# Install all tools
install-all-tools:
	@echo "Installing all required tools..."
	@$(MAKE) install-k3d
	@$(MAKE) install-helmfile  # This also installs Helm as a dependency
	@echo "All tools installed successfully."

# Install k3d locally (works on macOS, Linux, Windows)
install-k3d: check-dependencies
	@echo "Installing k3d..."
	@if command -v k3d > /dev/null; then \
		echo "k3d is already installed."; \
	else \
		curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash; \
		echo "k3d has been installed successfully."; \
	fi


# Install Helm
install-helm:
	@echo "Installing Helm..."
	@if command -v helm > /dev/null; then \
		echo "Helm is already installed."; \
	else \
		if [ "$(uname)" = "Darwin" ]; then \
			brew install helm; \
		elif [ "$(uname)" = "Linux" ]; then \
			curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 && \
			chmod 700 get_helm.sh && \
			./get_helm.sh && \
			rm get_helm.sh; \
		else \
			echo "Please install Helm manually: https://helm.sh/docs/intro/install/"; \
		fi; \
		echo "Helm has been installed successfully."; \
	fi

# Install Helmfile
install-helmfile: install-helm
	@echo "Installing Helmfile..."
	@if command -v helmfile > /dev/null; then \
		echo "Helmfile is already installed."; \
	else \
		if [ "$(uname)" = "Darwin" ]; then \
			brew install helmfile; \
		elif [ "$(uname)" = "Linux" ]; then \
			HELMFILE_VERSION=v0.149.0 && \
			wget -O helmfile https://github.com/helmfile/helmfile/releases/download/$${HELMFILE_VERSION}/helmfile_linux_amd64 && \
			chmod +x helmfile && \
			sudo mv helmfile /usr/local/bin/; \
		else \
			echo "Please install Helmfile manually: https://helmfile.readthedocs.io/en/latest/#installation"; \
		fi; \
		echo "Helmfile has been installed successfully."; \
	fi

# Set up local k3d cluster
setup-cluster: install-k3d
	@echo "Setting up k3d cluster..."
	@k3d cluster create workshop-cluster --servers 1 --agents 3 --api-port 6550 --port "8080:80@loadbalancer" --agents-memory 6G --servers-memory 4G
	@kubectl create namespace workshop || true
	@kubectl create namespace monitoring || true
	@kubectl create namespace keda || true
	@echo "k3d cluster is set up and running."
	@echo "You can access the cluster with: kubectl get nodes"
	@echo ""
	@echo "To deploy services with Helmfile, run: make helm-deploy"

# Set up complete environment (cluster + all services)
setup-all: setup-cluster helm-deploy
	@echo ""
	@echo "Complete environment setup finished."
	@echo "- Kubernetes cluster is running"
	@echo "- All Helm releases are deployed"
	@echo ""
	@echo "To access the services:"
	@echo "- To connect to Redis: kubectl port-forward service/redis-master 6379:6379 -n workshop"
	@echo "  Then connect to localhost:6379 (no password required)"
	@echo "- To access Grafana: make grafana-ui"
	@echo "- To access Prometheus: make prometheus-ui"
	@echo "- To access Celery API: make celery-api-ui"
	@echo "- To access Celery Flower: make celery-flower-ui"
	@echo "- To check API health: make health-check"

# Clean up
clean-cluster:
	@echo "Cleaning up k3d cluster..."
	@k3d cluster delete workshop-cluster || true
	@docker kill $(docker ps -q --filter "name=k3d-workshop-cluster") 2>/dev/null || true
	@docker rm $(docker ps -a -q --filter "name=k3d-workshop-cluster") 2>/dev/null || true
	@echo "Cluster removed completely."

recreate-cluster: clean-cluster setup-cluster
	@echo "Cluster has been recreated with more resources."

# Deploy with Helmfile
helm-deploy: install-helmfile
	@echo "Deploying services with Helmfile..."
	@if ! kubectl get nodes > /dev/null 2>&1; then \
		echo "Error: Kubernetes cluster not accessible"; \
		echo "Please set up the cluster first with: make setup-cluster"; \
		exit 1; \
	fi
	@cd infrastructure/helmfile && helmfile apply
	@echo "Services deployed successfully."
	@echo "To connect to Redis (no password required): kubectl port-forward service/redis-master 6379:6379 -n workshop"

# Deploy only services labeled as scaffolding
scaffold-deploy: install-helmfile
	@echo "Deploying only scaffolding services with Helmfile..."
	@if ! kubectl get nodes > /dev/null 2>&1; then \
		echo "Error: Kubernetes cluster not accessible"; \
		echo "Please set up the cluster first with: make setup-cluster"; \
		exit 1; \
	fi
	@cd infrastructure/helmfile && helmfile apply --selector category=scaffolding
	@echo "Scaffolding services deployed successfully."
	@echo "Infrastructure components deployed:"
	@echo "- KEDA (Kubernetes Event-driven Autoscaling) for worker autoscaling"
	@echo "- Redis for message broker and result backend"
	@echo "- Prometheus for monitoring"
	@echo "- Grafana for visualization"
	@echo ""
	@echo "To connect to Redis (no password required): kubectl port-forward service/redis-master 6379:6379 -n workshop"
	@echo "To access Grafana: make grafana-ui (no authentication required)"
	@echo "To access Prometheus: make prometheus-ui"

# Destroy Helm releases
helm-destroy: install-helmfile
	@echo "Removing Helm releases..."
	@cd infrastructure/helmfile && helmfile destroy

# Access Grafana UI
grafana-ui:
	@echo "Port-forwarding Grafana UI..."
	@echo "Grafana UI will be available at: http://localhost:3000"
	@echo "Authentication is disabled - you'll be logged in automatically"
	@kubectl port-forward -n monitoring svc/grafana 3000:80

# Access Prometheus UI
prometheus-ui:
	@echo "Port-forwarding Prometheus UI..."
	@echo "Prometheus UI will be available at: http://localhost:9090"
	@kubectl port-forward -n monitoring svc/prometheus-server 9090:80 

# Build Celery app Docker image
build-celery-app:
	@echo "Building Celery app Docker image..."
	@docker build  --platform linux/amd64 -t celery-app:latest -f app/Dockerfile app/
	@echo "Importing image to k3d..."
	@k3d image import celery-app:latest --cluster workshop-cluster
	@echo "Celery app Docker image built and imported successfully."

# Deploy Celery app
deploy-celery-app: build-celery-app
	@echo "Deploying Celery app to k3d cluster..."
	@cd infrastructure/helmfile && helmfile apply --selector category=application
	@echo "Celery app deployed successfully."
	@echo "- To access Celery API: make celery-api-ui"
	@echo "- To access Celery Flower: make celery-flower-ui"
	@echo "- To check API health: make health-check"

# Access Celery API UI
celery-api-ui:
	@echo "Port-forwarding Celery API UI..."
	@echo "Celery API will be available at: http://localhost:8000"
	@kubectl port-forward -n workshop svc/celery-app-api 8000:80

# Access health endpoint of nginx sidecar
health-check:
	@echo "Checking health endpoint..."
	@kubectl port-forward -n workshop svc/celery-app-api 8000:80 & \
	PID=$$! && \
	sleep 2 && \
	curl -v http://localhost:8000/health && \
	kill $$PID
	@echo "Health check complete. The /health endpoint should return 200 OK"

# Access Celery Flower UI
celery-flower-ui:
	@echo "Port-forwarding Celery Flower UI..."
	@echo "Celery Flower will be available at: http://localhost:5555"
	@kubectl port-forward -n workshop svc/celery-app-flower 5555:5555

# Show Celery pod logs
celery-pod-logs:
	@echo "Showing Celery pod logs..."
	@echo "API pods:"
	@kubectl get pods -n workshop -l app.kubernetes.io/name=celery-app,component=api
	@echo "\nWorker pods:"
	@kubectl get pods -n workshop -l app.kubernetes.io/name=celery-app,component=worker
	@echo "\nFlower pods:"
	@kubectl get pods -n workshop -l app.kubernetes.io/name=celery-app,component=flower
	@echo "\nExporter pods:"
	@kubectl get pods -n workshop -l app.kubernetes.io/name=celery-app,component=exporter
	@echo "\nTo see logs from a specific pod, run:"
	@echo "kubectl logs -n workshop POD_NAME"

# Deploy Celery load test
deploy-loadtest:
	@echo "Building and deploying Celery load test..."
	@docker build --platform linux/amd64 -t celery-loadtest:latest -f infrastructure/loadtest/Dockerfile infrastructure/loadtest/
	@echo "Importing image to k3d..."
	@k3d image import celery-loadtest:latest --cluster workshop-cluster
	@echo "Applying load test deployment..."
	@kubectl apply -f infrastructure/loadtest/kubernetes/deployment.yaml
	@echo "Celery load test deployed successfully."
	@echo "To access the load test UI: kubectl port-forward -n workshop svc/celery-loadtest 8089:8089"
	@echo "Then visit: http://localhost:8089"

# Access Load Test UI
loadtest-ui:
	@echo "Port-forwarding Load Test UI..."
	@echo "Load Test UI will be available at: http://localhost:8089"
	@kubectl port-forward -n workshop svc/celery-loadtest 8089:8089