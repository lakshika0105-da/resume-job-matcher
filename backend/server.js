const express = require('express');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const cors = require('cors');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const VENV_PYTHON_PATH = 'C:\\Users\\HP\\Desktop\\resume-analyzer\\venv\\Scripts\\python.exe';
const app = express();

app.use(cors());
app.use(express.json());
const upload = multer({ dest: 'uploads/' });

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'Server is running!' });
});

// Main analyze endpoint
app.post('/analyze', upload.single('resume'), async (req, res) => {
    try {
        console.log('Starting analysis for:', req.body.jobRole);
        
        if (!req.file || !req.body.jobRole) {
            return res.status(400).json({ error: 'Resume file and job role required' });
        }

        // Extract text from PDF
        const pdfPath = req.file.path;
        const fileBuffer = fs.readFileSync(pdfPath);
        const pdfData = await pdfParse(fileBuffer);
        const resumeText = pdfData.text;
        console.log('Text extracted:', resumeText.length, 'characters');

        // Call Python ML script
        const pythonScriptPath = path.join(__dirname, '../ml/analyzer.py');
        const python = spawn(VENV_PYTHON_PATH, [pythonScriptPath, resumeText, req.body.jobRole]);
        
        let result = '';
        let errorOutput = '';
        
        python.stdout.on('data', (data) => result += data.toString());
        python.stderr.on('data', (data) => errorOutput += data.toString());
        
        python.on('close', (code) => {
            fs.unlinkSync(pdfPath); // Cleanup file
            console.log('Python process completed with code:', code);
            
            if (code === 0) {
                try {
                    const analysisResult = JSON.parse(result);
                    console.log('Analysis successful!');
                    res.json(analysisResult);
                } catch (parseError) {
                    console.error('JSON parse error:', result);
                    res.status(500).json({ error: 'Failed to parse result', python_output: result });
                }
            } else {
                console.error('Python error:', errorOutput);
                res.status(500).json({ error: 'ML analysis failed', details: errorOutput });
            }
        });
        
    } catch (error) {
        console.error('Server error:', error);
        res.status(500).json({ error: 'Server error', message: error.message });
    }
});

// Start server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(✅ Server running on http://localhost:${PORT});
});
