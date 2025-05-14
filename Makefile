.PHONY: help check-dependencies install-tools setup-cluster start-workshop deploy-services deploy-app deploy-balancer run-loadtest show-ui clean-all

# Default target
help:
	@echo "UpscaleConf 2025 WaveSpeed Workshop - Streamlined Makefile"
	@echo "------------------------------------------------------"
	@echo "Main workflow commands:"
	@echo "  make help                  - Show this help message"
	@echo "  make check-dependencies    - Check required dependencies"
	@echo "  make install-tools         - Install all required tools (k3d, Helm, Helmfile)"
	@echo "  make setup-cluster         - Create local k3d cluster with required resources"
	@echo "  make start-workshop        - Complete workshop setup (cluster + all services)"
	@echo "  make deploy-services       - Deploy platform services (Redis, Prometheus, Grafana, KEDA)"
	@echo "  make deploy-app            - Build and deploy Celery application"
	@echo "  make deploy-balancer       - Deploy the inference balancer"
	@echo "  make run-loadtest          - Run load testing against the application"
	@echo "  make show-ui               - Show URLs for all UIs"
	@echo "  make clean-all             - Remove all workshop resources"
	@echo ""
	@echo "Individual UIs:"
	@echo "  make grafana-ui            - Access Grafana UI (http://localhost:3000)"
	@echo "  make prometheus-ui         - Access Prometheus UI (http://localhost:9090)"
	@echo "  make api-ui                - Access Celery API UI (http://localhost:8000)"
	@echo "  make flower-ui             - Access Celery Flower UI (http://localhost:5555)"
	@echo "  make loadtest-ui           - Access Load Test UI (http://localhost:8089)"
	@echo ""
	@echo "For more detailed commands, see Makefile.original"

# Check dependencies
check-dependencies:
	@echo "Checking dependencies..."
	@if ! command -v curl > /dev/null; then echo "curl is not installed"; exit 1; fi
	@if ! command -v docker > /dev/null; then echo "docker is not installed"; exit 1; fi
	@if ! command -v kubectl > /dev/null; then echo "kubectl is not installed"; exit 1; fi
	@if command -v helm > /dev/null; then echo "Helm is installed"; else echo "Helm is not installed - run 'make install-tools'"; fi
	@if command -v helmfile > /dev/null; then echo "Helmfile is installed"; else echo "Helmfile is not installed - run 'make install-tools'"; fi
	@if command -v k3d > /dev/null; then echo "k3d is installed"; else echo "k3d is not installed - run 'make install-tools'"; fi
	@echo "All required dependencies checked."

# Install tools
install-tools:
	@echo "Installing all required tools..."
	@echo "Installing k3d..."
	@if ! command -v k3d > /dev/null; then curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash; fi
	@echo "Installing Helm..."
	@if ! command -v helm > /dev/null; then \
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
	fi
	@echo "Installing Helmfile..."
	@if ! command -v helmfile > /dev/null; then \
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
	fi
	@echo "All tools installed successfully."

# Set up local k3d cluster
setup-cluster: check-dependencies
	@echo "Setting up k3d cluster..."
	@source infrastructure/cluster/k3d/cluster-config.sh && \
		k3d cluster create $${CLUSTER_NAME} \
		--servers $${SERVERS} \
		--agents $${AGENTS} \
		--api-port $${API_PORT} \
		--port "$${PORT_MAPPING}" \
		--agents-memory $${AGENTS_MEMORY} \
		--servers-memory $${SERVERS_MEMORY}
	@kubectl create namespace workshop || true
	@kubectl create namespace monitoring || true
	@kubectl create namespace keda || true
	@kubectl create namespace inference-balancer || true
	@echo "k3d cluster is set up and running."
	@echo "You can access the cluster with: kubectl get nodes"
	@echo ""
	@echo "Next step: deploy services with 'make deploy-services'"

