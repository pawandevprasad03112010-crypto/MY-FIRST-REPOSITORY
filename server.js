const express = require('express');
const fileUpload = require('express-fileupload');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(fileUpload());
app.use(express.urlencoded({ extended: true }));

const textStorage = {};

// Home Page: Mobile se file select karne ke liye clean design
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Phone File Hoster</title>
            <style>
                body { font-family: Arial, sans-serif; background: #121212; color: #ffffff; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .card { background: #1e1e1e; padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; }
                h2 { color: #4CAF50; margin-bottom: 20px; }
                input[type="file"] { margin: 20px 0; width: 100%; padding: 12px; background: #2c2c2c; border: 1px dashed #555; border-radius: 8px; color: #fff; }
                button { background: #4CAF50; color: white; border: none; padding: 14px 20px; width: 100%; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
                button:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>File Select Karein</h2>
                <form action="/upload" method="POST" enctype="multipart/form-data">
                    <input type="file" name="textFile" accept=".txt,.json,.csv,.log" required />
                    <button type="submit">Link Banayein</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

// File upload handle karega
app.post('/upload', (req, res) => {
    if (!req.files || !req.files.textFile) {
        return res.status(400).send('Kripya koi file select karein.');
    }

    const file = req.files.textFile;
    const fileContent = file.data.toString('utf8');
    
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
            <title>Link Taiyar Hai</title>
            <style>
                body { font-family: Arial, sans-serif; background: #121212; color: #ffffff; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .card { background: #1e1e1e; padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 420px; text-align: center; }
                input[type="text"] { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #444; border-radius: 8px; text-align: center; font-size: 14px; background: #2c2c2c; color: #fff; box-sizing: border-box; }
                .btn { background: #2196F3; color: white; border: none; padding: 14px 20px; width: 100%; border-radius: 8px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; box-sizing: border-box; margin-top: 10px; }
                .btn:hover { background: #1976D2; }
            </style>
        </head>
        <body>
            <div class="card">
                <h3>Aapka Link Ban Gaya!</h3>
                <input type="text" value="${generatedLink}" readonly />
                <a href="/view/${fileId}" class="btn" target="_blank">Link Kholein & Copy Karein</a>
            </div>
        </body>
        </html>
    `);
});

// View Page jahan poora text ek sath copy hoga
app.get('/view/:id', (req, res) => {
    const fileId = req.params.id;
    const content = textStorage[fileId];

    if (!content) {
        return res.status(404).send('<h3 style="color:red; text-align:center; margin-top:50px;">File expire ho chuki hai ya link galat hai.</h3>');
    }

    res.send(`
        <!DOCTYPE html>
        <html lang="hi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>View & Copy</title>
            <style>
                body { font-family: Arial, sans-serif; background: #121212; color: #ffffff; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; }
                .container { width: 100%; max-width: 600px; background: #1e1e1e; padding: 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin-top: 20px; box-sizing: border-box; }
                textarea { width: 100%; height: 350px; padding: 12px; border: 1px solid #444; border-radius: 8px; font-size: 16px; background: #2c2c2c; color: #fff; resize: vertical; box-sizing: border-box; }
                button { background: #FF9800; color: white; border: none; padding: 14px 20px; width: 100%; border-radius: 8px; font-size: 18px; cursor: pointer; margin-top: 15px; font-weight: bold; }
                button:hover { background: #F57C00; }
                #msg { color: #4CAF50; font-weight: bold; margin-top: 12px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h3 style="margin-top:0;">Poora Text (A to Z)</h3>
                <textarea id="textContent">${content}</textarea>
                <button onclick="copyAllText()">Ek Click Me Poora Copy Karein</button>
                <div id="msg"></div>
            </div>

            <script>
                function copyAllText() {
                    const textAreas = document.getElementById('textContent');
                    textAreas.select();
                    textAreas.setSelectionRange(0, 999999); // Mobile compatibility ke liye
                    
                    try {
                        navigator.clipboard.writeText(textAreas.value).then(() => {
                            document.getElementById('msgถาน" || document.getElementById('msg').innerText = "Poora text successfully copy ho gaya!";
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
