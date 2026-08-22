const express = require('express');
const multer = require('multer');
const path = require('path');
const cloudinary = require('cloudinary').v2;
const streamifier = require('streamifier');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

// === यहाँ आपकी Cloudinary डिटेल्स सीधे सेट कर दी गई हैं ===
cloudinary.config({
    cloud_name: 'nuhifsdu',
    api_key: '473579919555811',
    api_secret: 'BJEn_ZyhVXEtdn_wed4jXAzXFkU'
});

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ऑडियो अपलोड करने और Cloudinary पर भेजने का एंडपॉइंट
app.post('/upload-audio', upload.single('audio'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'कोई ऑडियो फ़ाइल नहीं मिली।' });
        }

        let streamUpload = (req) => {
            return new Promise((resolve, reject) => {
                let stream = cloudinary.uploader.upload_stream(
                    { resource_type: "video" },
                    (error, result) => {
                        if (result) {
                            resolve(result);
                        } else {
                            reject(error);
                        }
                    }
                );
                streamifier.createReadStream(req.file.buffer).pipe(stream);
            });
        };

        let result = await streamUpload(req);

        console.log('ऑडियो क्लाउड पर सफलतापूर्वक सेव हो गया:', result.secure_url);
        
        res.status(200).json({ 
            success: true, 
            message: 'ऑडियो सफलतापूर्वक Cloudinary पर सहेज लिया गया!',
            url: result.secure_url 
        });

    } catch (error) {
        console.error('अपलोड त्रुटि:', error);
        res.status(500).json({ error: 'सर्वर त्रुटि', details: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`सर्वर ${PORT} पोर्ट पर चल रहा है`);
});
