const express = require('express');
const { exec } = require('child_process');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Ensure the JSON directory exists
const jsonDir = '/volume2/ITStore/json/';
fs.mkdirSync(jsonDir, { recursive: true });

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: jsonDir,
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix);
    }
});

const upload = multer({ storage: storage });

const app = express();
const port = 3000;

// Middleware to parse form data
app.use(express.urlencoded({ extended: true }));

// Serve your index.html file
app.get('/', (req, res) => {
    res.sendFile('/volume2/ITStore/index.html');
});

// Endpoint to execute Python script for single config generation
app.post('/runscript', (req, res) => {
    const { extension, fullname, dhcphostname, agentname, macaddress } = req.body;
    const command = `/usr/local/bin/python3 /volume2/ITStore/Yealink.py ${extension} "${fullname}" "${dhcphostname}" "${agentname}" ${macaddress}`;
    console.log("Executing command for single config:", command);

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Execution error: ${error}`);
            return res.status(500).send(`Error executing script: ${stderr}`);
        }
        console.log("Single config script output:", stdout);
        res.send(`Script output: ${stdout}`);
    });
});

// Endpoint for JSON file upload and multiple config generation
app.post('/uploadjson', upload.single('jsonfile'), (req, res) => {
    // Check if the file is received
    if (!req.file) {
        console.error("No file received for JSON upload");
        return res.status(400).send('No JSON file uploaded.');
    }

    console.log("Received file for JSON upload:", req.file);

    // Construct the command to execute the Python script
    const command = `/usr/local/bin/python3 /volume2/ITStore/Yealink.py "${req.file.path}"`;
    console.log("Executing command for JSON processing:", command);

    exec(command, {maxBuffer: 1024 * 1024 * 5}, (error, stdout, stderr) => {
        console.log("stdout from JSON script:", stdout);
        console.log("stderr from JSON script:", stderr);

        // Remove the uploaded file after processing
        fs.unlink(req.file.path, (err) => {
            if (err) {
                console.error(`Error deleting file '${req.file.path}':`, err);
            }
        });

        if (error) {
            console.error(`Execution error from JSON script: ${error}`);
            return res.status(500).send(`Error processing JSON: ${error.message}`);
        }

        res.send(`JSON processed. Script output: ${stdout}`);
    });
});

// Error handling for Multer
function multerErrorHandler(err, req, res, next) {
    if (err instanceof multer.MulterError) {
        console.error('Multer error:', err);
        return res.status(500).send('Multer error: ' + err.message);
    }
    next(err); // Not a Multer error, forward to the next error handler
}

app.use(multerErrorHandler);

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});
