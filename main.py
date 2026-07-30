import os
import re
from flask import Flask, render_template_string, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MONGO_URI from environment variable or fallback
MONGO_URI = os.environ.get(
    "MONGO_URI", 
    "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB"
)

client = MongoClient(MONGO_URI)
db = client["gg"]
collection = db["txtCities"]

# Helper function: Extract all PGs from nested JSON
def extract_all_pgs(data, sector_name=""):
    pg_list = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "_id":
                continue
            # If key looks like a sector
            current_sector = key if "sector" in key.lower() or "salt lake" in key.lower() else sector_name
            pg_list.extend(extract_all_pgs(value, current_sector))

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # If item is a PG object
                if "name" in item:
                    pg_item = dict(item)
                    if "sector" not in pg_item or not pg_item["sector"]:
                        pg_item["sector"] = sector_name
                    pg_list.append(pg_item)
                else:
                    pg_list.extend(extract_all_pgs(item, sector_name))

    return pg_list

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kolkata PG Search Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
        body { background: #f4f7f6; color: #333; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { width: 100%; max-width: 800px; }
        h1 { text-align: center; margin-bottom: 20px; color: #2c3e50; }
        
        .search-box { position: relative; margin-bottom: 30px; }
        .search-box input {
            width: 100%; padding: 15px 20px; font-size: 18px;
            border: 2px solid #ddd; border-radius: 30px; outline: none;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: all 0.3s ease;
        }
        .search-box input:focus { border-color: #3498db; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2); }

        .results-container { display: flex; flex-direction: column; gap: 20px; }
        
        .pg-card {
            background: #ffffff; border-radius: 12px; padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08); border-left: 5px solid #3498db;
        }
        .pg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .pg-title { font-size: 20px; font-weight: 600; color: #2c3e50; text-transform: capitalize; }
        .pg-sector { background: #e1f5fe; color: #0288d1; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .pg-info { font-size: 14px; color: #555; margin-bottom: 8px; }

        .pg-image-container { margin-top: 15px; width: 100%; border-top: 1px solid #eee; padding-top: 15px; }
        .pg-image { width: 100%; max-height: 350px; object-fit: cover; border-radius: 8px; }

        .no-results { text-align: center; font-size: 16px; color: #888; margin-top: 20px; }
    </style>
</head>
<body>

<div class="container">
    <h1>Kolkata PG Search Engine</h1>
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search PG Name, Sector, or Phone..." onkeyup="performSearch()">
    </div>
    <div class="results-container" id="results"></div>
</div>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        performSearch();
    });

    function performSearch() {
        const query = document.getElementById('searchInput').value;
        const resultsContainer = document.getElementById('results');

        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = '';

                if (!data || data.length === 0) {
                    resultsContainer.innerHTML = '<div class="no-results">Koi PG nahi mila!</div>';
                    return;
                }

                data.forEach(pg => {
                    let card = document.createElement('div');
                    card.className = 'pg-card';

                    let imageHTML = '';
                    if (pg.image_url && pg.image_url.trim() !== "") {
                        imageHTML = `
                            <div class="pg-image-container">
                                <img src="${pg.image_url}" alt="${pg.name}" class="pg-image" loading="lazy">
                            </div>
                        `;
                    }

                    card.innerHTML = `
                        <div class="pg-header">
                            <div class="pg-title">${pg.name || 'N/A'}</div>
                            <span class="pg-sector">${pg.sector || 'Sector N/A'}</span>
                        </div>
                        <div class="pg-info"><strong>Phone:</strong> ${pg.phone_no || 'N/A'}</div>
                        <div class="pg-info">
                            <strong>Rent Details:</strong> 
                            Single: ${pg.rent?.single || '-'} | 
                            Double: ${pg.rent?.double || '-'} | 
                            Triple: ${pg.rent?.triple || '-'} | 
                            Four: ${pg.rent?.four || '-'}
                        </div>
                        ${imageHTML}
                    `;
                    resultsContainer.appendChild(card);
                });
            })
            .catch(error => console.error('Fetch Error:', error));
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search', methods=['GET'])
def search_pgs():
    query = request.args.get('q', '').strip().lower()

    try:
        # Fetch all documents from MongoDB
        docs = list(collection.find({}, {"_id": 0}))
        
        # Flatten all PGs regardless of JSON structure
        all_pgs = []
        for doc in docs:
            all_pgs.extend(extract_all_pgs(doc))

        # Filter PGs based on search query
        if not query:
            return jsonify(all_pgs)

        filtered = []
        for pg in all_pgs:
            name = str(pg.get('name', '')).lower()
            phone = str(pg.get('phone_no', '')).lower()
            sector = str(pg.get('sector', '')).lower()

            if query in name or query in phone or query in sector:
                filtered.append(pg)

        return jsonify(filtered)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
