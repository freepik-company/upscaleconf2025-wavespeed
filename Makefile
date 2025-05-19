.PHONY: help check-dependencies install-tools setup-cluster start-workshop deploy-services deploy-app deploy-balancer deploy-webhook deploy-frontend run-loadtest show-ui clean-all istio-verify istio-dashboards restart-inference-balancer enable-istio-injection fix-metrics-access fix-nginx-config

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
	@echo "  make deploy-services       - Deploy platform services (Redis, Prometheus, Grafana, KEDA, Istio)"
	@echo "  make deploy-app            - Build and deploy Celery application"
	@echo "  make deploy-balancer       - Deploy the inference balancer"
	@echo "  make deploy-webhook        - Deploy the webhook service"
	@echo "  make deploy-frontend       - Deploy the visualization frontend"
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
	@echo "  make frontend-ui           - Access Visualization UI (http://localhost:8080) with WebSocket support"
	@echo ""
	@echo "Istio commands:"
	@echo "  make istio-verify          - Verify Istio installation and sidecar injection"
	@echo "  make restart-inference-balancer - Restart deployments to enable Istio sidecar injection"
	@echo "  make enable-istio-injection - Ensure istio-injection label is added to the namespace"
	@echo "  make fix-metrics-access    - Fix metrics endpoint access for Istio sidecars"
	@echo "  make fix-nginx-config      - Fix NGINX configuration for proper path handling"
	@echo "  make run-istio-test        - Generate test traffic for Istio metrics"
	@echo ""
	@echo "Setting up DataCrunch API Token:"
	@echo "  For Flux Service A proxy to work, you need to set the DataCrunch bearer token using one of:"
	@echo "  - Environment variable: export DC_BEARER_TOKEN=your-token"
	@echo "  - .env file in the project root with DC_BEARER_TOKEN=your-token"
	@echo "  - Copy the template file: cp .env.dist .env and edit with your token"
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
	@kubectl create namespace webhook || true
	@kubectl create namespace frontend || true
	@kubectl create namespace istio-system || true
	@echo "k3d cluster is set up and running."
	@echo "You can access the cluster with: kubectl get nodes"
	@echo ""
	@echo "Next step: deploy services with 'make deploy-services'"

import-public-images: check-dependencies
	@echo "Pulling and importing public images to k3d cluster..."
	@source infrastructure/cluster/k3d/cluster-config.sh && \
	docker pull prom/pushgateway:v1.5.1 && \
	docker pull  jimmidyson/configmap-reload:v0.8.0 && \
	docker pull busybox:1.31.1 && \
	docker pull docker.io/bitnami/redis:7.0.5-debian-11-r25 && \
	docker pull curlimages/curl:7.85.0 && \
	docker pull docker.io/bitnami/redis-exporter:1.45.0-debian-11-r11 && \
	docker pull nginx:1.21-alpine && \
	docker pull danihodovic/celery-exporter:0.11.3 && \
	docker pull quay.io/prometheus/prometheus:v2.40.5 && \
	docker pull nginx:stable && \
	docker pull quay.io/martinhelmich/prometheus-nginxlog-exporter:v1.11.0 && \
	docker pull nginx:1.21-alpine && \
	docker pull docker.io/istio/proxyv2:1.20.0 && \
	docker pull docker.io/istio/pilot:1.20.0 && \
	docker pull docker.io/istio/install-cni:1.20.0 && \
	k3d image import \
	  prom/pushgateway:v1.5.1 \
	  jimmidyson/configmap-reload:v0.8.0 \
	  busybox:1.31.1 \
	  docker.io/bitnami/redis:7.0.5-debian-11-r25 \
	  docker.io/bitnami/redis-exporter:1.45.0-debian-11-r11 \
	  curlimages/curl:7.85.0 \
	  nginx:1.21-alpine \
	  danihodovic/celery-exporter:0.11.3 \
	  quay.io/prometheus/prometheus:v2.40.5 \
	  nginx:stable \
	  nginx:1.21-alpine \
	  quay.io/martinhelmich/prometheus-nginxlog-exporter:v1.11.0 \
	  docker.io/istio/proxyv2:1.20.0 \
	  docker.io/istio/pilot:1.20.0 \
	  docker.io/istio/install-cni:1.20.0 \
	  --cluster $${CLUSTER_NAME}
	@echo "Public images imported successfully."

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
# deploy-balancer: check-dependencies
# 	@echo "Deploying inference balancer..."
# 	@if [ -z "$$DC_BEARER_TOKEN" ] && [ -f .env ]; then \
# 		echo "Loading DC_BEARER_TOKEN from .env file..."; \
# 		export $$(grep -v '^#' .env | grep DC_BEARER_TOKEN); \
# 	fi; \
# 	if [ -z "$$DC_BEARER_TOKEN" ]; then \
# 		echo "Warning: DC_BEARER_TOKEN not set. The DataCrunch API proxy will not work correctly."; \
# 		echo "Please set the token using:"; \
# 		echo "  - Environment variable: export DC_BEARER_TOKEN=your-token"; \
# 		echo "  - .env file with DC_BEARER_TOKEN=your-token"; \
# 		helm upgrade --install inference-balancer infrastructure/services/inference-balancer -n inference-balancer --wait; \
# 	else \
# 		echo "Using DataCrunch bearer token from environment..."; \
# 		helm upgrade --install inference-balancer infrastructure/services/inference-balancer \
# 			--set datacrunch.bearerToken="$$DC_BEARER_TOKEN" \
# 			-n inference-balancer --wait; \
# 	fi
# 	@echo "Inference balancer deployed successfully."
# 	@echo "Next step: run load test with 'make run-loadtest'"

