from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from typing import Optional
import cloudinary
import cloudinary.uploader

app = FastAPI(title="MongoDB & Cloudinary Search Engine Backend")

# =========================================================================
# Cloudinary Configuration (अपनी डिटेल्स यहाँ चेक कर लें)
# =========================================================================
cloudinary.config(
    cloud_name="apka_cloud_name",
    api_key="apka_api_key",
    api_secret="apka_api_secret"
)

# =========================================================================
# MongoDB Atlas कनेक्शन
# =========================================================================
MONGO_URI = "mongodb://pawandevprasad03112010_db_user:12345@ac-j92zzlx-shard-00-00.p45qsrf.mongodb.net:27017,ac-j92zzlx-shard-00-01.p45qsrf.mongodb.net:27017,ac-j92zzlx-shard-00-02.p45qsrf.mongodb.net:27017/?ssl=true&replicaSet=atlas-rahm0d-shard-0&authSource=admin&appName=FIRSTMONGODB"

try:
    client = MongoClient(MONGO_URI)
    db = client["gg"]               
    collection = db["txtCities"]     
    print("Database se connection safal ho gaya hai!")
except Exception as e:
    print(f"MongoDB connection error: {e}")


# 1. होम रूट - ब्राउज़र में डेटा और फोटो एक साथ दिखाने के लिए (HTML UI)
@app.get("/", response_class=HTMLResponse)
def home():
    try:
        # मोंगोडीबी से सारा डेटा निकालना
        all_data = list(collection.find({}, {"_id": 0}))
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MongoDB Data & Images</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f4f9; }
                .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                img { max-width: 300px; border-radius: 6px; margin-top: 10px; display: block; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>MongoDB Cities Data & Photos</h1>
        """
        
        if not all_data:
            html_content += "<p>Database mein abhi koi data nahi hai.</p>"
        else:
            for item in all_data:
                html_content += "<div class='card'>"
                # डेटाबेस के हर फील्ड को लूप के जरिए दिखाना
                for key, value in item.items():
                    # अगर फील्ड का नाम image_url है, तो उसे फोटो की तरह दिखाना
                    if key == "image_url" and value:
                        html_content += f"<p><strong>{key}:</strong> <a href='{value}' target='_blank'>{value}</a></p>"
                        html_content += f"<img src='{value}' alt='City Image'>"
                    else:
                        html_content += f"<p><strong>{key}:</strong> {value}</p>"
                html_content += "</div>"
                
        html_content += "</body></html>"
        return html_content
        
    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"


# 2. नया डेटा और फोटो एक साथ अपलोड करने का API
@app.post("/api/upload")
async def upload_image(info_text: str = Query(..., description="Information text"), file: UploadFile = File(...)):
    try:
        upload_result = cloudinary.uploader.upload(file.file)
        image_url = upload_result.get("secure_url")
        
        document = {
            "info_text": info_text,
            "image_url": image_url
        }
        
        collection.insert_one(document)
        
        return {
            "message": "Data aur photo safaltapoorvak save ho gaye!",
            "image_url": image_url,
            "data": document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 3. सारा डेटा JSON फॉर्मेट में देखने के लिए
@app.get("/api/view-all")
def view_all_data():
    try:
        all_data = list(collection.find({}, {"_id": 0}))
        return {
            "total_documents": len(all_data),
            "data": all_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# 4. सर्च API
@app.get("/api/search")
def search_database(query: Optional[str] = Query(None, description="Search input")):
    try:
        if not query or query.strip() == "":
            return {"query": "", "total_results": 0, "results": []}
        
        search_filter = {"$or": [
            {"info_text": {"$regex": query, "$options": "i"}},
            {"city_name": {"$regex": query, "$options": "i"}}
        ]}
        results = list(collection.find(search_filter, {"_id": 0}))
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
        
