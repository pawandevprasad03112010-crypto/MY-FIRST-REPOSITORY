from jinja2 import Template
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB"
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("gg")
collection = db.get_collection("txtCities")

# Home & Search Template
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Engine - txtCities</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #fff; color: #202124; }
        .search-container { text-align: center; margin-top: {% if results %}30px{% else %}15vh{% endif %}; transition: margin-top 0.3s ease; }
        .logo { font-size: 48px; font-weight: bold; margin-bottom: 20px; }
        .logo span:nth-child(1) { color: #4285F4; }
        .logo span:nth-child(2) { color: #EA4335; }
        .logo span:nth-child(3) { color: #FBBC05; }
        .logo span:nth-child(4) { color: #4285F4; }
        .logo span:nth-child(5) { color: #34A853; }
        .logo span:nth-child(6) { color: #EA4335; }
        form { display: inline-flex; width: 100%; max-width: 600px; position: relative; align-items: center; }
        .search-box { width: 100%; padding: 12px 20px; padding-right: 90px; font-size: 16px; border: 1px solid #dfe1e5; border-radius: 24px; outline: none; box-shadow: 0 1px 6px rgba(32,33,36,.28); box-sizing: border-box; }
        .search-btn { position: absolute; right: 10px; background-color: #4285F4; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px; }
        .results-container { max-width: 700px; margin: 30px auto; padding: 0 20px; }
        .result-box { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); display: flex; gap: 20px; align-items: flex-start; }
        .result-content { flex: 1; }
        .result-title a { font-size: 20px; color: #1a0dab; font-weight: bold; text-decoration: none; }
        .result-title a:hover { text-decoration: underline; }
        .result-desc { font-size: 14px; color: #4d5156; margin-top: 4px; line-height: 1.5; }
        .result-image img { width: 120px; height: 90px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="search-container">
        <div class="logo">
            <span>C</span><span>i</span><span>t</span><span>i</span><span>e</span><span>s</span>
        </div>
        <form method="POST" action="/">
            <input type="search" class="search-box" name="search_query" value="{{ query }}" placeholder="Search city, name, sector..." required>
            <button type="submit" class="search-btn">Search</button>
        </form>
    </div>

    <div class="results-container">
        {% if results %}
            <p style="color: #70757a; font-size: 14px; margin-bottom: 20px;">Found {{ results|length }} results</p>
            {% for item in results %}
                <div class="result-box">
                    <div class="result-content">
                        <div class="result-title">
                            <a href="/details/{{ item._id }}">{{ item.name }}</a>
                        </div>
                        <div class="result-desc">
                        
