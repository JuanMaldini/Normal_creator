const express = require('express');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
const app = express();
const PORT = 3000;

app.use(express.static(path.join(__dirname, 'public')));

// Endpoint to download the BumpToNormalMap repository
app.post('/download-repo', (req, res) => {
    const repoUrl = 'https://github.com/MircoWerner/BumpToNormalMap.git';
    const targetDir = path.join(__dirname, 'BumpToNormalMap');
    const outputDir = path.join(__dirname, 'output');
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
        try {
            fs.mkdirSync(outputDir, { recursive: true });
            console.log('Output directory created:', outputDir);
        } catch (error) {
            console.error('Error creating output directory:', error);
        }
    }
    
    // Check if the repository directory already exists
    if (fs.existsSync(targetDir)) {
        return res.json({ 
            success: true, 
            message: 'Repository already exists! Output folder ready.',
            path: targetDir,
            outputPath: outputDir
        });
    }
    
    // Clone the repository
    exec(`git clone ${repoUrl} "${targetDir}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error cloning repository: ${error}`);
            return res.status(500).json({ 
                success: false, 
                error: error.message 
            });
        }
        
        res.json({ 
            success: true, 
            message: 'Repository downloaded and output folder created!',
            path: targetDir,
            outputPath: outputDir,
            stdout: stdout
        });
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
