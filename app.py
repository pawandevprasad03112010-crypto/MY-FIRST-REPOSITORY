from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()

# Aapka MongoDB Connection String aur Database details
MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB"
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("search_engine_db")
collection = db.get_collection("txtCities")

# HTML Template with Search Button & Mobile Search Support
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Search Engine - FastAPI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #fff;
            color: #202124;
        }
        .search-container {
            text-align: center;
            margin-top: 15vh;
            transition: margin-top 0.3s ease;
        }
        .logo {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .logo span:nth-child(1) { color: #4285F4; }
        .logo span:nth-child(2) { color: #EA4335; }
        .logo span:nth-child(3) { color: #FBBC05; }
        .logo span:nth-child(4) { color: #4285F4; }
        .logo span:nth-child(5) { color: #34A853; }
        .logo span:nth-child(6) { color: #EA4335; }

        form {
            display: inline-flex;
            width: 100%;
            max-width: 600px;
            position: relative;
            align-items: center;
        }
        .search-box {
            width: 100%;
            padding: 12px 20px;
            padding-right: 90px;
            font-size: 16px;
            border: 1px solid #dfe1e5;
            border-radius: 24px;
            outline: none;
            box-shadow: 0 1px 6px rgba(32,33,36,.28);
            box-sizing: border-box;
        }
        .search-box:focus {
            box-shadow: 0 1px 8px rgba(32,33,36,.38);
            border-color: rgba(223,225,229,0);
        }
        .search-btn {
            position: absolute;
            right: 10px;
            background-color: #4285F4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }
        .search-btn:hover {
            background-color: #3b78e7;
        }
        .results-container {
            max-width: 700px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .result-box {
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }
        .result-content {
            flex: 1;
        }
        .result-url {
            font-size: 14px;
            color: #202124;
            margin-bottom: 4px;
        }
        .result-title a {
            font-size: 20px;
            color: #1a0dab;
            text-decoration: none;
        }
        .result-title a:hover {
            text-decoration: underline;
        }
        .result-desc {
            font-size: 14px;
            color: #4d5156;
            margin-top: 6px;
            line-height: 1.5;
        }
        .result-image img {
            width: 120px;
            height: 90px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #ddd;
        }
    </style>
</head>
<body>

    <div class="search-container" style="margin-top: {% if results %}30px{% else %}15vh{% endif %};">
        <div class="logo">
            <span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span>
        </div>
        <form method="POST" action="/">
            <!-- type="search" karne se mobile keyboard par search/magnifying glass icon aa jata hai -->
            <input type="search" class="search-box" name="search_query" value="{{ query }}" placeholder="Search cities..." required>
            <button type="submit" class="search-btn">Search</button>
        </form>
    </div>

    <div class="results-container">
        {% if results %}
            <p style="color: #70757a; font-size: 14px; margin-bottom: 20px;">Found {{ results|length }} results</p>
            {% for item in results %}
                <div class="result-box">
                    <div class="result-content">
                        <div class="result-url">{{ item.url }}</div>
                        <div class="result-title">
                            <a href="{{ item.url }}" target="_blank">{{ item.title }}</a>
                        </div>
                        <div class="result-desc">{{ item.description }}</div>
                    </div>
                    {% if item.image_url %}
                    <div class="result-image">
                        <img src="{{ item.image_url }}" alt="Image">
                    </div>
                    {% endif %}
                </div>
            {% endfor %}
        {% elif query %}
            <p style="text-align: center; color: #70757a; margin-top: 40px;">No results found for "<b>{{ query }}</b>"</p>
        {% endif %}
    </div>

</body>
</html>
"""

from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
async def home():
    t = Template(HTML_TEMPLATE)
    return t.render(query="", results=[])

@app.post("/", response_class=HTMLResponse)
async def search(search_query: str = Form(...)):
    query = search_query.strip()
    results = []
    if query:
        cursor = collection.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        })
        results = await cursor.to_list(length=100)
        
    t = Template(HTML_TEMPLATE)
    return t.render(query=query, results=results)
