from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

app = FastAPI(title="PG Finder App", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MongoDB कनेक्शन ---
MONGO_DETAILS = "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.gg
users_collection = database.get_collection("users")
properties_collection = database.get_collection("txtCities")

# --- HTML पेज दिखाने के लिए रूट ---
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    # यह 'templates/index.html' फाइल को सीधे ब्राउज़र में खोल देगा
    html_path = os.path.join("templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found in templates folder!</h1>"

# --- बाक़ी API एंडपॉइंट्स ---

@app.post("/api/login")
async def login(user: BaseModel): # (या आपका पुराना UserLogin मॉडल)
    pass # (आपका लॉगिन वाला कोड यहाँ रहेगा)

@app.get("/api/properties")
async def get_properties(locality: str = None):
    query = {}
    if locality:
        query["location"] = {"$regex": locality, "$options": "i"}
    
    properties = []
    async for prop in properties_collection.find(query):
        prop["id"] = str(prop["_id"])
        del prop["_id"]
        properties.append(prop)
    
    if not properties and not locality:
        properties.append({
            "id": "sample_id_123",
            "title": "Shri Laxmi Narayan boys",
            "location": "Argora, Ranchi",
            "price": 4000,
            "meal_types": "Breakfast, Lunch, Dinner",
            "total_beds": 24,
            "notice_period": "30 Days",
            "power_backup": "Inverter",
            "parking": "Two Wheeler parking"
        })
    return {"status": "success", "data": properties}

@app.get("/api/properties/{property_id}")
async def get_property_detail(property_id: str):
    if property_id == "sample_id_123":
        return {
            "status": "success",
            "data": {
                "id": "sample_id_123",
                "title": "Shri Laxmi Narayan boys",
                "price": 4000,
                "location": "Argora, Ranchi",
                "meal_types": "Breakfast, Lunch, Dinner",
                "total_beds": 24,
                "notice_period": "30 Days",
                "power_backup": "Inverter",
            }
        }
    try:
        prop = await properties_collection.find_one({"_id": ObjectId(property_id)})
        if not prop:
            raise HTTPException(status_code=404, detail="Not found")
        prop["id"] = str(prop["_id"])
        del prop["_id"]
        return {"status": "success", "data": prop}
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
            
