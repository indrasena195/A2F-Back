const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const http = require('http');
const WebSocket = require('ws');

// Initialize Express
const app = express();
const PORT = 2000;

// Middleware
app.use(cors());
app.use(express.json());

// POST route for HTTP server
app.post('/send-text', (req, res) => {
    const { text } = req.body;

    if (!text) {
        return res.status(400).send('Text is required');
    }

    const apiKey = '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';
    const functionId = 'b85c53f3-5d18-4edf-8b12-875a400eb798';
    const pythonCommand = `python ./a2f_client.py "${text}" ./config/config_mark.yml --apikey ${apiKey} --function-id ${functionId}`;

    exec(pythonCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return res.status(500).send('Error executing Python script');
        }

        if (stderr) {
            console.error(`Python script stderr: ${stderr}`);
        }

        console.log(`Python script output: ${stdout}`);
        // res.send(stdout);
    });

    res.status(200).send('Text received and processed');
});

// Create HTTP server
const server = http.createServer(app);

// Attach WebSocket server to the same HTTP server
const wss = new WebSocket.Server({ server });

// Store connected WebSocket clients
const clients = new Set();

// WebSocket connection handler
wss.on('connection', (ws) => {
    console.log('WebSocket connection established.');
    clients.add(ws);

    // Handle incoming messages
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log(`Received data: ${JSON.stringify(data)}`);
            // Broadcast data to all clients
            broadcastData(data);
        } catch (error) {
            console.error('Invalid JSON received:', error.message);
        }
    });

    // Handle WebSocket close
    ws.on('close', () => {
        console.log('WebSocket connection closed.');
        clients.delete(ws);
    });
});

// Broadcast data to all connected WebSocket clients
function broadcastData(data) {
    for (const client of clients) {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    }
}

// Start the server
server.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
    console.log(`WebSocket server is running at ws://localhost:${PORT}`);
});
