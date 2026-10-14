const express = require('express');
const fileUpload = require('express-fileupload');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(fileUpload());
app.use(express.urlencoded({ extended: true }));

// In-memory storage for uploaded texts (Render restarts par clear ho sakta hai, permanent ke liye file system use kar sakte hain)
const textStorage = {};

// Home Page: File upload form
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Only Broker - Text & File Hoster</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
                h2 { color: #d32f2f; margin-bottom: 20px; }
                input[type="file"] { margin: 20px 0; width: 100%; padding: 10px; border: 1px dashed #ccc; border-radius: 6px; }
                button { background: #d32f2f; color: white; border: none; padding: 12px 20px; width: 100%; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; }
                button:hover { background: #b71c1c; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Text File Uploader</h2>
                <form action="/upload" method="POST" enctype="multipart/form-data">
                    <input type="file" name="textFile" accept=".txt" required />
                    <button type="submit">Generate Link</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

// Handle File Upload and generate link
app.post('/upload', (req, res) => {
    if (!req.files || !req.files.textFile) {
        return res.status(400).send('Kripya koi file select karein.');
    }

    const file = req.files.textFile;
    const fileContent = file.data.toString('utf8');
    
    // Unique ID generate karna
    const fileId = Math.random().toString(36).substring(2, 9);
    textStorage[fileId] = fileContent;

    const host = req.get('host');
    const protocol = req.protocol;
    const generatedLink = `${protocol}://${host}/view/${fileId}`;

    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Link Generated</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 450px; text-align: center; }
                h3 { color: #333; }
                input[type="text"] { width: 100%; padding: 10px; margin: 15px 0; border: 1px solid #ccc; border-radius: 6px; text-align: center; font-size: 14px; background: #e8e8e8; }
                .btn { background: #2e7d32; color: white; border: none; padding: 12px 20px; width: 100%; border-radius: 6px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; }
                .btn:hover { background: #1b5e20; }
            </style>
        </head>
        <body>
            <div class="card">
                <h3>Aapka Link Taiyar Hai!</h3>
                <input type="text" value="${generatedLink}" id="linkBox" readonly />
                <a href="/view/${fileId}" class="btn" target="_blank">Link Par Jayein & Text Copy Karein</a>
            </div>
        </body>
        </html>
    `);
});

// View Page jahan poora text ek sath milega aur "Copy All" button hoga
app.get('/view/:id', (req, res) => {
    const fileId = req.params.id;
    const content = textStorage[fileId];

    if (!content) {
        return res.status(404).send('<h2>File ya toh expire ho gayi hai ya galat link hai.</h2>');
    }

    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>View & Copy Text</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; }
                .container { width: 100%; max-width: 600px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 20px; }
                textarea { width: 100%; height: 350px; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px; resize: vertical; box-sizing: border-box; }
                button { background: #1976d2; color: white; border: none; padding: 14px 20px; width: 100%; border-radius: 6px; font-size: 18px; cursor: pointer; margin-top: 15px; font-weight: bold; }
                button:hover { background: #115293; }
                #msg { color: green; font-weight: bold; margin-top: 10px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h3>Poora Text (A to Z)</h3>
                <textarea id="textContent">${content}</textarea>
                <button onclick="copyAllText()">Poora Text Copy Karein</button>
                <div id="msg"></div>
            </div>

            <script>
                function copyAllText() {
                    const textAreas = document.getElementById('textContent');
                    textAreas.select();
                    textAreas.setSelectionRange(0, 999999); // Mobile ke liye poora select karega
                    
                    try {
                        navigator.clipboard.writeText(textAreas.value).then(() => {
                            document.getElementById('msg').innerText = "Poora text successfully copy ho gaya!";
                        });
                    } catch (err) {
                        document.execCommand('copy');
                        document.getElementById('msg').innerText = "Poora text copy ho gaya!";
                    }
                }
            </script>
        </body>
        </html>
    `);
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
