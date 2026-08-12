import os
import re
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, static_folder='static')

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://pawandevprasad_db_user:12345@cluster.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI)
db = client['gg']
properties_col = db['txtCities']

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Property Search Engine</title>
</head>
<body style="margin:0; padding:0; background-color:#f7f7fc;">
  <script src="/static/app.js"></script>
</body>
</html>'''

# 🔍 UNIVERSAL MATCHING SEARCH ENGINE
@app.route('/api/search', methods=['GET'])
def search_properties():
    query_text = request.args.get('q', '').strip()
    
    if not query_text:
        # Agar kuch bhi type nahi kiya hai to saari properties dikhao
        results = list(properties_col.find({}))
    else:
        # Special characters ko escape karna taaki search crash na ho
        escaped_query = re.escape(query_text)
        
        # Regex pattern: Case-insensitive search (chhota/bada letter farak nahi padega)
        regex_pattern = {"$regex": escaped_query, "$options": "i"}
        
        # Dictionary ke kisi bhi key/field me Alphabet, Word ya Sentence match hona
        search_filter = {
            "$or": [
                {"title": regex_pattern},
                {"location": regex_pattern},
                {"furnishing": regex_pattern},
                {"highlights": regex_pattern},
                {"description": regex_pattern},
                {"size": regex_pattern},
                {"price": regex_pattern}
            ]
        }
        results = list(properties_col.find(search_filter))

    # ObjectId ko JSON string me badalna
    for doc in results:
        doc['_id'] = str(doc['_id'])
    
    return jsonify(results)

# Single Property Fetch API
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
    