# Deploy webhook service
deploy-webhook: check-dependencies
	@echo "Deploying webhook service..."
	@kubectl create namespace webhook || true
	@helm upgrade --install webhook infrastructure/services/webhook -n webhook --wait
	@echo "Webhook service deployed successfully."
	@echo "Webhook endpoint available at: http://webhook.webhook.svc.cluster.local/publish-response"

# Deploy frontend visualization
deploy-frontend: check-dependencies
	@echo "Building and deploying frontend visualization..."
	@docker build --platform linux/amd64 -t localhost:5000/static-web-app:latest -f apps/frontend/Dockerfile.static apps/frontend/
	@docker build --platform linux/amd64 -t localhost:5000/websocket-server:latest -f apps/frontend/Dockerfile.websocket apps/frontend/
	@k3d image import localhost:5000/static-web-app:latest localhost:5000/websocket-server:latest --cluster workshop-cluster
	@kubectl create namespace frontend || true
	@helm upgrade --install visualize infrastructure/services/frontend/visualize -n frontend --wait
	@echo "Frontend visualization deployed successfully."
	@echo "Static web app available at: http://visualize-static.frontend.svc.cluster.local"
	@echo "WebSocket server available at: ws://visualize-websocket.frontend.svc.cluster.local:8765"
	@echo "WebSocket HTTP endpoint: http://visualize-websocket.frontend.svc.cluster.local:8766/publish"

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
start-workshop: setup-cluster import-public-images deploy-services deploy-app istio-verify enable-istio-injection deploy-inference-balancer deploy-webhook deploy-frontend
	@echo "Workshop environment is fully set up!"
	@echo "Note: For the DataCrunch API proxy to work correctly, make sure DC_BEARER_TOKEN is set"
	@echo "      via environment variable or .env file before running deploy-balancer."
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
	@echo "- Visualization UI: http://localhost:8081 (run 'make frontend-ui')"

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

# New frontend UI target that forwards both services
frontend-ui:
	@echo "Starting frontend visualization UI with WebSocket support..."
	@echo "Static web app will be available at: http://localhost:8081"
	@echo "WebSocket server will be available at: ws://localhost:8765"
	@echo "WebSocket HTTP endpoint will be available at: http://localhost:8767/publish"
	@echo "Starting port forwarding (press Ctrl+C to stop)..."
	@kubectl port-forward -n frontend svc/visualize-static 8081:80 & \
	kubectl port-forward -n frontend svc/visualize-websocket 8765:8765 8767:8766 & \
	echo "All services forwarded. Press Ctrl+C to stop." && \
	wait