# Deploy platform services (Redis, KEDA, Prometheus, Grafana)
deploy-services: check-dependencies
	@echo "Deploying platform services..."
	@if ! kubectl get nodes > /dev/null 2>&1; then \
		echo "Error: Kubernetes cluster not accessible"; \
		echo "Please set up the cluster first with: make setup-cluster"; \
		exit 1; \
	fi
	@cd infrastructure/deployment/helmfile && helmfile apply --selector category=scaffolding
	@echo "Platform services deployed successfully."
	@echo "Services deployed:"
	@echo "- KEDA (Kubernetes Event-driven Autoscaling)"
	@echo "- Redis (message broker and result backend)"
	@echo "- Prometheus (monitoring)"
	@echo "- Grafana (visualization)"
	@echo ""
	@echo "Next step: deploy application with 'make deploy-app'"

# Build and deploy Celery app
deploy-app: check-dependencies
	@echo "Building and deploying Celery application..."
	@docker build --platform linux/amd64 -t celery-app:latest -f apps/backend/Dockerfile apps/backend/
	@k3d image import celery-app:latest --cluster workshop-cluster
	@cd infrastructure/deployment/helmfile && helmfile apply --selector category=application
	@echo "Celery application deployed successfully."
	@echo "Next step: deploy balancer with 'make deploy-balancer'"

# Deploy balancer
deploy-balancer: check-dependencies
	@echo "Deploying inference balancer..."
	@helm upgrade --install inference-balancer infrastructure/services/balancer/helm -n inference-balancer --wait
	@echo "Inference balancer deployed successfully."
	@echo "Next step: run load test with 'make run-loadtest'"

# Run load test
run-loadtest: check-dependencies
	@echo "Building and deploying load test..."
	@docker build --platform linux/amd64 -t celery-loadtest:latest -f testing/load-testing/Dockerfile testing/load-testing/
	@k3d image import celery-loadtest:latest --cluster workshop-cluster
	@kubectl apply -f testing/load-testing/kubernetes/deployment.yaml
	@echo "Load test deployed successfully."
	@echo "To access the load test UI: make loadtest-ui"
	@echo "To monitor the system: make grafana-ui"

# Complete workshop workflow in one step
start-workshop: setup-cluster deploy-services deploy-app deploy-balancer
	@echo "Workshop environment is fully set up!"
	@echo "Next step: run load test with 'make run-loadtest'"
	@echo "To view all UIs: make show-ui"

# Show all UIs
show-ui:
	@echo "Workshop UI endpoints:"
	@echo "- Grafana (monitoring): http://localhost:3000 (run 'make grafana-ui')"
	@echo "- Prometheus: http://localhost:9090 (run 'make prometheus-ui')"
	@echo "- Celery API: http://localhost:8000 (run 'make api-ui')"
	@echo "- Celery Flower: http://localhost:5555 (run 'make flower-ui')"
	@echo "- Load Test UI: http://localhost:8089 (run 'make loadtest-ui')"

# UI access commands
grafana-ui:
	@echo "Opening Grafana UI..."
	@echo "Grafana UI will be available at: http://localhost:3000"
	@kubectl port-forward -n monitoring svc/grafana 3000:80

prometheus-ui:
	@echo "Opening Prometheus UI..."
	@echo "Prometheus UI will be available at: http://localhost:9090"
	@kubectl port-forward -n monitoring svc/prometheus-server 9090:80

api-ui:
	@echo "Opening Celery API UI..."
	@echo "Celery API will be available at: http://localhost:8000"
	@kubectl port-forward -n workshop svc/celery-app-api 8000:80

flower-ui:
	@echo "Opening Celery Flower UI..."
	@echo "Celery Flower will be available at: http://localhost:5555"
	@kubectl port-forward -n workshop svc/celery-app-flower 5555:5555

loadtest-ui:
	@echo "Opening Load Test UI..."
	@echo "Load Test UI will be available at: http://localhost:8089"
	@kubectl port-forward -n workshop svc/celery-loadtest 8089:8089

# Clean up
clean-all:
	@echo "Cleaning up all workshop resources..."
	@source infrastructure/cluster/k3d/cluster-config.sh && \
		k3d cluster delete $${CLUSTER_NAME} || true && \
		docker kill $$(docker ps -q --filter "name=k3d-$${CLUSTER_NAME}") 2>/dev/null || true && \
		docker rm $$(docker ps -a -q --filter "name=k3d-$${CLUSTER_NAME}") 2>/dev/null || true
	@echo "Workshop environment cleaned up successfully." 