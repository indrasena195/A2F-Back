const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');

const app = express();
const PORT = 2000;

// Middleware
app.use(cors());
app.use(express.json());

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

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
