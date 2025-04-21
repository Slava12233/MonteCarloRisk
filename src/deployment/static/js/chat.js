// Chat Interface JavaScript

// --- Constants and State ---
const DEFAULT_USER_ID = 'local_user'; // Use a consistent user ID for local dev
let currentUserId = DEFAULT_USER_ID;
let currentSessionId = null; // Will be set on load or when creating new
let webSocket = null;
let reconnectAttempts = 0;
let maxReconnectAttempts = 5;
let reconnectTimeout = null;
let isWaitingForResponse = false;

// --- UI Elements ---
let chatContainer;
let messageForm;
let messageInput;
let sessionList;
let newSessionBtn;
let statusIndicator;

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Get UI elements
    chatContainer = document.getElementById('chat-container');
    messageForm = document.getElementById('message-form');
    messageInput = document.getElementById('message-input');
    sessionList = document.getElementById('session-list');
    newSessionBtn = document.getElementById('new-session-btn');
    
    // Create status indicator
    createStatusIndicator();

    // Load existing sessions or create a new one
    loadSessions(currentUserId);

    // Handle New Session button click
    newSessionBtn.addEventListener('click', createNewSession);

    // Handle form submission
    messageForm.addEventListener('submit', handleFormSubmit);

    // Focus the input field
    messageInput.focus();
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);
});

// --- Core Functions ---

// Function to add a message to the chat display
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender);
    
    // Convert URLs to clickable links
    const linkedText = text.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    messageDiv.innerHTML = linkedText;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom
}

// Create a status indicator element
function createStatusIndicator() {
    statusIndicator = document.createElement('div');
    statusIndicator.id = 'status-indicator';
    statusIndicator.className = 'status-offline';
    statusIndicator.title = 'Connection status';
    document.body.appendChild(statusIndicator);
    
    // Add style if not already in CSS
    if (!document.querySelector('style[data-id="status-indicator-style"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-id', 'status-indicator-style');
        style.textContent = `
            #status-indicator {
                position: fixed;
                bottom: 10px;
                left: 10px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                transition: background-color 0.3s;
            }
            .status-online { background-color: #4CAF50; }
            .status-connecting { background-color: #FFC107; }
            .status-offline { background-color: #F44336; }
            
            .message.agent.typing:after {
                content: "";
                display: inline-block;
                width: 12px;
                height: 12px;
                margin-left: 5px;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 30"><circle cx="15" cy="15" r="5"><animate attributeName="opacity" dur="1s" values="0;1;0" repeatCount="indefinite" begin="0.1"/></circle><circle cx="40" cy="15" r="5"><animate attributeName="opacity" dur="1s" values="0;1;0" repeatCount="indefinite" begin="0.2"/></circle><circle cx="65" cy="15" r="5"><animate attributeName="opacity" dur="1s" values="0;1;0" repeatCount="indefinite" begin="0.3"/></circle></svg>');
                background-repeat: no-repeat;
                background-size: contain;
            }
        `;
        document.head.appendChild(style);
    }
}

// Update status indicator
function updateStatus(status) {
    if (!statusIndicator) return;
    
    statusIndicator.className = `status-${status}`;
    
    switch(status) {
        case 'online':
            statusIndicator.title = 'Connected';
            break;
        case 'connecting':
            statusIndicator.title = 'Connecting...';
            break;
        case 'offline':
            statusIndicator.title = 'Disconnected';
            break;
    }
}

