const express = require('express');
const multer = require('multer');
const path = require('path');
const cloudinary = require('cloudinary').v2;
const streamifier = require('streamifier');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

// === अपने Cloudinary क्रेडेंशियल्स यहाँ भरें ===
cloudinary.config({
    cloud_name: 'YOUR_CLOUD_NAME',
    api_key: 'YOUR_API_KEY',
    api_secret: 'YOUR_API_SECRET'
});

app.use(express.express ? express.static(path.join(__dirname, 'public')) : express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/upload-audio', upload.single('audio'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'कोई ऑडियो नहीं मिला' });
        }

        let streamUpload = (req) => {
            return new Promise((resolve, reject) => {
                let stream = cloudinary.uploader.upload_stream(
                    { resource_type: "video" },
                    (error, result) => {
                        if (result) resolve(result);
                        else reject(error);
                    }
                );
                streamifier.createReadStream(req.file.buffer).pipe(stream);
            });
        };

        let result = await streamUpload(req);
        console.log('ऑडियो क्लाउड पर सेव हुआ:', result.secure_url);
        res.status(200).json({ success: true, url: result.secure_url });
    } catch (error) {
        console.error('त्रुटि:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`सर्वर चालू है पोर्ट ${PORT} पर`);
});

