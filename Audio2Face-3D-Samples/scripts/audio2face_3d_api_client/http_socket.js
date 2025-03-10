const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const http = require('http');
const WebSocket = require('ws');

// Initialize Express
const app = express();
const PORT = 2000;
const API = process.env.NV_API

// Middleware
app.use(cors());
app.use(express.json());

// POST route for HTTP server
app.post('/send-text', (req, res) => {
    const { text } = req.body;

    if (!text) {
        return res.status(400).send('Text is required');
    }

    // const apiKey = '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';
    const apiKey = API;
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
        res.status(200).send(stdout || 'Text processed successfully'); // Respond after execution finishes
        // res.send(stdout);
    });


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
    ws.on('message', (message, isBinary) => {
        try {

            if (isBinary) {
                // Handle binary audio data
                // console.log('Received audio chunk (binary data)');
                broadcastData(message, true);  // Send as binary
            } else {
                // Handle JSON data (animation)
                const data = JSON.parse(message);
                
                if (data.type === 'animation_data') {
                    // console.log('Received animation data:', data);
                } else {
                    console.warn('Received unknown data type:', data);
                }
                
                broadcastData(data, false);  // Send as JSON
            }
        } catch (error) {
            console.error('Error processing message:', error.message);
        }
    });

    // Handle WebSocket close
    ws.on('close', () => {
        console.log('WebSocket connection closed.');
        clients.delete(ws);
    });
});

// Broadcast data to all connected WebSocket clients
function broadcastData(data, isBinary) {
    for (const client of clients) {
        if (client.readyState === WebSocket.OPEN) {
            if (isBinary) {
                client.send(data);  // Send binary audio directly
            } else {
                client.send(JSON.stringify(data));  // Send JSON data
            }
        }
    }
}

// Start the server
server.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
    console.log(`WebSocket server is running at ws://localhost:${PORT}`);
});
