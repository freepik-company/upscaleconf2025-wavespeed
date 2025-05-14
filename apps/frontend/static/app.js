// Configuration
const config = {
    // WebSocket server URL - will try to connect to either Kubernetes cluster URL or port-forwarded URL
    wsUrls: [
        "ws://localhost:8765", // Port-forwarded URL (for local testing)
        "ws://visualize-websocket.frontend.svc.cluster.local:8765" // In-cluster URL
    ],
    reconnectDelay: 3000, // ms
    maxReconnectAttempts: 10,
    gridSize: 10 // Just 10 preview cells
};

// State management
const state = {
    images: Array(10).fill(null), // Store only 10 images
    currentIndex: 0,
    isConnected: false,
    connectionError: null,
    lastUpdate: null,
    connectionAttempts: 0,
    socket: null,
    totalImagesReceived: 0,
    currentWsUrlIndex: 0 // Track which URL we're currently trying
};

// DOM elements cache
const elements = {
    grid: document.getElementById('image-grid'),
    status: {
        container: document.getElementById('connection-status'),
        text: document.getElementById('status-text')
    },
    stats: {
        imagesReceived: document.getElementById('images-received'),
        currentPosition: document.getElementById('current-position'),
        lastUpdate: document.getElementById('last-update'),
        connectionAttempts: document.getElementById('connection-attempts')
    },
    websocketUrl: document.getElementById('websocket-url')
};

// Initialize the UI
function initializeUI() {
    // Create grid cells - only 10 cells
    for (let i = 0; i < 10; i++) {
        const cell = document.createElement('div');
        cell.classList.add('grid-cell');
        cell.id = `cell-${i}`;
        cell.innerHTML = '<div class="empty-cell">⌛</div>';
        elements.grid.appendChild(cell);
    }
    
    // Set WebSocket URL display
    elements.websocketUrl.textContent = "Trying: " + config.wsUrls[state.currentWsUrlIndex];
    
    // Update UI to initial state
    updateUI();
}

// Update UI with current state
function updateUI() {
    // Update connection status
    if (state.isConnected) {
        elements.status.container.className = 'status-connected';
        elements.status.text.textContent = 'Connected to WebSocket';
    } else if (state.connectionError) {
        elements.status.container.className = 'status-error';
        elements.status.text.textContent = `Connection Error: ${state.connectionError}`;
    } else {
        elements.status.container.className = 'status-connecting';
        elements.status.text.textContent = 'Connecting to WebSocket...';
    }
    
    // Update stats
    elements.stats.imagesReceived.textContent = state.totalImagesReceived;
    elements.stats.currentPosition.textContent = state.currentIndex;
    elements.stats.connectionAttempts.textContent = state.connectionAttempts;
    
    if (state.lastUpdate) {
        const timeString = new Date(state.lastUpdate).toLocaleTimeString();
        elements.stats.lastUpdate.textContent = timeString;
    }
}

// Handle received messages
function handleMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        
        // Check for image data
        if (data.response && (data.response.image || (typeof data.response === 'object' && data.response.image))) {
            let imageData;
            
            // Extract image data from the response
            if (typeof data.response === 'string') {
                try {
                    const parsedResponse = JSON.parse(data.response);
                    imageData = parsedResponse.image;
                } catch (e) {
                    console.error('Failed to parse response JSON:', e);
                }
            } else if (data.response.image) {
                imageData = data.response.image;
            }
            
            if (imageData) {
                displayImage(imageData);
            }
        } else if (data.image) {
            displayImage(data.image);
        }
    } catch (error) {
        console.error('Error processing message:', error);
    }
}

// Display an image in the grid
function displayImage(imageData) {
    try {
        // Remove data URL prefix if present
        if (imageData.startsWith('data:image')) {
            imageData = imageData.split(',', 2)[1];
        }
        
        // Create image element
        const img = new Image();
        img.src = `data:image/jpeg;base64,${imageData}`;
        
        // Update cell content - use the current index for placement
        const cellIndex = state.currentIndex;
        const cell = document.getElementById(`cell-${cellIndex}`);
        if (cell) {
            cell.innerHTML = '';
            cell.appendChild(img);
        }
        
        // Update state
        state.images[cellIndex] = imageData;
        state.currentIndex = (cellIndex + 1) % 10; // Wrap around after 10 cells
        state.lastUpdate = Date.now();
        state.totalImagesReceived++;
        
        // Update UI
        updateUI();
        
        // Log position info for debugging
        console.log(`Image placed at cell ${cellIndex}, new position will be ${state.currentIndex}`);
    } catch (error) {
        console.error('Error displaying image:', error);
    }
}

// Connect to WebSocket server
function connectWebSocket() {
    // Close existing connection if any
    if (state.socket) {
        state.socket.close();
    }
    
    state.connectionAttempts++;
    
    // Get current WebSocket URL
    const wsUrl = config.wsUrls[state.currentWsUrlIndex];
    elements.websocketUrl.textContent = "Trying: " + wsUrl;
    
    updateUI();
    
    try {
        console.log(`Connecting to WebSocket: ${wsUrl} (attempt ${state.connectionAttempts})`);
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function() {
            console.log('WebSocket connection established');
            state.isConnected = true;
            state.connectionError = null;
            elements.websocketUrl.textContent = "Connected to: " + wsUrl;
            updateUI();
        };
        
        socket.onmessage = handleMessage;
        
        socket.onerror = function(error) {
            console.error('WebSocket error:', error);
            state.connectionError = 'Connection failed';
            state.isConnected = false;
            
            // Try the next URL
            state.currentWsUrlIndex = (state.currentWsUrlIndex + 1) % config.wsUrls.length;
            
            updateUI();
        };
        
        socket.onclose = function(event) {
            console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
            state.isConnected = false;
            updateUI();
            
            // Try the next URL if this one failed
            if (!state.isConnected) {
                state.currentWsUrlIndex = (state.currentWsUrlIndex + 1) % config.wsUrls.length;
            }
            
            // Attempt to reconnect if not max attempts
            if (state.connectionAttempts < config.maxReconnectAttempts) {
                setTimeout(connectWebSocket, config.reconnectDelay);
            } else {
                state.connectionError = 'Max reconnection attempts reached';
                updateUI();
            }
        };
        
        state.socket = socket;
    } catch (error) {
        console.error('Error creating WebSocket:', error);
        state.connectionError = error.message;
        state.isConnected = false;
        updateUI();
        
        // Try the next URL
        state.currentWsUrlIndex = (state.currentWsUrlIndex + 1) % config.wsUrls.length;
        
        // Attempt to reconnect
        if (state.connectionAttempts < config.maxReconnectAttempts) {
            setTimeout(connectWebSocket, config.reconnectDelay);
        }
    }
}

// Initialize the application
function init() {
    initializeUI();
    connectWebSocket();
}

// Start the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init); 