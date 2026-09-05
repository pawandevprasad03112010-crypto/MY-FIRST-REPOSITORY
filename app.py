import os
from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# Render Environment Variable ya Default Connection String
DEFAULT_URI = "mongodb+srv://pawandevprasad8_db_user:12300pawandevprasad03112010@cluster0.xmjo7lc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_URI = os.environ.get("MONGO_URI", DEFAULT_URI)

client = MongoClient(MONGO_URI)

# Database aur Collection
db = client["BUY_PROPERTY_KOLKATA"]
collection = db["KOLKATA_LISTING"]

# Integrated HTML Frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kolkata Listing Entry</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); width: 100%; max-width: 650px; }
        .card h2 { color: #1a202c; margin-bottom: 8px; font-size: 22px; }
        .db-badge { display: inline-block; background-color: #e6fffa; color: #234e52; border: 1px solid #b2f5ea; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-bottom: 15px; }
        textarea { width: 100%; height: 220px; padding: 14px; border: 2px solid #e2e8f0; border-radius: 8px; font-family: monospace; font-size: 14px; background-color: #f8fafc; }
        textarea:focus { outline: none; border-color: #3182ce; background-color: #ffffff; }
        .btn-container { margin-top: 15px; display: flex; justify-content: flex-end; }
        button { background-color: #3182ce; color: white; border: none; padding: 12px 24px; font-size: 15px; font-weight: 600; border-radius: 8px; cursor: pointer; }
        button:disabled { background-color: #cbd5e0; cursor: not-allowed; }
        #status { margin-top: 20px; padding: 12px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; display: none; }
        #status.loading { display: block; background-color: #feebc8; color: #744210; border: 1px solid #fbd38d; }
        #status.success { display: block; background-color: #c6f6d5; color: #22543d; border: 1px solid #9ae6b4; }
        #status.error { display: block; background-color: #fed7d7; color: #742a2a; border: 1px solid #feb2b2; }
    </style>
</head>
<body>

<div class="card">
    <h2>JSON Data Entry</h2>
    <div class="db-badge">Database: BUY_PROPERTY_KOLKATA | Collection: KOLKATA_LISTING</div>
    
    <textarea id="jsonInput" placeholder='{\n  "property_name": "3 BHK Flat",\n  "price": "75 Lakhs",\n  "location": "Salt Lake, Kolkata"\n}'></textarea>

    <div class="btn-container">
        <button id="submitBtn" onclick="sendData()">Submit to Database</button>
    </div>

    <div id="status"></div>
</div>

<script>
    async function sendData() {
        const inputField = document.getElementById("jsonInput");
        const statusDiv = document.getElementById("status");
        const submitBtn = document.getElementById("submitBtn");
        const rawText = inputField.value.trim();

        if (!rawText) {
            statusDiv.className = "error";
            statusDiv.innerText = "❌ Kripya valid JSON data daliye.";
            return;
        }

        let jsonData;
        try {
            jsonData = JSON.parse(rawText);
        } catch (e) {
            statusDiv.className = "error";
            statusDiv.innerText = "❌ Invalid JSON format! Syntax check karein.";
            return;
        }

        // Processing UI
        statusDiv.className = "loading";
        statusDiv.innerText = "⏳ Processing... Saving data to KOLKATA_LISTING collection...";
        submitBtn.disabled = true;

        try {
            const response = await fetch('/save-json', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(jsonData)
            });

            const result = await response.json();

            if (response.ok) {
                statusDiv.className = "success";
                statusDiv.innerText = "✅ " + result.message;
                inputField.value = ""; // Text box clear
            } else {
                statusDiv.className = "error";
                statusDiv.innerText = "❌ Error: " + result.message;
            }
        } catch (err) {
            statusDiv.className = "error";
            statusDiv.innerText = "❌ Server se connect nahi ho paya.";
        } finally {
            submitBtn.disabled = false;
        }
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save-json', methods=['POST'])
def save_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid ya khali JSON"}), 400
        
        collection.insert_one(data)
        return jsonify({
            "status": "success", 
            "message": "Data BUY_PROPERTY_KOLKATA db me successfully save ho gaya!"
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
