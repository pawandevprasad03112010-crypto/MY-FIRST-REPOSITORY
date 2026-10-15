import os
import re
import time
import requests
import boto3
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = "AKIA32VVAONMQV5QKNED"
AWS_SECRET_ACCESS_KEY = "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"
REGION = "ap-south-1"
BUCKET_NAME = "property-images-estatex-1"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)

# Complete Frontend & Backend Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ONLY BROKER - S3 Image Migrator</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 950px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; text-align: center; }
        textarea { width: 100%; height: 120px; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; box-sizing: border-box; resize: vertical; }
        .btn-primary { background: #3498db; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; }
        .btn-primary:hover { background: #2980b9; }
        .btn-upload { background: #27ae60; color: white; border: none; padding: 14px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 20px; font-weight: bold; display: none; }
        .btn-upload:hover { background: #219653; }
        
        .grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .image-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 8px; text-align: center; position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .image-card img { width: 100%; height: 140px; object-fit: cover; border-radius: 6px; }
        .delete-btn { position: absolute; top: 12px; right: 12px; background: #e74c3c; color: white; border: none; border-radius: 50%; width: 26px; height: 26px; cursor: pointer; font-weight: bold; font-size: 14px; line-height: 26px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .delete-btn:hover { background: #c0392b; }
        
        .output-section { margin-top: 25px; display: none; }
        .output-box { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; font-size: 13px; }
        .btn-copy { background: #e67e22; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; margin-top: 10px; font-weight: bold; }
        .btn-copy:hover { background: #d35400; }
        .loader { text-align: center; display: none; margin-top: 15px; font-weight: bold; color: #e67e22; }
    </style>
</head>
<body>
    <div class="container">
        <h2>ONLY BROKER - Image Manager & S3 Migrator</h2>
        <p>Yahan apne image URLs paste karein (chahe Array brackets `[]` mein ho ya plain text):</p>
        <textarea id="urlInput" placeholder="Yahan URLs daalein..."></textarea>
        <button class="btn-primary" onclick="loadImagesPreview()">Images Load Karein</button>

        <!-- Preview Grid -->
        <div class="grid-container" id="imageGrid"></div>
        
        <!-- Upload Button -->
        <button class="btn-upload" id="uploadBtn" onclick="uploadToS3()">S3 Par Upload Karein</button>
        <div class="loader" id="loader">🔄 S3 par upload ho raha hai, kripya intezaar karein...</div>

        <!-- JSON Output Section -->
        <div class="output-section" id="outputSection">
            <h3>S3 Uploaded URLs (JSON Format):</h3>
            <div class="output-box" id="jsonOutput"></div>
            <button class="btn-copy" onclick="copyJSON()">Copy All JSON</button>
        </div>
    </div>

    <script>
        let currentUrls = [];

        function loadImagesPreview() {
            let rawInput = document.getElementById("urlInput").value.trim();
            if(!rawInput) {
                alert("Kripya kuch URLs daalein!");
                return;
            }

            const matches = rawInput.match(/https?:\/\/[^\s,\'\"\[\]]+/g);
            if(!matches || matches.length === 0) {
                alert("Koi bhi valid URL nahi mila!");
                return;
            }

            currentUrls = [...new Set(matches)];
            renderGrid();
        }

        function renderGrid() {
            let grid = document.getElementById("imageGrid");
            grid.innerHTML = "";

            currentUrls.forEach((url, index) => {
                let card = document.createElement("div");
                card.className = "image-card";
                card.innerHTML = `
                    <button class="delete-btn" onclick="removeImage(${index})">&times;</button>
                    <img src="${url}" onerror="this.src='https://via.placeholder.com/150?text=Invalid+Image'">
                    <p style="font-size:10px; color:#666; margin:5px 0 0 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${url}</p>
                `;
                grid.appendChild(card);
            });

            if(currentUrls.length > 0) {
                document.getElementById("uploadBtn").style.display = "block";
            } else {
                document.getElementById("uploadBtn").style.display = "none";
            }
            document.getElementById("outputSection").style.display = "none";
        }

        function removeImage(index) {
            currentUrls.splice(index, 1);
            renderGrid();
        }

        async function uploadToS3() {
            if(currentUrls.length === 0) return;

            document.getElementById("loader").style.display = "block";
            document.getElementById("uploadBtn").style.display = "none";

            try {
                let response = await fetch('/upload_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ urls: currentUrls })
                });

                let result = await response.json();
                document.getElementById("loader").style.display = "none";

                if(result.success) {
                    let jsonStr = JSON.stringify(result.s3_urls, null, 4);
                    document.getElementById("jsonOutput").innerText = jsonStr;
                    document.getElementById("outputSection").style.display = "block";
                } else {
                    alert("Error: " + result.error);
                    document.getElementById("uploadBtn").style.display = "block";
                }
            } catch (err) {
                document.getElementById("loader").style.display = "none";
                alert("Upload failed!");
                document.getElementById("uploadBtn").style.display = "block";
            }
        }

        function copyJSON() {
            let text = document.getElementById("jsonOutput").innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert("Successfully Copied All URLs in JSON format!");
            });
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/upload_batch", methods=["POST"])
def upload_batch():
    try:
        data = request.json
        urls = data.get("urls", [])
        s3_uploaded_urls = []
        
        for idx, url in enumerate(urls):
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    ext = url.split("?")[0].split(".")[-1]
                    if ext not in ["jpg", "jpeg", "png", "webp"]:
                        ext = "png"
                        
                    filename = f"onlybroker_{idx}_{int(time.time())}.{ext}"
                    
                    s3_client.put_object(
                        Bucket=BUCKET_NAME,
                        Key=filename,
                        Body=res.content,
                        ContentType=f"image/{ext}"
                    )
                    
                    s3_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{filename}"
                    s3_uploaded_urls.append(s3_url)
            except Exception as e:
                print(f"Error uploading {url}: {e}")
                
        return jsonify({"success": True, "s3_urls": s3_uploaded_urls})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
            
