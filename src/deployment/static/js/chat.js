// Chat Interface JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    
    // Add a welcome message
    addMessage('Welcome! How can I help you today?', 'agent');
    
    // Function to add a message to the chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender);
        messageDiv.textContent = text;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Handle form submission
    messageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';
        
        try {
            // Send message to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: message,
                    user_id: 'user',
                    session_id: 'session'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Add agent response to chat
            addMessage(data.response, 'agent');
        } catch (error) {
            console.error('Error:', error);
            addMessage('Error: Could not get response from agent', 'agent');
        }
    });

    // Focus the input field when the page loads
    messageInput.focus();
});

// WebSocket support for streaming responses
function setupWebSocket(userId, sessionId) {
    const wsUrl = `ws://${window.location.host}/ws/${userId}/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connection established');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'partial') {
            // Handle partial response (streaming)
            updatePartialResponse(data.text);
        } else if (data.type === 'final') {
            // Handle final response
            addMessage(data.text, 'agent');
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket connection closed');
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    return ws;
}

// Function to update a partial response (for streaming)
function updatePartialResponse(text) {
    let partialMessage = document.querySelector('.message.partial');
    
    if (!partialMessage) {
        partialMessage = document.createElement('div');
        partialMessage.classList.add('message', 'agent', 'partial');
        chatContainer.appendChild(partialMessage);
    }
    
    partialMessage.textContent = text;
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
