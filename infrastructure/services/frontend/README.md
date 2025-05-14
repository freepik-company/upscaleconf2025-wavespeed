# Frontend Visualization Service

This service provides a visualization frontend for inference results using a static web app and WebSockets.

## Components

The service consists of two main components:

1. **WebSocket Server**: Receives inference results via HTTP POST requests and forwards them to connected WebSocket clients
2. **Static Web App**: Connects to the WebSocket server and displays inference results in a grid

## Architecture

```
┌─────────────┐        ┌───────────────┐       ┌─────────────────┐
│ Celery Task │───────▶│ WebSocket     │◀──────│ Static Web App  │
│ (POST)      │        │ Server        │       │ (visualization) │
└─────────────┘        └───────────────┘       └─────────────────┘
                           │
                           │
                       ┌───▼───┐
                       │ Other │
                       │ Clients│
                       └───────┘
```

## Usage

### Deployment

Deploy the visualization service using:

```
make deploy-frontend
```

This will:
1. Build Docker images for the static web app and WebSocket server
2. Import the images into the k3d cluster
3. Deploy the Helm chart for the visualization service

### Accessing the UI

Access the web UI using:

```
make frontend-ui
```

This will forward ports to your local machine, allowing you to access the UI at http://localhost:8081.

### Sending Data to the WebSocket Server

To send data to the WebSocket server, use the `/websocket/flux` endpoint of the Celery API:

```
POST /websocket/flux
{
  "prompt": "A sample prompt",
  "seed": 42
}
```

## WebSocket API

The WebSocket server provides the following endpoints:

- WebSocket: `ws://visualize-websocket.frontend.svc.cluster.local:8765`
- HTTP POST: `http://visualize-websocket.frontend.svc.cluster.local:8766/publish`

The HTTP POST endpoint accepts JSON payloads, which are then forwarded to all connected WebSocket clients. 