// Handle form submission (using WebSocket)
async function handleFormSubmit(e) {
    e.preventDefault();
    const messageText = messageInput.value.trim();
    
    // Validate form submission
    if (!messageText) {
        messageInput.focus();
        return;
    }
    
    if (isWaitingForResponse) {
        // Optionally show a message that agent is still thinking
        const notification = document.createElement('div');
        notification.classList.add('message', 'system');
        notification.textContent = "Please wait for the agent to respond...";
        chatContainer.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
        return;
    }
    
    if (!currentSessionId) {
        console.error("No session ID available");
        addMessage("Error: No active session. Please refresh the page.", 'system');
        return;
    }
    
    // Check WebSocket status and reconnect if needed
    if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
        console.log("WebSocket not connected, attempting to reconnect...");
        webSocket = setupWebSocket(currentUserId, currentSessionId);
        
        // Wait briefly for connection
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check if connection successful
        if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
            addMessage("Error: Unable to connect to server. Please refresh the page.", 'system');
            return;
        }
    }

    // Add user message to chat display
    addMessage(messageText, 'user');
    messageInput.value = ''; // Clear input
    
    // Show typing indicator
    showTypingIndicator();
    
    // Set waiting state
    isWaitingForResponse = true;
    messageInput.disabled = true;
    
    // Send message via WebSocket
    try {
        webSocket.send(messageText);
    } catch (error) {
        console.error("Error sending message:", error);
        hideTypingIndicator();
        addMessage("Error: Failed to send message. Please try again.", 'system');
        isWaitingForResponse = false;
        messageInput.disabled = false;
    }
}

