from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI(title="PG Finder API", version="1.0")

# CORS सक्षम करें ताकि फ्रंटएंड इसे आसानी से एक्सेस कर सके
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

# यहाँ डेटाबेस का नाम 'gg' और प्रॉपर्टी कलेक्शन का नाम 'txtCities' सेट किया गया है
database = client.gg
users_collection = database.get_collection("users")
properties_collection = database.get_collection("txtCities")

# --- Pydantic मॉडल्स (Data Validation के लिए) ---

class UserLogin(BaseModel):
    name: str
    password: str

class PropertyModel(BaseModel):
    title: str
    location: str
    price: int
    sharing_type: str
    meals: str
    total_beds: int
    notice_period: str
    power_backup: str
    parking: str
    images: list[str]

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Welcome to PG Finder API running with FastAPI and MongoDB!"}

# 1. लॉगिन एंडपॉइंट (Login API)
@app.post("/api/login")
async def login(user: UserLogin):
    existing_user = await users_collection.find_one({"name": user.name})
    
    if existing_user:
        if existing_user["password"] == user.password:
            return {"status": "success", "message": "Login successful", "name": user.name}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        new_user = {"name": user.name, "password": user.password}
        await users_collection.insert_one(new_user)
        return {"status": "success", "message": "User registered and logged in successfully", "name": user.name}

# 2. सर्च या प्रॉपर्टी डेटा प्राप्त करने का एंडपॉइंट (Search/Fetch Properties API)
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
    
    # यदि डेटाबेस में डेटा नहीं मिला, तो डिफ़ॉल्ट डमी डेटा दिखाएं
    if not properties and not locality:
        default_property = {
            "id": "sample_id_123",
            "title": "Shri Laxmi Narayan boys",
            "location": "Argora, Ranchi",
            "price": 4000,
            "sharing_type": "Triple Sharing, Double Sharing, Private Room",
            "meals": "Breakfast, Lunch, Dinner",
            "total_beds": 24,
            "notice_period": "30 Days",
            "power_backup": "Inverter (No A/C Support)",
            "parking": "Two Wheeler parking",
            "images": ["hall1.jpg", "hall2.jpg"]
        }
        properties.append(default_property)
        
    return {"status": "success", "data": properties}

# 3. प्रॉपर्टी डिटेल पाने का एंडपॉइंट (Property Detail API)
@app.get("/api/properties/{property_id}")
async def get_property_detail(property_id: str):
    if property_id == "sample_id_123":
        return {
            "status": "success",
            "data": {
                "id": "sample_id_123",
                "title": "Shri Laxmi Narayan boys",
                "subtitle": "Triple Sharing , Double Sharing , Private Room",
                "for_gender": "BOYS",
                "price": 4000,
                "price_onwards": "Onwards",
                "location": "Argora, Ranchi",
                "managed_by": "Property Managed by Owner",
                "meal_types": "Breakfast,Lunch,Dinner",
                "total_beds": 24,
                "notice_period": "30 Days",
                "power_backup": "Inverter (No A/C Support)",
                "parking": "Two Wheeler parking",
                "furnishing": ["Fridge", "Washing Machine", "Microwave"],
                "amenities": ["CCTV", "24 Hrs Security", "TT Table"],
                "images": ["image1.jpg", "image2.jpg"]
            }
        }
    
    try:
        prop = await properties_collection.find_one({"_id": ObjectId(property_id)})
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")
        prop["id"] = str(prop["_id"])
        del prop["_id"]
        return {"status": "success", "data": prop}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Property ID format")
        
