import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Cross-Origin requests allow karne ke liye

# Aapki MongoDB Atlas connection string
# NOTE: '<db_password>' ki jagah apna asli password zaroor likhein
MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?retryWrites=true&w=majority&appName=FIRSTMONGODB"

# MongoDB client connection establish karna
client = MongoClient(MONGO_URI)

# Database aur Collection ka naam (Aapne 'txtCities' mention kiya hai)
db = client["txtCities_database"]  # Aap chahein toh database ka naam badal sakte hain
collection = db["txtCities"]  # Collection ka naam


@app.route("/upload", methods=["POST"])
def upload_frame():
  try:
    data = request.json
    image_data = data.get("image")  # Base64 image string

    if image_data:
      # MongoDB mein save karne ke liye document structure
      frame_document = {
          "image_data": image_data,
          "timestamp": datetime.datetime.utcnow(),
      }

      # Data ko MongoDB collection ('txtCities') mein insert karna
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
  # Render ya local server ke liye port configuration
  import os

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
    
