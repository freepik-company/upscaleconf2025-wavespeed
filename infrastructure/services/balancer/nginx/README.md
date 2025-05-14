# Nginx Balancer Container

This container provides an Nginx-based load balancer for distributing traffic across multiple backend services.

## Configuration

The balancer is configured to route traffic to three backend services with different weights:

- dc-bumblebee-ai-proxy: weight=99, will receive 99% of traffic
- fal-bumblebee-ai-proxy: weight=1, will receive 1% of traffic
- runware-bumblebee-ai-proxy: weight=1, marked as down, will only be used if other servers fail

The load balancer handles traffic for the `/flux` endpoint and includes various proxy headers and timeout configurations.

## Usage

### Building and Running with Docker Compose

```bash
cd infrastructure/nginx-balancer
docker-compose up -d
```

The balancer will be available at http://localhost:8080/flux

### Building and Running with Docker

```bash
cd infrastructure/nginx-balancer
docker build -t balancer .
docker run -d --name balancer -p 8080:80 balancer
```

## Lua Scripts

The configuration references Lua scripts that are included as placeholders:

- `/etc/nginx/lua/flux-blackwell-request.lua`
- `/etc/nginx/lua/flux-request.lua`

Replace these with actual implementations if needed. 