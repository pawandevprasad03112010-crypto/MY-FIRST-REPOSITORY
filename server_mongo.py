import datetime
import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo import MongoClient

# 'templates' folder ke andar index.html rakhna hoga
app = Flask(__name__, template_folder=".")
CORS(app)

MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?retryWrites=true&w=majority&appName=FIRSTMONGODB"

client = MongoClient(MONGO_URI)
db = client["txtCities_database"]
collection = db["txtCities"]


# 1. Yeh route aapke main URL par index.html file dikhayega
@app.route("/")
def index():
  return render_template("index.html")


# 2. Yeh route data upload karne ke liye hai
@app.route("/upload", methods=["POST"])
def upload_frame():
  try:
    data = request.json
    image_data = data.get("image")

    if image_data:
      frame_document = {
          "image_data": image_data,
          "timestamp": datetime.datetime.utcnow(),
      }
      result = collection.insert_one(frame_document)
      return jsonify(
          {"status": "success", "id": str(result.inserted_id)}
      )

    return jsonify({"status": "error", "message": "No image data"}), 400
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
  