# Clean up
clean-all:
	@echo "Cleaning up all workshop resources..."
	@source infrastructure/cluster/k3d/cluster-config.sh && \
		k3d cluster delete $${CLUSTER_NAME} || true && \
		docker kill $$(docker ps -q --filter "name=k3d-$${CLUSTER_NAME}") 2>/dev/null || true && \
		docker rm $$(docker ps -a -q --filter "name=k3d-$${CLUSTER_NAME}") 2>/dev/null || true
	@echo "Workshop environment cleaned up successfully."

# Verify Istio installation and sidecar injection
istio-verify:
	@echo "Verifying Istio installation..."
	@kubectl get pods -n istio-system
	@echo ""
	@echo "Verifying inference-balancer namespace has Istio injection enabled:"
	@if kubectl get namespace inference-balancer -o jsonpath='{.metadata.labels.istio-injection}' | grep -q "enabled"; then \
		echo "✅ istio-injection label is set to 'enabled' on namespace"; \
	else \
		echo "❌ istio-injection label is NOT set on namespace"; \
		echo "Run 'make enable-istio-injection' to add the label"; \
	fi
	@echo ""
	@echo "Verifying inference-balancer pods have Istio sidecar:"
	@if kubectl get pods -n inference-balancer -o jsonpath='{.items[*].spec.containers[*].name}' | grep -q "istio-proxy"; then \
		echo "✅ Istio sidecars found in pods"; \
	else \
		echo "❌ No Istio sidecars found"; \
		echo "To fix this:"; \
		echo "1. Run 'make enable-istio-injection' to ensure the label is set"; \
		echo "2. Run 'make restart-inference-balancer' to restart deployments with sidecars"; \
	fi

# Restart inference-balancer deployments to ensure sidecar injection

# Ensure istio-injection label is added to the namespace
enable-istio-injection:
	@echo "Ensuring istio-injection label is added to inference-balancer namespace..."
	@if kubectl get namespace inference-balancer -o jsonpath='{.metadata.labels.istio-injection}' | grep -q "enabled"; then \
		echo "✅ istio-injection label is already set to 'enabled' on namespace"; \
	else \
		echo "Adding istio-injection=enabled label to inference-balancer namespace..."; \
		kubectl label namespace inference-balancer istio-injection=enabled --overwrite; \
		echo "✅ istio-injection label added successfully"; \
	fi
	@echo ""
	@echo "You may need to restart deployments for sidecar injection to take effect:"
	@echo "  make restart-inference-balancer"

deploy-inference-balancer: check-dependencies
	@echo "Deploying inference balancer..."
	@if [ -z "$$DC_BEARER_TOKEN" ] && [ -f .env ]; then \
		echo "Loading DC_BEARER_TOKEN from .env file..."; \
		export $$(grep -v '^#' .env | grep DC_BEARER_TOKEN); \
	fi; \
	if [ -z "$$DC_BEARER_TOKEN" ]; then \
		echo "Warning: DC_BEARER_TOKEN not set. The DataCrunch API proxy will not work correctly."; \
		echo "Please set the token using:"; \
		echo "  - Environment variable: export DC_BEARER_TOKEN=your-token"; \
		echo "  - .env file with DC_BEARER_TOKEN=your-token"; \
		helm upgrade --install inference-balancer infrastructure/services/inference-balancer -n inference-balancer --wait; \
	else \
		echo "Using DataCrunch bearer token from environment..."; \
		helm upgrade --install inference-balancer infrastructure/services/inference-balancer \
			--set datacrunch.bearerToken="$$DC_BEARER_TOKEN" \
			-n inference-balancer --wait; \
	fi
	@echo "Inference balancer deployed successfully."
	@echo "Next step: run load test with 'make run-loadtest'"
