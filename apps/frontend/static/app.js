// Configuration
const config = {
    // WebSocket server URL - will try to connect to either Kubernetes cluster URL or port-forwarded URL
    wsUrls: [
        "ws://localhost:8765", // Port-forwarded URL (for local testing)
        "ws://visualize-websocket.frontend.svc.cluster.local:8765" // In-cluster URL
    ],
    reconnectDelay: 3000, // ms
    maxReconnectAttempts: 10,
    gridSize: 8 // 2x4 grid
};

// State management
const state = {
    images: Array(8).fill(null),
    isConnected: false,
    connectionError: null,
    connectionAttempts: 0,
    socket: null,
    totalImagesReceived: 0,
    currentWsUrlIndex: 0
};

// DOM elements cache
const elements = {
    grid: document.getElementById('image-grid'),
    status: {
        container: document.getElementById('connection-status'),
        text: document.getElementById('status-text')
    },
    imagesReceived: document.getElementById('images-received')
};

// Initialize the UI
function initializeUI() {
    // Create grid cells - 8 cells
    for (let i = 0; i < config.gridSize; i++) {
        const cell = document.createElement('div');
        cell.classList.add('grid-cell');
        cell.id = `cell-${i}`;
        cell.innerHTML = '<div class="empty-cell"></div>';
        elements.grid.appendChild(cell);
    }
    
    // Update UI to initial state
    updateUI();
}

// Update UI with current state
function updateUI() {
    // Update connection status
    if (state.isConnected) {
        elements.status.container.className = 'status-connected';
        elements.status.text.textContent = 'Connected';
    } else if (state.connectionError) {
        elements.status.container.className = 'status-error';
        elements.status.text.textContent = `Error: ${state.connectionError}`;
    } else {
        elements.status.container.className = 'status-connecting';
        elements.status.text.textContent = 'Connecting...';
    }
    
    // Update image counter
    elements.imagesReceived.textContent = state.totalImagesReceived;
}

// Handle received messages
function handleMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
        
        // Check for image data in various formats
        if (data.response) {
            // Check for enhanced response with image_url
            if (data.response.image_url) {
                console.log('Found image URL in enhanced response:', data.response.image_url);
                displayImageFromUrl(data.response.image_url);
                return;
            }
            
            // Check for base64 image data
            if (data.response.image || (typeof data.response === 'object' && data.response.image)) {
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
                    return;
                }
            }
            
            // Try to parse string response if it's JSON
            if (typeof data.response === 'string') {
                try {
                    const parsedResponse = JSON.parse(data.response);
                    
                    if (parsedResponse.output && parsedResponse.output.outputs && parsedResponse.output.outputs.length > 0) {
                        const imageUrl = parsedResponse.output.outputs[0];
                        console.log('Found image URL in parsed response:', imageUrl);
                        displayImageFromUrl(imageUrl);
                        return;
                    }
                } catch (e) {
                    console.error('Error parsing response JSON:', e);
                }
            }
        }
        
        // Additional fallback: check if the entire data object has outputs we can use
        if (data.original_response && data.original_response.output && 
            data.original_response.output.outputs && 
            data.original_response.output.outputs.length > 0) {
            const imageUrl = data.original_response.output.outputs[0];
            console.log('Found image URL in original_response:', imageUrl);
            displayImageFromUrl(imageUrl);
            return;
        }
        
        // Final fallback: just look for the pattern in any string properties
        for (const key in data) {
            if (typeof data[key] === 'string' && data[key].includes('"outputs":["https://')) {
                try {
                    const match = data[key].match(/"outputs":\["(https:\/\/[^"]+)"/);
                    if (match && match[1]) {
                        console.log('Found image URL in string property:', match[1]);
                        displayImageFromUrl(match[1]);
                        return;
                    }
                } catch (e) {
                    console.error('Error extracting URL from string:', e);
                }
            }
        }
        
        console.warn('Could not find any image URL in the message:', data);
    } catch (error) {
        console.error('Error processing message:', error);
    }
}

// Get a random cell index for placing the new image
function getRandomCellIndex() {
    return Math.floor(Math.random() * config.gridSize);
}

// Display an image from a URL
function displayImageFromUrl(imageUrl) {
    try {
        console.log(`Preloading image from URL: ${imageUrl}`);
        
        // Get a random cell index for placement
        const cellIndex = getRandomCellIndex();
        const cell = document.getElementById(`cell-${cellIndex}`);
        
        if (!cell) return;
        
        // Create image element but don't add to DOM yet
        const img = new Image();
        img.crossOrigin = "anonymous";  // Try to avoid CORS issues
        
        // Create container for the image
        const container = document.createElement('div');
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.position = 'relative';
        
        // Set up onload handler
        img.onload = function() {
            console.log('Image loaded successfully, displaying now');
            
            // Now add the fully loaded image to container
            img.classList.add('image-loaded');
            container.appendChild(img);
            
            // Add caption with a link to open the image
            const caption = document.createElement('div');
            caption.classList.add('image-caption');
            caption.innerHTML = `<a href="${imageUrl}" target="_blank" title="Open in new tab">View Original Image</a>`;
            container.appendChild(caption);
            
            // Now replace the cell content with our prepared container
            cell.innerHTML = '';
            cell.appendChild(container);
            
            // Update state
            state.totalImagesReceived++;
            updateUI();
        };
        
        img.onerror = function() {
            console.error(`Error loading image from URL: ${imageUrl}`);
            
            // Only update the cell if there was an error
            cell.innerHTML = `
                <div class="error-image">
                    Image Load Error<br>
                    <a href="${imageUrl}" target="_blank" style="color: #ff7285; font-weight: bold; text-decoration: underline;">
                        Click to Open Image
                    </a>
                </div>
            `;
            
            state.totalImagesReceived++;
            updateUI();
        };
        
        // Start loading the image in the background
        img.src = imageUrl;
        
    } catch (error) {
        console.error('Error displaying image from URL:', error);
    }
}

// Display an image from base64 data
function displayImage(imageData) {
    try {
        // Remove data URL prefix if present
        if (imageData.startsWith('data:image')) {
            imageData = imageData.split(',', 2)[1];
        }
        
        // Get a random cell index for placement
        const cellIndex = getRandomCellIndex();
        const cell = document.getElementById(`cell-${cellIndex}`);
        
        if (!cell) return;
        
        // Create image element but don't add to DOM yet
        const img = new Image();
        
        // Set up onload handler
        img.onload = function() {
            // Now add the fully loaded image to cell
            cell.innerHTML = '';
            img.classList.add('image-loaded');
            cell.appendChild(img);
            
            state.totalImagesReceived++;
            updateUI();
        };
        
        img.onerror = function() {
            cell.innerHTML = '<div class="error-image">Failed to load image</div>';
            state.totalImagesReceived++;
            updateUI();
        };
        
        // Start loading the image in the background
        img.src = `data:image/jpeg;base64,${imageData}`;
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
    
    try {
        console.log(`Connecting to WebSocket: ${wsUrl} (attempt ${state.connectionAttempts})`);
        const socket = new WebSocket(wsUrl);
        
        socket.onopen = function() {
            console.log('WebSocket connection established');
            state.isConnected = true;
            state.connectionError = null;
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