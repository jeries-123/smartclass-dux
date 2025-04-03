const WebSocket = require('ws');

const PORT = 8766;
const wss = new WebSocket.Server({ port: PORT });

wss.on('connection', (ws) => {
    console.log('New client connected');

    ws.on('message', (message) => {
        console.log(`Received message: ${message}`);

        // Parse the incoming message as JSON
        let data;
        try {  
            data = JSON.parse(message);
        } catch (err) {
            console.error('Invalid JSON:', err);
            return;
        }

        // Broadcast the received message to all other clients
        wss.clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify(data));
            }
        });
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

console.log(`WebSocket signaling server is running on ws://localhost:${PORT}`);