// Show typing indicator
function showTypingIndicator() {
    const typingIndicator = document.createElement('div');
    typingIndicator.classList.add('message', 'agent', 'typing');
    typingIndicator.id = 'typing-indicator';
    typingIndicator.textContent = "Agent is thinking...";
    chatContainer.appendChild(typingIndicator);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// --- Session Management Functions ---

// Load sessions from the backend
async function loadSessions(userId) {
    console.log("[loadSessions] Attempting to load sessions for user:", userId);
    try {
        const response = await fetch(`/api/sessions/${userId}`);
        console.log("[loadSessions] Response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("[loadSessions] Data received:", data);
        sessionList.innerHTML = ''; // Clear existing list ONLY on initial load
        console.log("[loadSessions] Session list cleared for initial load."); // DEBUG

        if (data.sessions && data.sessions.length > 0) {
            console.log("[loadSessions] Populating session list with:", data.sessions);
            data.sessions.forEach(sessionId => addSessionToList(sessionId, false)); // Add without making active yet
            // Switch to the first session in the list by default AFTER adding all
            switchSession(data.sessions[0]);
        } else {
            console.log("[loadSessions] No existing sessions found, creating a new one.");
            // No sessions found, create a new one
            createNewSession();
        }
    } catch (error) {
        console.error('[loadSessions] Error loading sessions:', error);
        addMessage('Error loading sessions. Creating a new one.', 'agent');
        // Fallback to creating a new session if loading fails
        console.log("[loadSessions] Fallback: Creating a new session due to load error.");
        createNewSession();
    }
}

// Add a session ID to the sidebar list
function addSessionToList(sessionId, makeActive = false) {
    console.log(`[addSessionToList] Adding session ID to UI: ${sessionId}, Make active: ${makeActive}`); // DEBUG
    // Check if item already exists
    if (sessionList.querySelector(`li[data-session-id="${sessionId}"]`)) {
        console.warn(`[addSessionToList] Session ID ${sessionId} already exists in the list. Skipping add.`);
        if (makeActive) setActiveSessionUI(sessionId); // Ensure it's marked active if requested
        return;
    }
    const listItem = document.createElement('li');
    listItem.textContent = sessionId.substring(0, 8) + '...'; // Show shortened ID
    listItem.dataset.sessionId = sessionId; // Store full ID
    listItem.title = sessionId; // Show full ID on hover
    listItem.addEventListener('click', () => switchSession(sessionId));

    sessionList.appendChild(listItem);

    if (makeActive) {
        setActiveSessionUI(sessionId);
    }
}

// Switch the active session
async function switchSession(newSessionId) { // Make function async
    if (currentSessionId === newSessionId && chatContainer.children.length > 1) { // Avoid reload if already active and populated
        console.log(`[switchSession] Already on session ${newSessionId}. Skipping switch.`);
        return;
    }

    console.log(`[switchSession] Switching to session: ${newSessionId}`);
    const previousSessionId = currentSessionId;
    currentSessionId = newSessionId;

    // Clear chat content visually first
    chatContainer.innerHTML = '';
    addMessage(`Loading history for session ${newSessionId.substring(0, 8)}...`, 'system'); // Loading message

    // Update UI highlighting
    setActiveSessionUI(newSessionId);

    // Fetch and display history
    try {
        console.log(`[switchSession] Fetching history for ${currentUserId}/${currentSessionId}`);
        const response = await fetch(`/api/sessions/${currentUserId}/${currentSessionId}/history`);
        if (!response.ok) {
             // Handle session not found or other errors specifically
             if (response.status === 404) {
                 console.log(`[switchSession] Session ${currentSessionId} not found on backend (likely new).`);
                 // Clear loading message and add standard switch message for new sessions
                 chatContainer.innerHTML = '';
                 addMessage(`Started new session ${currentSessionId.substring(0, 8)}...`, 'system');
             } else {
                throw new Error(`HTTP error fetching history! status: ${response.status}`);
             }
        } else {
            const data = await response.json();
            console.log(`[switchSession] Received history:`, data);
            chatContainer.innerHTML = ''; // Clear loading message
            addMessage(`Switched to session ${currentSessionId.substring(0, 8)}...`, 'system'); // Add switch message first
            if (data.history && data.history.length > 0) {
                data.history.forEach(msg => addMessage(msg.text, msg.sender));
            } else {
                 console.log(`[switchSession] No history found for session ${currentSessionId}.`);
            }
        }
    } catch (error) {
        console.error('[switchSession] Error fetching session history:', error);
        chatContainer.innerHTML = ''; // Clear loading message on error
        addMessage(`Error loading history for session ${currentSessionId.substring(0, 8)}.`, 'system');
        // Optionally revert session ID if fetch fails? Depends on desired UX.
        // currentSessionId = previousSessionId;
        // setActiveSessionUI(previousSessionId);
    }

    // Close existing WebSocket if open
    if (webSocket && webSocket.readyState === WebSocket.OPEN) {
        webSocket.close();
    }
    // Setup new WebSocket connection
    webSocket = setupWebSocket(currentUserId, currentSessionId);

    messageInput.focus(); // Refocus input
}

// Update the visual highlighting for the active session in the list
function setActiveSessionUI(sessionId) {
    const items = sessionList.querySelectorAll('li');
    items.forEach(item => {
        if (item.dataset.sessionId === sessionId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Create a new session locally (doesn't require backend call as InMemory service manages it)
function createNewSession() {
    // Simple unique ID generation for local use
    const newSessionId = `local_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    console.log(`[createNewSession] Called. Attempting to create new ID: ${newSessionId}`);

    // Check if session already exists in UI (shouldn't happen with this ID generation, but good practice)
    if (sessionList.querySelector(`li[data-session-id="${newSessionId}"]`)) {
        console.warn(`[createNewSession] Attempted to create a session ID that already exists in UI: ${newSessionId}. Switching instead.`);
        switchSession(newSessionId); // Just switch if it somehow exists
        return;
    }

    // 1. Add the new session ID to the UI list
    console.log("[createNewSession] Adding new session to UI list:", newSessionId);
    addSessionToList(newSessionId, false); // Add to list but don't mark active yet

    // 2. Switch the application state to use the new session
    // This clears the chat, updates currentSessionId, sets up the WebSocket, and marks active in UI
    console.log("[createNewSession] Switching application state to new session:", newSessionId);
    switchSession(newSessionId);

    // Log the current state of the session list in the UI after adding
    const currentListItems = Array.from(sessionList.querySelectorAll('li')).map(li => li.dataset.sessionId);
    console.log("[createNewSession] Current UI session list after add:", currentListItems);
}

// --- WebSocket Functions ---

// Setup WebSocket connection for a given session
function setupWebSocket(userId, sessionId) {
    // Close existing WebSocket if open
    if (webSocket && webSocket.readyState === WebSocket.OPEN) {
        console.log("Closing previous WebSocket connection.");
        webSocket.close();
    }

    updateStatus('connecting');
    const wsUrl = `ws://${window.location.host}/ws/${userId}/${sessionId}`;
    console.log(`Connecting WebSocket: ${wsUrl}`);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log(`WebSocket connection established for session ${sessionId}`);
        updateStatus('online');
        reconnectAttempts = 0; // Reset reconnect counter on successful connection
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log("WebSocket message received:", data);

            if (data.type === 'partial') {
                hideTypingIndicator(); // Remove typing indicator when first chunk arrives
                updatePartialResponse(data.text);
            } else if (data.type === 'final') {
                // Response complete - reset waiting state
                isWaitingForResponse = false;
                messageInput.disabled = false;
                messageInput.focus();
                
                // Remove partial message and typing indicator if they exist
                const partial = chatContainer.querySelector('.message.partial');
                if (partial) partial.remove();
                hideTypingIndicator();
                
                // Add the final message with animation
                const finalMessage = document.createElement('div');
                finalMessage.classList.add('message', 'agent');
                
                // Convert URLs to clickable links
                const linkedText = data.text.replace(
                    /(https?:\/\/[^\s]+)/g, 
                    '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
                );
                
                finalMessage.innerHTML = linkedText;
                chatContainer.appendChild(finalMessage);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                // Optional: Add subtle animation
                finalMessage.style.opacity = '0';
                finalMessage.style.transition = 'opacity 0.3s';
                setTimeout(() => finalMessage.style.opacity = '1', 10);
            } else {
                addMessage(JSON.stringify(data), 'system'); // Display other messages
            }
        } catch (error) {
            console.error("Error processing WebSocket message:", error);
            addMessage("Received malformed data from server.", 'system');
            isWaitingForResponse = false;
            messageInput.disabled = false;
        }
    };

    ws.onclose = (event) => {
        console.log(`WebSocket connection closed for session ${sessionId}. Code: ${event.code}, Reason: ${event.reason}`);
        updateStatus('offline');
        
        // Reset UI if response was pending
        if (isWaitingForResponse) {
            hideTypingIndicator();
            isWaitingForResponse = false;
            messageInput.disabled = false;
        }
        
        // Try to reconnect if this is the current session and not a deliberate close
        if (sessionId === currentSessionId && event.code !== 1000) {
            attemptReconnect(userId, sessionId);
        }
    };

    ws.onerror = (error) => {
        console.error(`WebSocket error for session ${sessionId}:`, error);
        updateStatus('offline');
        
        if (sessionId === currentSessionId) {
            // Don't show error if we're waiting for reconnect
            if (!reconnectTimeout) {
                addMessage("Connection error. Attempting to reconnect...", 'system');
            }
        }
    };

    return ws; // Return the WebSocket instance
}

// Attempt to reconnect WebSocket with exponential backoff
function attemptReconnect(userId, sessionId) {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.log("Maximum reconnection attempts reached.");
        addMessage("Unable to reconnect after several attempts. Please refresh the page.", 'system');
        return;
    }
    
    const delay = Math.min(30000, 1000 * Math.pow(2, reconnectAttempts)); // Exponential backoff
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})...`);
    
    clearTimeout(reconnectTimeout); // Clear any existing timeout
    
    reconnectTimeout = setTimeout(() => {
        reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${reconnectAttempts}`);
        webSocket = setupWebSocket(userId, sessionId);
    }, delay);
}

// Handle page visibility changes
function handleVisibilityChange() {
    if (document.visibilityState === 'visible') {
        // Page became visible - check connection status
        if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
            console.log("Page visible, connection lost - reconnecting...");
            if (currentSessionId) {
                webSocket = setupWebSocket(currentUserId, currentSessionId);
            }
        }
    }
}

// Update or create the partial response message element with improved display
function updatePartialResponse(text) {
    let partialMessage = chatContainer.querySelector('.message.partial');

    if (!partialMessage) {
        partialMessage = document.createElement('div');
        partialMessage.classList.add('message', 'agent', 'partial'); // Mark as agent and partial
        chatContainer.appendChild(partialMessage);
    }

    // Convert URLs to clickable links
    const linkedText = text.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    partialMessage.innerHTML = linkedText;
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom
}
