import os
import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader

# Cloudinary Configuration
cloudinary.config(
    cloud_name = "nuhlfsdu",
    api_key = "473579919558511",
    api_secret = "BJEn_ZyhVXEtdn_wed4jXAzXFkU",
    secure = True
)

# Flask app initialization
app = Flask(__name__, template_folder=".")
CORS(app)

# MongoDB Connection
MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p4qsrf.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# Database "gg" aur collection "txtCities"
db = client["IMAGE"]
collection = db["IMAGE"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_frame():
    try:
        data = request.json
        image_data = data.get("image")  # Base64 image string

        if image_data:
            # 1. Image ko Cloudinary par upload karein
            upload_result = cloudinary.uploader.upload(
                image_data,
                folder = "webcam_captures"
            )
            
            image_url = upload_result.get("secure_url")
            public_id = upload_result.get("public_id")

            # 2. Cloudinary se mila URL MongoDB mein document banakar save karein
            frame_document = {
                "image_url": image_url,
                "public_id": public_id,
                "timestamp": datetime.datetime.utcnow()
            }
            
            result = collection.insert_one(frame_document)

            print(f"[+] Success: Cloudinary URL MongoDB mein save ho gaya! ID: {result.inserted_id}")

            return jsonify({
                "status": "success",
                "message": "Image saved to Cloudinary & URL stored in MongoDB",
                "mongo_id": str(result.inserted_id),
                "image_url": image_url
            })

        return jsonify({"status": "error", "message": "No image data found"}), 400

    except Exception as e:
        print(f"[-] Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
          
