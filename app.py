import os
from flask import Flask, jsonify, request, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, static_folder='static')

# MongoDB Connection (Render Environment Variable se URI lega)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB")
client = MongoClient(MONGO_URI)
db = client['gg']
properties_col = db['txtCities']

# Root Route: Bina kisi HTML template ke sirf Script tag load karega
@app.route('/')
def index():
    return '<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Property App</title></head><body style="margin:0; padding:0; background:#f7f7fc;"><script src="/static/app.js"></script></body></html>'

# Search API
@app.route('/api/search', methods=['GET'])
def search_properties():
    query = request.args.get('q', '').strip()
    if not query:
        results = list(properties_col.find({}))
    else:
        regex_query = {"$regex": query, "$options": "i"}
        results = list(properties_col.find({
            "$or": [
                {"location": regex_query},
                {"title": regex_query},
                {"furnishing": regex_query}
            ]
        }))

    for doc in results:
        doc['_id'] = str(doc['_id'])
    
    return jsonify(results)

# Get Single Property Detail API
@app.route('/api/property/<id>', methods=['GET'])
def get_property(id):
    try:
        doc = properties_col.find_one({"_id": ObjectId(id)})
        if doc:
            doc['_id'] = str(doc['_id'])
            return jsonify(doc)
        return jsonify({"error": "Property not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    
