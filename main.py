import os
import re
from flask import Flask, render_template_string, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Connection String (Render Par Environment Variable Set Karein)
MONGO_URI = os.environ.get("mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB")

try:
    client = MongoClient(MONGO_URI)
    db = client["gg"]
    collection = db["txtCities"]
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

# HTML, CSS aur JS Code python variable ke andar
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kolkata PG Search Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
        }

        body {
            background: #f4f7f6;
            color: #333;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 800px;
        }

        h1 {
            text-align: center;
            margin-bottom: 20px;
            color: #2c3e50;
        }

        /* Search Box Design */
        .search-box {
            position: relative;
            margin-bottom: 30px;
        }

        .search-box input {
            width: 100%;
            padding: 15px 20px;
            font-size: 18px;
            border: 2px solid #ddd;
            border-radius: 30px;
            outline: none;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }

        .search-box input:focus {
            border-color: #3498db;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);
        }

        /* Results Layout */
        .results-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* Information Box (PG Card) */
        .pg-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 5px solid #3498db;
            transition: transform 0.2s ease;
        }

        .pg-card:hover {
            transform: translateY(-3px);
        }

        .pg-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .pg-title {
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            text-transform: capitalize;
        }

        .pg-sector {
            background: #e1f5fe;
            color: #0288d1;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .pg-info {
            font-size: 14px;
            color: #555;
            margin-bottom: 8px;
        }

        .pg-info strong {
            color: #333;
        }

        /* Image Box - Displayed directly below information */
        .pg-image-container {
            margin-top: 15px;
            width: 100%;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }

        .pg-image {
            width: 100%;
            max-height: 350px;
            object-fit: cover;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .no-results {
            text-align: center;
            font-size: 16px;
            color: #888;
            margin-top: 20px;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Kolkata PG Search Engine</h1>
    
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="Search PG Name, Sector, or Phone..." onkeyup="performSearch()">
    </div>

    <div class="results-container" id="results">
        <!-- Search Results Yahan Load Honge -->
    </div>
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

                if (data.length === 0) {
                    resultsContainer.innerHTML = '<div class="no-results">Koi PG nahi mila!</div>';
                    return;
                }

                data.forEach(pg => {
                    let card = document.createElement('div');
                    card.className = 'pg-card';

                    let imageHTML = '';
                    // Cloudinary Image Box (Information Box ke theek niche)
                    if (pg.image_url && pg.image_url.trim() !== "") {
                        imageHTML = `
                            <div class="pg-image-container">
                                <img src="${pg.image_url}" alt="${pg.name}" class="pg-image" loading="lazy">
                            </div>
                        `;
                    }

                    card.innerHTML = `
                        <div class="pg-header">
                            <div class="pg-title">${pg.name}</div>
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
            .catch(error => console.error('Error fetching data:', error));
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    # render_template_string se Python variable se seedhe HTML render hoga
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search', methods=['GET'])
def search_pgs():
    query = request.args.get('q', '').strip()
    results = []

    if not query:
        search_filter = {}
    else:
        regex = re.compile(re.escape(query), re.IGNORECASE)
        search_filter = {
            "$or": [
                {"name": regex},
                {"sector": regex},
                {"phone_no": regex},
                {"city": regex}
            ]
        }

    try:
        records = collection.find(search_filter, {"_id": 0})
        for doc in records:
            results.append(doc)
    except Exception as e:
        print(f"Query Execution Error: {e}")

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
