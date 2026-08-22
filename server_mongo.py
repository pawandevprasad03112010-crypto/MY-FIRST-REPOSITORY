import datetime
import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo import MongoClient

# Flask app initialize karna (templates ke liye current folder set hai)
app = Flask(__name__, template_folder=".")
CORS(app)  # Cross-Origin requests allow karne ke liye

# Aapki MongoDB Atlas connection string (Password ki jagah apna asli password likhein)
MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?retryWrites=true&w=majority&appName=FIRSTMONGODB"

# MongoDB client connection establish karna
client = MongoClient(MONGO_URI)

# Aapke bataye gaye Database aur Collection ke naam
db = client["gg"]
collection = db["txtCities"]


# 1. Root route jo aapka frontend (index.html) page dikhayega
@app.route("/")
def index():
  return render_template("index.html")


# 2. Yeh route frontend se aane wale camera frames ko receive karke MongoDB mein save karega
@app.route("/upload", methods=["POST"])
def upload_frame():
  try:
    data = request.json
    image_data = data.get("image")  # Base64 image string

    if image_data:
      # MongoDB document structure
      frame_document = {
          "image_data": image_data,
          "timestamp": datetime.datetime.utcnow(),
      }

      # Data ko seedha 'gg' database ke 'txtCities' collection mein insert karna
      result = collection.insert_one(frame_document)

      print(
          f"[+] Success: Frame successfully MongoDB mein save ho gaya! ID:"
          f" {result.inserted_id}"
      )
      return jsonify(
          {
              "status": "success",
              "message": "Saved to MongoDB successfully",
              "id": str(result.inserted_id),
          }
      )

    return jsonify({"status": "error", "message": "No image data found"}), 400

  except Exception as e:
    print(f"[-] MongoDB Error: {e}")
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  # Render ya local server ke liye dynamic port configuration
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
  
