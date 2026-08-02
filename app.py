from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from jinja2 import Template
import motor.motor_asyncio
from bson import ObjectId

app = FastAPI()

# ----------------- MONGODB CONNECTION -----------------
# यहाँ नीचे दिए गए कोट्स के अंदर अपना MongoDB Atlas URL पेस्ट करें (जैसे: "mongodb+srv://...")
MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:1234512345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client["gg"]
collection = db["txtCities"]
# ------------------------------------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ए जेड - Search Engine</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 0;
            color: #333;
        }
        header {
            background-color: #1e293b;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 2px;
        }
        .container {
            max-width: 900px;
            margin: 30px auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .search-box input {
            flex: 1;
            padding: 12px 15px;
            font-size: 16px;
            border: 2px solid #cbd5e1;
            border-radius: 6px;
            outline: none;
        }
        .search-box input:focus {
            border-color: #3b82f6;
        }
        .search-box button {
            padding: 12px 25px;
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .search-box button:hover {
            background-color: #2563eb;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 20px;
        }
        .card {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }
        .card img {
            width: 100%;
            height: 160px;
            object-fit: cover;
        }
        .card-content {
            padding: 15px;
        }
        .card-content h3 {
            margin: 0 0 10px;
            font-size: 18px;
            color: #1e293b;
        }
        .card-content p {
            margin: 0;
            color: #64748b;
            font-size: 14px;
        }
        .detail-container {
            padding: 10px;
        }
        .back-btn {
            display: inline-block;
            margin-bottom: 20px;
            padding: 8px 16px;
            background-color: #64748b;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
        }
        .back-btn:hover {
            background-color: #475569;
        }
        .detail-image {
            width: 100%;
            max-height: 350px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .scrollable-info {
            max-height: 250px;
            overflow-y: auto;
            padding-right: 10px;
            line-height: 1.8;
            font-size: 16px;
        }
        .no-result {
            text-align: center;
            color: #ef4444;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <header>ए जेड</header>

    <div class="container">
        {% if detail_item %}
            <div class="detail-container">
                <a href="/" class="back-btn">&#8592; Back</a>
                <h2>{{ detail_item.name }}</h2>
                
                {% if detail_item.image_url %}
                    <img src="{{ detail_item.image_url }}" alt="Image" class="detail-image">
                {% endif %}

                <h3>City: {{ detail_item.city }}</h3>
                <h3>Sector: {{ detail_item.sector }}</h3>
                <hr>
                
                <div class="scrollable-info">
                    <p><strong>📞 Phone No:</strong> {{ detail_item.phone_no }}</p>
                    <p><strong>💰 Rent:</strong> {{ detail_item.rent if detail_item.rent else 'N/A' }}</p>
                </div>
            </div>

        {% else %}
            <form action="/search" method="POST" class="search-box">
                <input type="text" name="query" placeholder="Please search your location..." value="{{ query if query else '' }}" required>
                <button type="submit">Search</button>
            </form>

            {% if searched %}
                <h3>Search Results:</h3>
                {% if results %}
                    <div class="grid-container">
                        {% for item in results %}
                            <div class="card" onclick="window.location.href='/item/{{ item.id }}'">
                                {% if item.image_url %}
                                    <img src="{{ item.image_url }}" alt="Photo">
                                {% else %}
                                    <img src="https://res.cloudinary.com/demo/image/upload/v1652345678/sample.jpg" alt="Default">
                                {% endif %}
                                <div class="card-content">
                                    <h3>{{ item.name }}</h3>
                                    <p>📍 {{ item.sector }}, {{ item.city }}</p>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="no-result">कोई डेटा नहीं मिला! कृपया दूसरी लोकेशन सर्च करें।</p>
                {% endif %}
            {% endif %}
        {% endif %}
    </div>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    t = Template(HTML_TEMPLATE)
    return t.render(request=request, results=None, searched=False)

@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, query: str = Form(...)):
    regex_query = {"$regex": query, "$options": "i"}
    cursor = collection.find({
        "$or": [
            {"city": regex_query},
            {"sector": regex_query},
            {"name": regex_query}
        ]
    })
    
    filtered_data = []
    async for document in cursor:
        document["id"] = str(document["_id"])
        filtered_data.append(document)

    t = Template(HTML_TEMPLATE)
    return t.render(request=request, results=filtered_data, searched=True, query=query)

@app.get("/item/{item_id}", response_class=HTMLResponse)
async def item_detail(request: Request, item_id: str):
    try:
        item = await collection.find_one({"_id": ObjectId(item_id)})
        if item:
            item["id"] = str(item["_id"])
    except:
        item = None

    t = Template(HTML_TEMPLATE)
    return t.render(request=request, detail_item=item, searched=False)

