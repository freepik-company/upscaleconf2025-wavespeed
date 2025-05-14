#!/usr/bin/env python
import asyncio
import websockets
import json
import logging
import os
from aiohttp import web
import ssl
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# In-memory set of connected websocket clients
connected_clients = set()
client_info = {}  # Store additional information about clients

# Configuration from environment variables
HOST = os.environ.get("HOST", "0.0.0.0")
WS_PORT = int(os.environ.get("WS_PORT", 8765))
HTTP_PORT = int(os.environ.get("HTTP_PORT", 8766))
PING_INTERVAL = 30  # Seconds
CLIENT_TIMEOUT = 120  # Seconds

# Function to broadcast message to all connected clients
async def broadcast(message):
    if not connected_clients:
        logger.warning("No connected clients to broadcast to")
        return
    
    disconnected_clients = set()
    success_count = 0
    
    for client in connected_clients:
        try:
            await client.send(message)
            success_count += 1
            # Update last activity timestamp
            if client in client_info:
                client_info[client]['last_activity'] = time.time()
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected during broadcast: {client.remote_address}")
            disconnected_clients.add(client)
        except Exception as e:
            logger.error(f"Error broadcasting to client {client.remote_address}: {str(e)}")
            disconnected_clients.add(client)
    
    # Remove disconnected clients
    for client in disconnected_clients:
        if client in connected_clients:
            connected_clients.remove(client)
        if client in client_info:
            del client_info[client]
    
    logger.info(f"Broadcasted message to {success_count} clients (removed {len(disconnected_clients)} disconnected)")

# Periodic ping to keep connections alive
async def ping_clients():
    while True:
        try:
            disconnected_clients = set()
            now = time.time()
            
            # Check each client
            for client in connected_clients:
                try:
                    # Check if client has been inactive for too long
                    if client in client_info:
                        last_activity = client_info[client]['last_activity']
                        if (now - last_activity) > CLIENT_TIMEOUT:
                            logger.warning(f"Client {client.remote_address} timed out after {CLIENT_TIMEOUT}s of inactivity")
                            disconnected_clients.add(client)
                            continue
                    
                    # Send ping
                    pong_waiter = await client.ping()
                    await asyncio.wait_for(pong_waiter, timeout=5)
                    if client in client_info:
                        client_info[client]['last_ping'] = now
                        
                except asyncio.TimeoutError:
                    logger.warning(f"Ping timeout for client {client.remote_address}")
                    disconnected_clients.add(client)
                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"Client {client.remote_address} disconnected during ping")
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.error(f"Error pinging client {client.remote_address}: {str(e)}")
                    disconnected_clients.add(client)
            
            # Clean up disconnected clients
            for client in disconnected_clients:
                if client in connected_clients:
                    connected_clients.remove(client)
                if client in client_info:
                    del client_info[client]
            
            if disconnected_clients:
                logger.info(f"Ping cycle removed {len(disconnected_clients)} disconnected clients. {len(connected_clients)} clients remain.")
                
        except Exception as e:
            logger.error(f"Error in ping_clients: {str(e)}")
        
        await asyncio.sleep(PING_INTERVAL)

# WebSocket handler for client connections
async def websocket_handler(websocket, path):
    try:
        client_addr = websocket.remote_address
        logger.info(f"New client connected: {client_addr}")
        
        # Add client to connected clients
        connected_clients.add(websocket)
        client_info[websocket] = {
            'connected_at': time.time(),
            'last_activity': time.time(),
            'last_ping': time.time(),
            'address': client_addr,
            'path': path
        }
        
        # Send welcome message
        try:
            await websocket.send(json.dumps({
                "type": "connection_status", 
                "status": "connected",
                "connected_clients": len(connected_clients)
            }))
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
        
        # Keep the connection alive until client disconnects
        async for message in websocket:
            # Update last activity time
            client_info[websocket]['last_activity'] = time.time()
            
            try:
                # Try to parse the message as JSON
                data = json.loads(message)
                logger.debug(f"Received message from client {client_addr}: {str(data)[:100]}")
                
                # Echo back for testing
                await websocket.send(json.dumps({
                    "type": "echo", 
                    "original": data,
                    "timestamp": time.time()
                }))
                
            except json.JSONDecodeError:
                logger.debug(f"Received non-JSON message from client: {message[:100]}")
            except Exception as e:
                logger.error(f"Error processing message from {client_addr}: {str(e)}")
    
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"Client disconnected normally: {client_addr}")
    except websockets.exceptions.ConnectionClosedError as e:
        logger.warning(f"Client connection closed with error: {client_addr}, code: {e.code}, reason: {e.reason}")
    except Exception as e:
        logger.error(f"Error handling client {websocket.remote_address}: {str(e)}")
    finally:
        # Clean up
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        if websocket in client_info:
            del client_info[websocket]
        logger.info(f"Client removed: {client_addr}. Remaining clients: {len(connected_clients)}")

# HTTP POST handler to receive messages from Celery tasks
async def http_handler(request):
    try:
        # Get the request body
        data = await request.json()
        logger.info(f"Received message via HTTP POST: {list(data.keys())}")
        
        # Broadcast to all connected clients
        await broadcast(json.dumps(data))
        
        return web.json_response({
            "status": "success", 
            "clients": len(connected_clients),
            "timestamp": time.time()
        })
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in HTTP request: {str(e)}")
        return web.json_response({"status": "error", "message": "Invalid JSON", "error": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error handling HTTP request: {str(e)}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

# Health check endpoint
async def health_handler(request):
    return web.json_response({
        "status": "ok",
        "uptime": int(time.time() - start_time),
        "connected_clients": len(connected_clients),
        "timestamp": time.time()
    })

# Status endpoint
async def status_handler(request):
    client_list = []
    for client, info in client_info.items():
        client_list.append({
            "address": f"{info['address'][0]}:{info['address'][1]}",
            "connected_at": info['connected_at'],
            "last_activity": info['last_activity'],
            "path": info['path'],
            "idle": time.time() - info['last_activity']
        })
        
    return web.json_response({
        "status": "ok",
        "uptime": int(time.time() - start_time),
        "connected_clients": len(connected_clients),
        "clients": client_list,
        "timestamp": time.time()
    })

# Create HTTP application
app = web.Application()
app.router.add_post('/publish', http_handler)
app.router.add_get('/health', health_handler)
app.router.add_get('/status', status_handler)

# Start time for uptime reporting
start_time = time.time()

# Start both servers
async def start_servers():
    # Start WebSocket server
    ping_task = asyncio.create_task(ping_clients())
    
    # Start WebSocket server with ping_interval of None (we'll handle pings ourselves)
    ws_server = await websockets.serve(
        websocket_handler, 
        HOST, 
        WS_PORT, 
        ping_interval=None, 
        max_size=10 * 1024 * 1024  # 10 MB max message size
    )
    logger.info(f"WebSocket server started on ws://{HOST}:{WS_PORT}")
    
    # Start HTTP server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, HTTP_PORT)
    await site.start()
    logger.info(f"HTTP server started on http://{HOST}:{HTTP_PORT}")
    
    # Keep the servers running
    try:
        logger.info("Servers running. Press Ctrl+C to stop.")
        await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        logger.info("Server tasks cancelled")
    finally:
        # Cleanup
        ping_task.cancel()
        try:
            await ping_task
        except asyncio.CancelledError:
            pass
        
        ws_server.close()
        await ws_server.wait_closed()
        await runner.cleanup()
        logger.info("Servers shut down")

if __name__ == "__main__":
    logger.info("Starting WebSocket and HTTP servers...")
    try:
        asyncio.run(start_servers())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True) 