from flask import Flask, render_template, request, jsonify, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# ---------- MongoDB connection ----------
# Render ke "Environment" tab mein ye variables set karein:
#   MONGO_URI        -> aapki MongoDB connection string (mongodb+srv://...)
#   DB_NAME           -> database ka naam (default: dictionary_db)
#   COLLECTION_NAME   -> collection ka naam (default: words)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://pawandevprasad03112010_db_user:<db_password>@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB")
DB_NAME = os.environ.get("DB_NAME", "gg")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "txtCities")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Expected document format in MongoDB collection:
# {
#   "word": "Apple",
#   "meaning": "Apple ek fal hai...",
#   "photo": "https://example.com/apple.jpg"
# }


def serialize(doc):
    """MongoDB ka ObjectId ko JSON/HTML ke liye string bana deta hai."""
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc


# ---------- Home page (search box) ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- Search API (AJAX ke liye) ----------
@app.route("/api/search")
def search_api():
    query = request.args.get("q", "").strip()

    if query == "":
        results = []
    else:
        # Case-insensitive partial match "word" field par
        cursor = collection.find(
            {"word": {"$regex": query, "$options": "i"}}
        ).sort("word", 1)
        results = [serialize(doc) for doc in cursor]

    return jsonify(results)


# ---------- Detail page (click karne par khulta hai) ----------
@app.route("/word/<word_id>")
def detail(word_id):
    try:
        doc = collection.find_one({"_id": ObjectId(word_id)})
    except Exception:
        doc = None

    if doc is None:
        abort(404)

    item = serialize(doc)
    return render_template("detail.html", item=item)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
